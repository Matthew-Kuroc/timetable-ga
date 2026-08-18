from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from backend.app.core.config import get_settings
from backend.app.core.security import (
    create_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from backend.app.db.models import AccountAuditModel, AppUserModel, AuthSessionModel
from backend.app.db.session import get_session_local


@dataclass(frozen=True)
class SessionGrant:
    token: str
    expires_at: datetime
    user: AppUserModel


_DUMMY_PASSWORD_HASH = hash_password("invalid-account-password")


def authenticate(username: str, password: str) -> SessionGrant | None:
    normalized_username = normalize_username(username)
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        user = session.scalar(
            select(AppUserModel).where(AppUserModel.username == normalized_username)
        )
        password_matches = verify_password(
            password,
            user.password_hash if user is not None else _DUMMY_PASSWORD_HASH,
        )
        if user is None or not password_matches or not user.active:
            session.add(
                AccountAuditModel(
                    actor_user_id=None,
                    target_user_id=user.id if user is not None else None,
                    actor_username=None,
                    target_username=normalized_username,
                    action="LOGIN_FAILED",
                    new_value={
                        "reason": "INACTIVE_ACCOUNT"
                        if user is not None and password_matches and not user.active
                        else "INVALID_CREDENTIALS"
                    },
                    created_at=now,
                )
            )
            session.commit()
            return None

        token = create_session_token()
        expires_at = now + timedelta(minutes=get_settings().auth_session_ttl_minutes)
        session.add(
            AuthSessionModel(
                user_id=user.id,
                token_hash=hash_session_token(token),
                expires_at=expires_at,
                created_at=now,
            )
        )
        user.last_login_at = now
        session.add(
            AccountAuditModel(
                actor_user_id=user.id,
                target_user_id=user.id,
                actor_username=user.username,
                target_username=user.username,
                action="LOGIN_SUCCESS",
                new_value={"expires_at": expires_at.isoformat()},
                created_at=now,
            )
        )
        session.commit()
        return SessionGrant(token=token, expires_at=expires_at, user=user)


def user_from_session_token(token: str) -> AppUserModel | None:
    if not token:
        return None
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        auth_session = session.scalar(
            select(AuthSessionModel).where(
                AuthSessionModel.token_hash == hash_session_token(token)
            )
        )
        if auth_session is None or auth_session.revoked_at is not None:
            return None
        if _as_utc(auth_session.expires_at) <= now:
            auth_session.revoked_at = now
            session.commit()
            return None
        user = session.get(AppUserModel, auth_session.user_id)
        if user is None or not user.active:
            return None
        return user


def revoke_session(token: str) -> None:
    if not token:
        return
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        auth_session = session.scalar(
            select(AuthSessionModel).where(
                AuthSessionModel.token_hash == hash_session_token(token)
            )
        )
        if auth_session is None or auth_session.revoked_at is not None:
            return
        user = session.get(AppUserModel, auth_session.user_id)
        auth_session.revoked_at = now
        session.add(
            AccountAuditModel(
                actor_user_id=user.id if user is not None else None,
                target_user_id=user.id if user is not None else None,
                actor_username=user.username if user is not None else None,
                target_username=user.username if user is not None else None,
                action="LOGOUT",
                created_at=now,
            )
        )
        session.commit()


def revoke_all_user_sessions(user_id: int) -> None:
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        active_sessions = session.scalars(
            select(AuthSessionModel).where(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
            )
        ).all()
        for auth_session in active_sessions:
            auth_session.revoked_at = now
        session.commit()


def normalize_username(username: str) -> str:
    return username.strip().lower()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
