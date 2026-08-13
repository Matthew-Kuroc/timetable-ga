from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Callable, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from backend.app.api.dependencies import require_roles
from backend.app.db.models import AppUserModel
from backend.app.domain.auth import UserRole
from backend.app.domain.change_requests import (
    ScheduleChangeRequestStatus,
    ScheduleChangeRequestType,
)
from backend.app.services.change_request_service import (
    ScheduleChangeRequestError,
    adjustment_options,
    apply_request,
    approve_request,
    cancel_request,
    get_request_for_lecturer,
    get_training_request,
    list_lecturer_requests,
    list_training_requests,
    reject_request,
    submit_request,
    validate_request,
)


LecturerUser = Annotated[AppUserModel, Depends(require_roles(UserRole.LECTURER))]
TrainingOfficeUser = Annotated[
    AppUserModel,
    Depends(require_roles(UserRole.TRAINING_OFFICE)),
]

lecturer_change_requests_router = APIRouter(
    prefix="/api/lecturer/change-requests",
    tags=["lecturer-change-requests"],
)
training_change_requests_router = APIRouter(
    prefix="/api/training-office/change-requests",
    tags=["training-office-change-requests"],
)


class SubmitScheduleChangeRequest(BaseModel):
    official_code: str = Field(min_length=1, max_length=50)
    section_code: str = Field(min_length=1, max_length=80)
    occurrence_date: date
    request_type: ScheduleChangeRequestType
    reason: str = Field(min_length=1, max_length=2000)
    proposed_date: date | None = None
    proposed_slot_code: str | None = Field(default=None, max_length=50)
    proposed_room_code: str | None = Field(default=None, max_length=50)

    @field_validator("official_code", "section_code", "reason")
    @classmethod
    def non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Thông tin bắt buộc không được để trống.")
        return normalized

    @field_validator("proposed_slot_code", "proposed_room_code")
    @classmethod
    def normalize_optional_code(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class ReviewNoteRequest(BaseModel):
    note: str = Field(default="", max_length=2000)


class RejectScheduleChangeRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Phải nhập lý do từ chối.")
        return normalized


@lecturer_change_requests_router.post("")
def create_lecturer_change_request(
    request: SubmitScheduleChangeRequest,
    current_user: LecturerUser,
) -> dict[str, Any]:
    created = _call(
        submit_request,
        current_user,
        official_code=request.official_code,
        section_code=request.section_code,
        occurrence_date=request.occurrence_date,
        request_type=request.request_type,
        reason=request.reason,
        proposed_date=request.proposed_date,
        proposed_slot_code=request.proposed_slot_code,
        proposed_room_code=request.proposed_room_code,
    )
    return {"message": "Đã gửi yêu cầu điều chỉnh lịch. Lịch chính thức chưa thay đổi.", "request": created}


@lecturer_change_requests_router.get("")
def get_lecturer_change_requests(current_user: LecturerUser) -> dict[str, Any]:
    return _call(list_lecturer_requests, current_user.id)


# This static route must be registered before /{request_code}.
@lecturer_change_requests_router.get("/options")
def get_lecturer_adjustment_options(
    current_user: LecturerUser,
    official_code: str = Query(min_length=1, max_length=50),
    section_code: str = Query(min_length=1, max_length=80),
    occurrence_date: date = Query(),
    target_date: date = Query(),
) -> dict[str, Any]:
    return _call(
        adjustment_options,
        current_user,
        official_code=official_code,
        section_code=section_code,
        occurrence_date=occurrence_date,
        target_date=target_date,
    )


@lecturer_change_requests_router.get("/{request_code}")
def get_lecturer_change_request(
    request_code: str,
    current_user: LecturerUser,
) -> dict[str, Any]:
    return _call(get_request_for_lecturer, request_code, current_user.id)


@lecturer_change_requests_router.post("/{request_code}/cancel")
def cancel_lecturer_change_request(
    request_code: str,
    current_user: LecturerUser,
) -> dict[str, Any]:
    cancelled = _call(cancel_request, request_code, current_user)
    return {"message": "Đã hủy yêu cầu đang chờ xử lý.", "request": cancelled}


@training_change_requests_router.get("")
def get_training_change_requests(
    current_user: TrainingOfficeUser,
    status: ScheduleChangeRequestStatus | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    del current_user
    return _call(list_training_requests, status, limit=limit, offset=offset)


@training_change_requests_router.get("/{request_code}")
def get_training_change_request(
    request_code: str,
    current_user: TrainingOfficeUser,
) -> dict[str, Any]:
    del current_user
    return _call(get_training_request, request_code)


@training_change_requests_router.post("/{request_code}/validate")
def validate_training_change_request(
    request_code: str,
    current_user: TrainingOfficeUser,
) -> dict[str, Any]:
    request, validation = _call(validate_request, request_code, current_user)
    return {"request": request, "validation": validation}


@training_change_requests_router.post("/{request_code}/approve")
def approve_training_change_request(
    request_code: str,
    body: ReviewNoteRequest,
    current_user: TrainingOfficeUser,
) -> dict[str, Any]:
    request = _call(approve_request, request_code, current_user, body.note)
    return {"message": "Đã duyệt yêu cầu. Lịch chính thức chỉ thay đổi khi áp dụng.", "request": request}


@training_change_requests_router.post("/{request_code}/reject")
def reject_training_change_request(
    request_code: str,
    body: RejectScheduleChangeRequest,
    current_user: TrainingOfficeUser,
) -> dict[str, Any]:
    request = _call(reject_request, request_code, current_user, body.reason)
    return {"message": "Đã từ chối yêu cầu; lịch chính thức không thay đổi.", "request": request}


@training_change_requests_router.post("/{request_code}/apply")
def apply_training_change_request(
    request_code: str,
    current_user: TrainingOfficeUser,
) -> dict[str, Any]:
    request, official = _call(apply_request, request_code, current_user)
    return {
        "message": "Đã áp dụng yêu cầu sau khi kiểm tra lại toàn bộ ràng buộc cứng.",
        "request": request,
        "official": official,
    }


T = TypeVar("T")


def _call(function: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    try:
        return function(*args, **kwargs)
    except ScheduleChangeRequestError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

