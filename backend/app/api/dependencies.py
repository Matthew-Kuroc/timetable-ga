from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from backend.app.db.models import AppUserModel
from backend.app.domain.auth import UserRole
from backend.app.services.auth_service import user_from_session_token


AUTH_COOKIE_NAME = "timetable_session"


def extract_session_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "").strip()
    if authorization:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() != "bearer" or not credentials.strip():
            return None
        return credentials.strip()
    return request.cookies.get(AUTH_COOKIE_NAME)


def get_current_user(request: Request) -> AppUserModel:
    user = user_from_session_token(extract_session_token(request) or "")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: UserRole) -> Callable[..., AppUserModel]:
    allowed_roles = {role.value for role in roles}

    def dependency(
        current_user: Annotated[AppUserModel, Depends(get_current_user)],
    ) -> AppUserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện thao tác này.",
            )
        if current_user.must_change_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản phải đổi mật khẩu trước khi sử dụng chức năng này.",
            )
        return current_user

    return dependency
