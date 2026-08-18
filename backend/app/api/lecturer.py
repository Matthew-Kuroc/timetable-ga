from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.dependencies import require_roles
from backend.app.db.models import AppUserModel
from backend.app.domain.auth import UserRole
from backend.app.services.lecturer_service import assigned_course_sections, personal_timetable


LecturerUser = Annotated[AppUserModel, Depends(require_roles(UserRole.LECTURER))]

router = APIRouter(prefix="/api/lecturer", tags=["lecturer"])


@router.get("/timetable")
def get_personal_timetable(
    current_user: LecturerUser,
    week: int = Query(ge=1, le=53),
) -> dict[str, Any]:
    return personal_timetable(_lecturer_code(current_user), week)


@router.get("/course-sections")
def get_assigned_course_sections(current_user: LecturerUser) -> dict[str, Any]:
    return assigned_course_sections(_lecturer_code(current_user))


def _lecturer_code(user: AppUserModel) -> str:
    if not user.lecturer_code:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản giảng viên chưa được gắn mã giảng viên.",
        )
    return user.lecturer_code
