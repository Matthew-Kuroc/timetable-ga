from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from backend.app.core.security import hash_password, validate_password, verify_password
from backend.app.db.models import AccountAuditModel, AppUserModel, AuthSessionModel
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.app.services.auth_service import normalize_username
from backend.app.services.runtime_store import list_confirmed_lecturers


class AccountConflictError(ValueError):
    pass


class AccountNotFoundError(LookupError):
    pass


class AccountValidationError(ValueError):
    pass


LEGACY_PASSWORD_SENTINEL = "!legacy-account-without-password!"


def _temporary_password() -> str:
    import secrets
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(20))


def create_user(
    *,
    username: str,
    display_name: str,
    password: str,
    role: UserRole,
    lecturer_code: str | None,
    actor: AppUserModel,
) -> AppUserModel:
    normalized_username = normalize_username(username)
    normalized_lecturer_code = _validate_account_values(
        normalized_username,
        display_name,
        role,
        lecturer_code,
    )
    display_name = _lecturer_display_name(normalized_lecturer_code, display_name, role)
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        _ensure_singleton_role(session, role)
        _ensure_unique_values(session, normalized_username, normalized_lecturer_code)
        user = AppUserModel(
            username=normalized_username,
            display_name=display_name.strip(),
            password_hash=_validated_password_hash(password),
            must_change_password=True,
            role=role.value,
            active=True,
            lecturer_code=normalized_lecturer_code,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        try:
            session.flush()
            session.add(
                _audit(
                    actor=actor,
                    target=user,
                    action="USER_CREATED",
                    old_value=None,
                    new_value=user_snapshot(user),
                    now=now,
                )
            )
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise AccountConflictError("Tên đăng nhập hoặc mã giảng viên đã được sử dụng.") from error
        return user


def update_user(
    user_id: int,
    changes: dict[str, Any],
    *,
    actor: AppUserModel,
) -> AppUserModel:
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        user = session.get(AppUserModel, user_id)
        if user is None:
            raise AccountNotFoundError("Không tìm thấy tài khoản.")
        if user.system_account:
            raise AccountValidationError("Tài khoản quản trị hệ thống được cố định và không thể chỉnh sửa tại đây.")
        old_value = user_snapshot(user)

        username = normalize_username(str(changes.get("username", user.username)))
        display_name = str(changes.get("display_name", user.display_name)).strip()
        try:
            role = UserRole(str(changes.get("role", user.role)))
        except ValueError as error:
            raise AccountValidationError("Vai trò tài khoản không hợp lệ.") from error
        lecturer_code_value = changes.get("lecturer_code", user.lecturer_code)
        if role is not UserRole.LECTURER:
            if "lecturer_code" in changes and lecturer_code_value:
                raise AccountValidationError("Chỉ tài khoản giảng viên mới được gắn mã giảng viên.")
            lecturer_code_value = None
        lecturer_code = _validate_account_values(
            username,
            display_name,
            role,
            str(lecturer_code_value) if lecturer_code_value is not None else None,
        )
        display_name = _lecturer_display_name(lecturer_code, display_name, role)
        _ensure_unique_values(
            session,
            username,
            lecturer_code,
            excluded_user_id=user.id,
        )
        _ensure_singleton_role(session, role, excluded_user_id=user.id)

        user.username = username
        user.display_name = display_name
        user.role = role.value
        user.lecturer_code = lecturer_code
        if "active" in changes:
            user.active = bool(changes["active"])
        password_changed = "password" in changes and changes["password"] is not None
        if password_changed:
            user.password_hash = _validated_password_hash(str(changes["password"]))
            user.must_change_password = True
        user.updated_at = now

        try:
            session.flush()
            new_value = user_snapshot(user)
            if password_changed:
                new_value["password_changed"] = True
            session.add(
                _audit(
                    actor=actor,
                    target=user,
                    action="USER_UPDATED",
                    old_value=old_value,
                    new_value=new_value,
                    now=now,
                )
            )
            if not user.active or password_changed or old_value["role"] != user.role:
                active_sessions = session.scalars(
                    select(AuthSessionModel).where(
                        AuthSessionModel.user_id == user.id,
                        AuthSessionModel.revoked_at.is_(None),
                    )
                ).all()
                for auth_session in active_sessions:
                    auth_session.revoked_at = now
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise AccountConflictError("Tên đăng nhập hoặc mã giảng viên đã được sử dụng.") from error
        return user


def list_users(
    *,
    query: str = "",
    role: UserRole | None = None,
    active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AppUserModel], int]:
    filters = []
    normalized_query = query.strip().lower()
    if normalized_query:
        pattern = f"%{normalized_query}%"
        filters.append(
            or_(
                func.lower(AppUserModel.username).like(pattern),
                func.lower(AppUserModel.display_name).like(pattern),
            )
        )
    if role is not None:
        filters.append(AppUserModel.role == role.value)
    if active is not None:
        filters.append(AppUserModel.active.is_(active))

    with get_session_local()() as session:
        total = session.scalar(
            select(func.count()).select_from(AppUserModel).where(*filters)
        ) or 0
        users = session.scalars(
            select(AppUserModel)
            .where(*filters)
            .order_by(AppUserModel.username)
            .offset(offset)
            .limit(limit)
        ).all()
        return list(users), int(total)


def list_audit_logs(*, limit: int = 100, offset: int = 0) -> tuple[list[AccountAuditModel], int]:
    with get_session_local()() as session:
        total = session.scalar(select(func.count()).select_from(AccountAuditModel)) or 0
        logs = session.scalars(
            select(AccountAuditModel)
            .order_by(AccountAuditModel.created_at.desc(), AccountAuditModel.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return list(logs), int(total)


def bootstrap_admin(*, username: str, display_name: str, password: str) -> AppUserModel:
    normalized_username = normalize_username(username)
    _validate_account_values(
        normalized_username,
        display_name,
        UserRole.ADMIN,
        None,
    )
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        active_admin = session.scalar(
            select(AppUserModel.id)
            .where(
                AppUserModel.role == UserRole.ADMIN.value,
                AppUserModel.active.is_(True),
            )
            .limit(1)
        )
        if active_admin is not None:
            raise AccountConflictError("Hệ thống đã có tài khoản quản trị viên.")
        legacy_admin = session.scalar(
            select(AppUserModel).where(AppUserModel.username == normalized_username)
        )
        if legacy_admin is not None:
            if (
                legacy_admin.role != UserRole.ADMIN.value
                or legacy_admin.active
                or legacy_admin.password_hash != LEGACY_PASSWORD_SENTINEL
            ):
                raise AccountConflictError("Tên đăng nhập đã được sử dụng.")
            old_value = user_snapshot(legacy_admin)
            legacy_admin.display_name = display_name.strip()
            legacy_admin.password_hash = _validated_password_hash(password)
            legacy_admin.active = True
            legacy_admin.system_account = True
            legacy_admin.updated_at = now
            session.add(
                AccountAuditModel(
                    target_user_id=legacy_admin.id,
                    target_username=legacy_admin.username,
                    action="ADMIN_RECOVERED",
                    old_value=old_value,
                    new_value=user_snapshot(legacy_admin),
                    created_at=now,
                )
            )
            session.commit()
            return legacy_admin
        _ensure_unique_values(session, normalized_username, None)
        user = AppUserModel(
            username=normalized_username,
            display_name=display_name.strip(),
            password_hash=_validated_password_hash(password),
            role=UserRole.ADMIN.value,
            active=True,
            system_account=True,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        try:
            session.flush()
            session.add(
                AccountAuditModel(
                    target_user_id=user.id,
                    target_username=user.username,
                    action="ADMIN_BOOTSTRAPPED",
                    new_value=user_snapshot(user),
                    created_at=now,
                )
            )
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise AccountConflictError("Tên đăng nhập đã được sử dụng.") from error
        return user


def user_snapshot(user: AppUserModel) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "active": user.active,
        "system_account": user.system_account,
        "lecturer_code": user.lecturer_code,
        "must_change_password": bool(user.must_change_password),
    }


def _validate_account_values(
    username: str,
    display_name: str,
    role: UserRole,
    lecturer_code: str | None,
) -> str | None:
    if not username:
        raise AccountValidationError("Tên đăng nhập không được để trống.")
    if not display_name.strip():
        raise AccountValidationError("Tên hiển thị không được để trống.")
    normalized_lecturer_code = lecturer_code.strip() if lecturer_code else None
    if role is UserRole.LECTURER and not normalized_lecturer_code:
        raise AccountValidationError("Tài khoản giảng viên phải gắn với mã giảng viên.")
    if role is UserRole.LECTURER and normalized_lecturer_code:
        catalog = list_confirmed_lecturers()
        available_codes = {
            str(item["lecturer_code"])
            for item in catalog.get("lecturers", [])
            if isinstance(item, dict) and item.get("lecturer_code")
        }
        if available_codes and normalized_lecturer_code not in available_codes:
            raise AccountValidationError(
                f"Mã giảng viên {normalized_lecturer_code} không tồn tại trong bộ dữ liệu đã xác nhận."
            )
    if role is not UserRole.LECTURER and normalized_lecturer_code:
        raise AccountValidationError("Chỉ tài khoản giảng viên mới được gắn mã giảng viên.")
    return normalized_lecturer_code


def _lecturer_display_name(lecturer_code: str | None, display_name: str, role: UserRole) -> str:
    """Use the confirmed CSV master name for lecturer accounts when available."""
    cleaned = display_name.strip()
    if role is not UserRole.LECTURER or not lecturer_code:
        return cleaned
    catalog = list_confirmed_lecturers()
    for lecturer in catalog.get("lecturers", []):
        if str(lecturer.get("lecturer_code") or "") == lecturer_code:
            return str(lecturer.get("lecturer_name") or cleaned).strip()
    return cleaned


def _ensure_unique_values(
    session: Any,
    username: str,
    lecturer_code: str | None,
    *,
    excluded_user_id: int | None = None,
) -> None:
    username_query = select(AppUserModel.id).where(AppUserModel.username == username)
    if excluded_user_id is not None:
        username_query = username_query.where(AppUserModel.id != excluded_user_id)
    if session.scalar(username_query) is not None:
        raise AccountConflictError("Tên đăng nhập đã được sử dụng.")
    if lecturer_code is None:
        return
    lecturer_query = select(AppUserModel.id).where(AppUserModel.lecturer_code == lecturer_code)
    if excluded_user_id is not None:
        lecturer_query = lecturer_query.where(AppUserModel.id != excluded_user_id)
    if session.scalar(lecturer_query) is not None:
        raise AccountConflictError("Mã giảng viên đã được gắn với tài khoản khác.")


def _ensure_singleton_role(session: Any, role: UserRole, *, excluded_user_id: int | None = None) -> None:
    if role not in {UserRole.ADMIN, UserRole.TRAINING_OFFICE}:
        return
    query = select(func.count(AppUserModel.id)).where(AppUserModel.role == role.value)
    if excluded_user_id is not None:
        query = query.where(AppUserModel.id != excluded_user_id)
    if int(session.scalar(query) or 0) >= 1:
        label = "ADMIN" if role is UserRole.ADMIN else "Phòng Đào tạo"
        raise AccountConflictError(f"Hệ thống chỉ cho phép một tài khoản {label}.")


def _audit(
    *,
    actor: AppUserModel,
    target: AppUserModel,
    action: str,
    old_value: dict[str, Any] | None,
    new_value: dict[str, Any] | None,
    now: datetime,
) -> AccountAuditModel:
    return AccountAuditModel(
        actor_user_id=actor.id,
        target_user_id=target.id,
        actor_username=actor.username,
        target_username=target.username,
        action=action,
        old_value=old_value,
        new_value=new_value,
        created_at=now,
    )


def _validated_password_hash(password: str) -> str:
    try:
        validate_password(password)
    except ValueError as error:
        raise AccountValidationError(str(error)) from error
    return hash_password(password)


def change_own_password(*, user_id: int, current_password: str, new_password: str) -> None:
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        user = session.get(AppUserModel, user_id)
        if user is None or not verify_password(current_password, user.password_hash):
            raise AccountValidationError("Mật khẩu hiện tại không đúng.")
        new_hash = _validated_password_hash(new_password)
        if verify_password(current_password, new_hash):
            raise AccountValidationError("Mật khẩu mới phải khác mật khẩu hiện tại.")
        user.password_hash = new_hash
        user.must_change_password = False
        user.updated_at = now
        sessions = session.scalars(
            select(AuthSessionModel).where(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
            )
        ).all()
        for auth_session in sessions:
            auth_session.revoked_at = now
        session.add(
            AccountAuditModel(
                actor_user_id=user.id,
                target_user_id=user.id,
                actor_username=user.username,
                target_username=user.username,
                action="PASSWORD_CHANGED",
                new_value={"must_change_password": False},
                created_at=now,
            )
        )
        session.commit()


def provision_lecturer_accounts(
    *,
    actor: AppUserModel,
    lecturer_codes: list[str] | None = None,
    all_lecturers: bool = False,
) -> dict[str, Any]:
    catalog = list_confirmed_lecturers()
    available = {
        str(item["lecturer_code"]): str(item.get("lecturer_name") or item["lecturer_code"])
        for item in catalog.get("lecturers", [])
        if isinstance(item, dict) and item.get("lecturer_code")
    }
    requested = set(available) if all_lecturers else {str(item).strip() for item in (lecturer_codes or []) if str(item).strip()}
    unknown = sorted(requested - set(available))
    if unknown:
        raise AccountValidationError(f"Không tìm thấy mã giảng viên trong batch đã xác nhận: {', '.join(unknown)}.")
    created: list[dict[str, str]] = []
    skipped: list[str] = []
    conflicts: list[dict[str, str]] = []
    with get_session_local()() as session:
        for code in sorted(requested):
            existing = session.scalar(select(AppUserModel).where(AppUserModel.lecturer_code == code))
            if existing is not None:
                skipped.append(code)
                continue
            username = normalize_username(code)
            if session.scalar(select(AppUserModel.id).where(AppUserModel.username == username)) is not None:
                conflicts.append({"lecturer_code": code, "reason": f"Tên đăng nhập {username} đã được sử dụng."})
                continue
            password = _temporary_password()
            user = AppUserModel(
                username=username,
                display_name=available[code],
                password_hash=hash_password(password),
                must_change_password=True,
                role=UserRole.LECTURER.value,
                active=True,
                lecturer_code=code,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(user)
            session.flush()
            session.add(_audit(actor=actor, target=user, action="LECTURER_PROVISIONED", old_value=None, new_value=user_snapshot(user), now=datetime.now(timezone.utc)))
            created.append({"lecturer_code": code, "username": username, "temporary_password": password})
        session.commit()
    return {"batch_code": catalog.get("batch_code"), "created": created, "skipped": skipped, "conflicts": conflicts}


def reset_lecturer_password(*, actor: AppUserModel, user_id: int) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        user = session.get(AppUserModel, user_id)
        if user is None:
            raise AccountNotFoundError("Không tìm thấy tài khoản.")
        if user.role != UserRole.LECTURER.value or not user.lecturer_code:
            raise AccountValidationError("Chỉ có thể cấp lại mật khẩu cho tài khoản Giảng viên.")
        password = _temporary_password()
        old_value = user_snapshot(user)
        user.password_hash = hash_password(password)
        user.must_change_password = True
        user.updated_at = now
        sessions = session.scalars(select(AuthSessionModel).where(AuthSessionModel.user_id == user.id, AuthSessionModel.revoked_at.is_(None))).all()
        for auth_session in sessions:
            auth_session.revoked_at = now
        session.add(_audit(actor=actor, target=user, action="PASSWORD_RESET_BY_ADMIN", old_value=old_value, new_value={"must_change_password": True}, now=now))
        session.commit()
        return {"user": user_snapshot(user), "temporary_password": password}
