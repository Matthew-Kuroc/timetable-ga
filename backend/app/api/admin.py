from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.api.auth import user_payload
from backend.app.api.dependencies import require_roles
from backend.app.db.models import AppUserModel
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.app.services.user_service import (
    AccountConflictError,
    AccountNotFoundError,
    AccountValidationError,
    create_user,
    list_audit_logs,
    list_users,
    update_user,
)
from backend.app.services.runtime_store import list_confirmed_lecturers


AdminUser = Annotated[AppUserModel, Depends(require_roles(UserRole.ADMIN))]

router = APIRouter(prefix="/api/admin", tags=["admin"])


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    display_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=256)
    role: UserRole
    lecturer_code: str | None = Field(default=None, max_length=50)


class UpdateUserRequest(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=80)
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=256)
    role: UserRole | None = None
    active: bool | None = None
    lecturer_code: str | None = Field(default=None, max_length=50)


@router.get("/users")
def get_users(
    _admin: AdminUser,
    q: str = Query(default="", max_length=255),
    role: UserRole | None = None,
    active: bool | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    users, total = list_users(
        query=q,
        role=role,
        active=active,
        limit=limit,
        offset=offset,
    )
    return {
        "users": [user_payload(user, include_timestamps=True) for user in users],
        "total": total,
    }


@router.get("/lecturers")
def get_lecturers(_admin: AdminUser) -> dict[str, Any]:
    """List valid lecturer identifiers for account provisioning."""
    result = list_confirmed_lecturers()
    with get_session_local()() as session:
        accounts = {
            user.lecturer_code: user
            for user in session.query(AppUserModel).filter(
                AppUserModel.role == UserRole.LECTURER.value,
                AppUserModel.lecturer_code.is_not(None),
            )
        }
    for lecturer in result.get("lecturers", []):
        account = accounts.get(lecturer.get("lecturer_code"))
        lecturer["account_username"] = account.username if account else None
        lecturer["account_active"] = account.active if account else None
    return result


@router.post("/users", status_code=status.HTTP_201_CREATED)
def post_user(request: CreateUserRequest, admin: AdminUser) -> dict[str, Any]:
    try:
        user = create_user(
            username=request.username,
            display_name=request.display_name,
            password=request.password,
            role=request.role,
            lecturer_code=request.lecturer_code,
            actor=admin,
        )
    except AccountConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except AccountValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"user": user_payload(user, include_timestamps=True)}


@router.patch("/users/{user_id}")
def patch_user(
    user_id: int,
    request: UpdateUserRequest,
    admin: AdminUser,
) -> dict[str, Any]:
    changes = request.model_dump(exclude_unset=True, mode="json")
    if not changes:
        raise HTTPException(status_code=422, detail="Không có thông tin tài khoản cần cập nhật.")
    required_when_supplied = ("username", "display_name", "password", "role", "active")
    if any(field in changes and changes[field] is None for field in required_when_supplied):
        raise HTTPException(status_code=422, detail="Trường cập nhật tài khoản không được để trống.")
    try:
        user = update_user(user_id, changes, actor=admin)
    except AccountNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except AccountConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except AccountValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"user": user_payload(user, include_timestamps=True)}


@router.get("/audit-logs")
def get_audit_logs(
    _admin: AdminUser,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    logs, total = list_audit_logs(limit=limit, offset=offset)
    return {
        "audit_logs": [
            {
                "id": item.id,
                "actor_user_id": item.actor_user_id,
                "target_user_id": item.target_user_id,
                "actor_username": item.actor_username,
                "target_username": item.target_username,
                "action": item.action,
                "old_value": item.old_value,
                "new_value": item.new_value,
                "created_at": item.created_at.isoformat(),
            }
            for item in logs
        ],
        "total": total,
    }
