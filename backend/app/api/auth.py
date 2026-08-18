from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from backend.app.api.dependencies import (
    AUTH_COOKIE_NAME,
    extract_session_token,
    get_current_user,
)
from backend.app.core.config import get_settings
from backend.app.db.models import AppUserModel
from backend.app.services.auth_service import authenticate, revoke_session


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)


@router.post("/login")
def login(request: LoginRequest, response: Response) -> dict[str, Any]:
    grant = authenticate(request.username, request.password)
    if grant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=grant.token,
        max_age=settings.auth_session_ttl_minutes * 60,
        expires=grant.expires_at,
        path="/",
        secure=settings.auth_cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return {
        "user": user_payload(grant.user),
        "expires_at": grant.expires_at.isoformat(),
    }


@router.get("/me")
def me(
    current_user: Annotated[AppUserModel, Depends(get_current_user)],
) -> dict[str, Any]:
    return {"user": user_payload(current_user)}


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
) -> dict[str, str]:
    revoke_session(extract_session_token(request) or "")
    settings = get_settings()
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        secure=settings.auth_cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return {"message": "Đã đăng xuất."}


def user_payload(user: AppUserModel, *, include_timestamps: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "active": user.active,
        "lecturer_code": user.lecturer_code,
    }
    if include_timestamps:
        payload.update(
            {
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            }
        )
    return payload
