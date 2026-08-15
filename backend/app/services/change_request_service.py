from __future__ import annotations

import copy
from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from backend.app.db.models import (
    AppUserModel,
    OfficialTimetableModel,
    ScheduleChangeLogModel,
    ScheduleChangeRequestEventModel,
    ScheduleChangeRequestModel,
)
from backend.app.db.session import get_session_local
from backend.app.domain.change_requests import (
    ScheduleChangeRequestStatus,
    ScheduleChangeRequestType,
)
from backend.app.services import runtime_store


class ScheduleChangeRequestError(Exception):
    def __init__(self, status_code: int, detail: str | dict[str, Any]) -> None:
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail


def submit_request(
    user: AppUserModel,
    *,
    official_code: str,
    section_code: str,
    occurrence_date: date,
    request_type: ScheduleChangeRequestType,
    reason: str,
    proposed_date: date | None,
    proposed_slot_code: str | None,
    proposed_room_code: str | None,
) -> dict[str, Any]:
    lecturer_code = _lecturer_code(user)
    _ensure_supported_request_type(request_type)
    _ensure_proposal_shape(request_type, proposed_date, proposed_slot_code, proposed_room_code)

    with get_session_local()() as session:
        official = _official_by_code(session, official_code, lock=True)
        _ensure_published(official)
        payload = copy.deepcopy(official.payload)
        _ensure_section_owned(payload, section_code, lecturer_code)
        occurrence = _active_occurrence(payload, section_code, occurrence_date)

        request = ScheduleChangeRequestModel(
            request_code=_new_request_code(),
            official_timetable_id=official.id,
            requester_user_id=user.id,
            requester_username=user.username,
            lecturer_code=lecturer_code,
            section_code=section_code,
            occurrence_date=occurrence_date,
            request_type=request_type.value,
            reason=reason.strip(),
            proposed_date=proposed_date,
            proposed_slot_code=proposed_slot_code,
            proposed_room_code=proposed_room_code,
            current_snapshot=_occurrence_snapshot(occurrence),
            proposal_snapshot=_proposal_snapshot(
                request_type,
                proposed_date,
                proposed_slot_code,
                proposed_room_code,
            ),
            status=ScheduleChangeRequestStatus.PENDING.value,
            expected_official_version=official.version_number,
        )

        # Submission never mutates the official timetable, but an impossible
        # move should be rejected immediately with actionable diagnostics.
        precheck = _validate_model(request, official, payload)
        if not precheck["valid"]:
            raise ScheduleChangeRequestError(422, _invalid_detail(precheck))

        session.add(request)
        session.flush()
        _add_event(
            session,
            request,
            action="SUBMITTED",
            actor=user,
            from_status=None,
            to_status=ScheduleChangeRequestStatus.PENDING.value,
            note=reason.strip(),
            snapshot={"current": request.current_snapshot, "proposal": request.proposal_snapshot},
        )
        session.commit()
        request_code = request.request_code

    return get_request_for_lecturer(request_code, user.id)


def list_lecturer_requests(user_id: int) -> dict[str, Any]:
    with get_session_local()() as session:
        requests = session.scalars(
            _request_query()
            .where(ScheduleChangeRequestModel.requester_user_id == user_id)
            .order_by(ScheduleChangeRequestModel.created_at.desc())
        ).unique().all()
        values = [_serialize_request(item) for item in requests]
        return {"requests": values, "total": len(values)}


def get_request_for_lecturer(request_code: str, user_id: int) -> dict[str, Any]:
    with get_session_local()() as session:
        request = session.scalar(
            _request_query().where(
                ScheduleChangeRequestModel.request_code == request_code,
                ScheduleChangeRequestModel.requester_user_id == user_id,
            )
        )
        if request is None:
            raise ScheduleChangeRequestError(404, "Không tìm thấy yêu cầu điều chỉnh lịch của bạn.")
        return _serialize_request(request)


def cancel_request(request_code: str, user: AppUserModel) -> dict[str, Any]:
    with get_session_local()() as session:
        request = session.scalar(
            select(ScheduleChangeRequestModel)
            .where(
                ScheduleChangeRequestModel.request_code == request_code,
                ScheduleChangeRequestModel.requester_user_id == user.id,
            )
            .with_for_update()
        )
        if request is None:
            raise ScheduleChangeRequestError(404, "Không tìm thấy yêu cầu điều chỉnh lịch của bạn.")
        _require_status(request, ScheduleChangeRequestStatus.PENDING, "Chỉ có thể hủy yêu cầu đang chờ xử lý.")
        previous_status = request.status
        request.status = ScheduleChangeRequestStatus.CANCELLED.value
        request.cancelled_at = _now()
        _add_event(
            session,
            request,
            action="CANCELLED",
            actor=user,
            from_status=previous_status,
            to_status=request.status,
            note="Giảng viên hủy yêu cầu.",
        )
        session.commit()
    return get_request_for_lecturer(request_code, user.id)


def list_training_requests(
    status: ScheduleChangeRequestStatus | None = None,
    *,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    with get_session_local()() as session:
        statement = _request_query().order_by(ScheduleChangeRequestModel.created_at.desc())
        if status is not None:
            statement = statement.where(ScheduleChangeRequestModel.status == status.value)
        total_statement = select(ScheduleChangeRequestModel.id)
        if status is not None:
            total_statement = total_statement.where(ScheduleChangeRequestModel.status == status.value)
        total = len(session.scalars(total_statement).all())
        requests = session.scalars(statement.offset(offset).limit(limit)).unique().all()
        values = [_serialize_request(item) for item in requests]
        return {"requests": values, "total": total}


def get_training_request(request_code: str) -> dict[str, Any]:
    with get_session_local()() as session:
        request = session.scalar(
            _request_query().where(ScheduleChangeRequestModel.request_code == request_code)
        )
        if request is None:
            raise ScheduleChangeRequestError(404, "Không tìm thấy yêu cầu điều chỉnh lịch.")
        return _serialize_request(request)


def validate_request(request_code: str, actor: AppUserModel) -> tuple[dict[str, Any], dict[str, Any]]:
    with get_session_local()() as session:
        request = _request_by_code(session, request_code, lock=True)
        _require_status(request, ScheduleChangeRequestStatus.PENDING, "Chỉ kiểm tra yêu cầu đang chờ xử lý.")
        official = _official_by_id(session, request.official_timetable_id, lock=True)
        result = _validate_model(request, official, copy.deepcopy(official.payload))
        request.validation_result = result
        request.validated_at = _now()
        if result["valid"]:
            request.expected_official_version = official.version_number
        _add_event(
            session,
            request,
            action="VALIDATED",
            actor=actor,
            from_status=request.status,
            to_status=request.status,
            note="Kiểm tra hợp lệ." if result["valid"] else "Kiểm tra phát hiện vi phạm ràng buộc cứng.",
            snapshot=result,
        )
        session.commit()
    return get_training_request(request_code), result


def approve_request(request_code: str, actor: AppUserModel, note: str = "") -> dict[str, Any]:
    with get_session_local()() as session:
        request = _request_by_code(session, request_code, lock=True)
        _require_status(request, ScheduleChangeRequestStatus.PENDING, "Chỉ có thể duyệt yêu cầu đang chờ xử lý.")
        official = _official_by_id(session, request.official_timetable_id, lock=True)
        _ensure_published(official)
        validation = request.validation_result or {}
        if not request.validated_at or not validation.get("valid"):
            raise ScheduleChangeRequestError(422, "Hãy kiểm tra xung đột và bảo đảm yêu cầu hợp lệ trước khi duyệt.")
        if int(validation.get("official_version") or -1) != official.version_number:
            raise ScheduleChangeRequestError(409, "Lịch chính thức đã thay đổi sau lần kiểm tra. Hãy kiểm tra lại yêu cầu trước khi duyệt.")
        previous_status = request.status
        request.status = ScheduleChangeRequestStatus.APPROVED.value
        request.reviewer_user_id = actor.id
        request.reviewer_username = actor.username
        request.review_note = note.strip() or None
        request.reviewed_at = _now()
        _add_event(
            session,
            request,
            action="APPROVED",
            actor=actor,
            from_status=previous_status,
            to_status=request.status,
            note=request.review_note,
            snapshot=validation,
        )
        session.commit()
    return get_training_request(request_code)


def reject_request(request_code: str, actor: AppUserModel, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ScheduleChangeRequestError(422, "Phải nhập lý do từ chối để giảng viên biết cách xử lý.")
    with get_session_local()() as session:
        request = _request_by_code(session, request_code, lock=True)
        _require_status(request, ScheduleChangeRequestStatus.PENDING, "Chỉ có thể từ chối yêu cầu đang chờ xử lý.")
        previous_status = request.status
        request.status = ScheduleChangeRequestStatus.REJECTED.value
        request.reviewer_user_id = actor.id
        request.reviewer_username = actor.username
        request.review_note = reason.strip()
        request.reviewed_at = _now()
        _add_event(
            session,
            request,
            action="REJECTED",
            actor=actor,
            from_status=previous_status,
            to_status=request.status,
            note=request.review_note,
        )
        session.commit()
    return get_training_request(request_code)


def apply_request(request_code: str, actor: AppUserModel) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the approved request and all audit writes in one transaction."""
    with get_session_local()() as session:
        request = _request_by_code(session, request_code, lock=True)
        _require_status(request, ScheduleChangeRequestStatus.APPROVED, "Chỉ có thể áp dụng yêu cầu đã được duyệt.")
        official = _official_by_id(session, request.official_timetable_id, lock=True)
        payload = copy.deepcopy(official.payload)
        validation = _validate_model(request, official, payload)
        if not validation["valid"]:
            raise ScheduleChangeRequestError(422, _invalid_detail(validation, prefix="Không thể áp dụng yêu cầu"))

        target = _active_occurrence(payload, request.section_code, request.occurrence_date)
        previous = _occurrence_snapshot(target)
        if request.request_type == ScheduleChangeRequestType.SUSPEND_ONE_OCCURRENCE.value:
            target["status"] = "SUSPENDED"
        else:
            calendar_date = _input_data(official).academic_calendar_dates[request.proposed_date]
            target.update(
                {
                    "date": request.proposed_date.isoformat(),
                    "academic_week": calendar_date.academic_week,
                    "slot_code": request.proposed_slot_code,
                    "room_code": request.proposed_room_code,
                    "status": "MOVED",
                }
            )
        current = _occurrence_snapshot(target)
        changed_at = _now().isoformat()
        history = list(payload.get("change_history", []))
        history.append(
            {
                "request_code": request.request_code,
                "section_code": request.section_code,
                "scope": request.request_type,
                "previous": previous,
                "current": current,
                "reason": request.reason,
                "changed_by": actor.username,
                "changed_at": changed_at,
            }
        )
        payload["change_history"] = history
        official.version_number += 1
        payload["version_number"] = official.version_number
        payload["status"] = official.status
        official.payload = payload
        official.updated_at = _now()

        previous_status = request.status
        request.status = ScheduleChangeRequestStatus.APPLIED.value
        request.validation_result = validation
        request.applied_at = _now()
        request.reviewer_user_id = request.reviewer_user_id or actor.id
        request.reviewer_username = request.reviewer_username or actor.username
        _add_event(
            session,
            request,
            action="APPLIED",
            actor=actor,
            from_status=previous_status,
            to_status=request.status,
            note="Đã áp dụng vào lịch chính thức sau khi kiểm tra lại ràng buộc.",
            snapshot={"previous": previous, "current": current, "validation": validation},
        )
        session.add(
            ScheduleChangeLogModel(
                run_code=None,
                official_code=official.official_code,
                request_id=request.id,
                section_code=request.section_code,
                scope=request.request_type,
                previous_value={"occurrence": previous},
                current_value={"occurrence": current},
                reason=request.reason,
                changed_by=actor.username,
                changed_at=_now().replace(tzinfo=None),
            )
        )
        session.commit()
        applied_official = copy.deepcopy(payload)

    return get_training_request(request_code), applied_official


def adjustment_options(
    user: AppUserModel,
    *,
    official_code: str,
    section_code: str,
    occurrence_date: date,
    target_date: date,
) -> dict[str, Any]:
    lecturer_code = _lecturer_code(user)
    with get_session_local()() as session:
        official = _official_by_code(session, official_code)
        _ensure_published(official)
        payload = copy.deepcopy(official.payload)
        _ensure_section_owned(payload, section_code, lecturer_code)
        occurrence = _active_occurrence(payload, section_code, occurrence_date)
        data = _input_data(official)
        section = data.course_sections.get(section_code)
        if section is None:
            raise ScheduleChangeRequestError(422, "Lớp học phần không còn trong dữ liệu nguồn của lịch chính thức.")

        slots: list[dict[str, Any]] = []
        for slot in sorted(data.time_slots.values(), key=lambda item: (item.start_period, item.end_period, item.slot_code)):
            if not slot.active or slot.day_of_week != target_date.isoweekday() + 1:
                continue
            if section.course_type not in slot.supports_course_types or slot.duration != section.periods_per_session:
                continue
            rooms: list[dict[str, Any]] = []
            for room in sorted(data.rooms.values(), key=lambda item: item.room_code):
                if not room.available or room.room_type != section.required_room_type:
                    continue
                if room.capacity < section.scheduling_student_count:
                    continue
                errors = _proposal_errors(
                    official,
                    payload,
                    section_code=section_code,
                    occurrence_date=occurrence_date,
                    target_date=target_date,
                    slot_code=slot.slot_code,
                    room_code=room.room_code,
                    data=data,
                )
                if errors:
                    continue
                rooms.append(
                    {
                        "room_code": room.room_code,
                        "room_name": room.room_name,
                        "capacity": room.capacity,
                    }
                )
            if rooms:
                slots.append(
                    {
                        "slot_code": slot.slot_code,
                        "day_of_week": slot.day_of_week,
                        "start_period": slot.start_period,
                        "end_period": slot.end_period,
                        "rooms": rooms,
                    }
                )
        return {
            "official_code": official_code,
            "section_code": section_code,
            "occurrence": _occurrence_snapshot(occurrence),
            "target_date": target_date.isoformat(),
            "slots": slots,
        }


def _validate_model(
    request: ScheduleChangeRequestModel,
    official: OfficialTimetableModel,
    payload: dict[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if official.status != "PUBLISHED":
        errors.append(_error("OFFICIAL_NOT_PUBLISHED", "Lịch chính thức đã bị thay thế; không thể xử lý yêu cầu này."))
    try:
        occurrence = _active_occurrence(payload, request.section_code, request.occurrence_date)
    except ScheduleChangeRequestError as exc:
        errors.append(_error("OCCURRENCE_NOT_AVAILABLE", str(exc.detail)))
        occurrence = None

    if request.request_type == ScheduleChangeRequestType.MOVE_RECURRING_SCHEDULE.value:
        errors.append(_error("RECURRING_DEADLINE_NOT_CONFIGURED", "Chưa cấu hình thời hạn đổi lịch lặp; hãy chọn đổi một buổi hoặc liên hệ Phòng Đào tạo."))
    elif request.request_type == ScheduleChangeRequestType.MOVE_ONE_OCCURRENCE.value:
        if request.proposed_date is None or not request.proposed_slot_code or not request.proposed_room_code:
            errors.append(_error("MISSING_PROPOSAL", "Yêu cầu chuyển buổi phải có ngày, khung giờ và phòng đề xuất."))
        else:
            try:
                data = _input_data(official)
            except ScheduleChangeRequestError as exc:
                errors.append(_error("INPUT_DATA_INVALID", str(exc.detail)))
            else:
                errors.extend(
                    _proposal_errors(
                        official,
                        payload,
                        section_code=request.section_code,
                        occurrence_date=request.occurrence_date,
                        target_date=request.proposed_date,
                        slot_code=request.proposed_slot_code,
                        room_code=request.proposed_room_code,
                        data=data,
                    )
                )
    elif request.request_type == ScheduleChangeRequestType.SUSPEND_ONE_OCCURRENCE.value and occurrence is None:
        # The occurrence-specific error above is sufficient.
        pass

    checked_at = _now().isoformat()
    return {
        "valid": not errors,
        "hard_conflicts": errors,
        "official_code": official.official_code,
        "official_version": official.version_number,
        "checked_at": checked_at,
    }


def _proposal_errors(
    official: OfficialTimetableModel,
    payload: dict[str, Any],
    *,
    section_code: str,
    occurrence_date: date,
    target_date: date,
    slot_code: str,
    room_code: str,
    data: Any,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    section = data.course_sections.get(section_code)
    slot = data.time_slots.get(slot_code)
    room = data.rooms.get(room_code)
    calendar_date = data.academic_calendar_dates.get(target_date)
    if section is None:
        return [_error("SECTION_NOT_FOUND", "Không tìm thấy lớp học phần trong dữ liệu nguồn.")]
    if calendar_date is None or not calendar_date.is_teaching_day or calendar_date.is_holiday:
        errors.append(_error("INVALID_TEACHING_DATE", "Ngày đề xuất phải là ngày giảng dạy, không phải ngày nghỉ hoặc ngày lễ."))
    elif calendar_date.day_of_week != target_date.isoweekday() + 1:
        errors.append(_error("CALENDAR_WEEKDAY_MISMATCH", "Thứ của ngày đề xuất không khớp lịch học vụ."))
    if not section.start_date <= target_date <= section.end_date:
        errors.append(_error("OUTSIDE_SECTION_RANGE", "Ngày đề xuất nằm ngoài khoảng hiệu lực của lớp học phần."))
    if slot is None:
        errors.append(_error("SLOT_NOT_FOUND", f"Không tìm thấy khung giờ {slot_code}."))
    else:
        if not slot.active:
            errors.append(_error("SLOT_INACTIVE", f"Khung giờ {slot_code} không được kích hoạt."))
        if slot.day_of_week != target_date.isoweekday() + 1:
            errors.append(_error("SLOT_WRONG_WEEKDAY", f"Khung giờ {slot_code} không thuộc đúng thứ của ngày đề xuất."))
        if section.course_type not in slot.supports_course_types or slot.duration != section.periods_per_session:
            errors.append(_error("SLOT_INCOMPATIBLE", "Khung giờ không phù hợp loại học phần hoặc số tiết của buổi học."))
    if room is None:
        errors.append(_error("ROOM_NOT_FOUND", f"Không tìm thấy phòng {room_code}."))
    else:
        if not room.available:
            errors.append(_error("ROOM_INACTIVE", f"Phòng {room_code} hiện không khả dụng."))
        if room.room_type != section.required_room_type:
            errors.append(_error("ROOM_TYPE", f"Phòng {room_code} không đáp ứng loại phòng {section.required_room_type}."))
        if room.capacity < section.scheduling_student_count:
            errors.append(_error("ROOM_CAPACITY", f"Phòng {room_code} không đủ sức chứa {section.scheduling_student_count} sinh viên."))
    if (room_code, slot_code) in {(item.room_code, item.slot_code) for item in data.room_unavailable_slots}:
        errors.append(_error("ROOM_UNAVAILABLE", f"Phòng {room_code} không sử dụng được tại khung giờ {slot_code}."))
    if (section.lecturer_code, slot_code) in {
        (item.lecturer_code, item.slot_code) for item in data.lecturer_time_preferences if item.mandatory
    }:
        errors.append(_error("LECTURER_RESTRICTION", "Khung giờ đề xuất vi phạm hạn chế cố định đã xác nhận của giảng viên."))

    if slot is not None:
        for other in payload.get("occurrences", []):
            if str(other.get("status") or "").upper() == "SUSPENDED":
                continue
            if other.get("section_code") == section_code and other.get("date") == occurrence_date.isoformat():
                continue
            if other.get("date") != target_date.isoformat():
                continue
            other_slot = data.time_slots.get(str(other.get("slot_code") or ""))
            other_section = data.course_sections.get(str(other.get("section_code") or ""))
            if other_slot is None or other_section is None or not _periods_overlap(slot, other_slot):
                continue
            if other.get("room_code") == room_code:
                errors.append(_error("ROOM_CONFLICT", f"Phòng {room_code} trùng tiết với lớp {other_section.section_code} trong ngày đề xuất."))
            if other_section.lecturer_code == section.lecturer_code:
                errors.append(_error("LECTURER_CONFLICT", f"Giảng viên {section.lecturer_code} trùng tiết với lớp {other_section.section_code} trong ngày đề xuất."))
    return errors


def _input_data(official: OfficialTimetableModel) -> Any:
    batch_code = str(official.payload.get("batch_code") or "")
    if not batch_code:
        raise ScheduleChangeRequestError(422, "Lịch chính thức không có mã bộ dữ liệu nguồn.")
    try:
        result = runtime_store.validate_sample_dataset(runtime_store.batch_directory(batch_code))
    except Exception as exc:
        if isinstance(exc, ScheduleChangeRequestError):
            raise
        raise ScheduleChangeRequestError(422, "Không thể đọc bộ dữ liệu nguồn của lịch chính thức.") from exc
    if not result.is_valid or result.data is None:
        raise ScheduleChangeRequestError(422, "Bộ dữ liệu nguồn của lịch chính thức không còn hợp lệ.")
    return result.data


def _ensure_supported_request_type(request_type: ScheduleChangeRequestType) -> None:
    if request_type == ScheduleChangeRequestType.MOVE_RECURRING_SCHEDULE:
        raise ScheduleChangeRequestError(
            422,
            "Chưa cấu hình thời hạn đổi lịch lặp. Hãy chọn đổi một buổi hoặc liên hệ Phòng Đào tạo.",
        )


def _ensure_proposal_shape(
    request_type: ScheduleChangeRequestType,
    proposed_date: date | None,
    proposed_slot_code: str | None,
    proposed_room_code: str | None,
) -> None:
    provided = (proposed_date, proposed_slot_code, proposed_room_code)
    if request_type == ScheduleChangeRequestType.MOVE_ONE_OCCURRENCE and not all(provided):
        raise ScheduleChangeRequestError(422, "Yêu cầu chuyển buổi phải có đầy đủ ngày, khung giờ và phòng đề xuất.")
    if request_type == ScheduleChangeRequestType.SUSPEND_ONE_OCCURRENCE and any(provided):
        raise ScheduleChangeRequestError(422, "Yêu cầu tạm ngưng một buổi không được kèm phương án chuyển phòng hoặc khung giờ.")


def _ensure_section_owned(payload: dict[str, Any], section_code: str, lecturer_code: str) -> dict[str, Any]:
    assignment = next(
        (item for item in payload.get("assignments", []) if item.get("section_code") == section_code),
        None,
    )
    if assignment is None or str(assignment.get("lecturer_code") or "") != lecturer_code:
        raise ScheduleChangeRequestError(403, "Bạn chỉ có thể gửi yêu cầu cho lớp học phần được phân công cho mình.")
    return assignment


def _active_occurrence(payload: dict[str, Any], section_code: str, occurrence_date: date) -> dict[str, Any]:
    occurrence = next(
        (
            item
            for item in payload.get("occurrences", [])
            if item.get("section_code") == section_code and item.get("date") == occurrence_date.isoformat()
        ),
        None,
    )
    if occurrence is None:
        raise ScheduleChangeRequestError(422, "Không tìm thấy buổi học đã chọn trong lịch chính thức hiện tại.")
    if str(occurrence.get("status") or "").upper() == "SUSPENDED":
        raise ScheduleChangeRequestError(422, "Buổi học đã tạm ngưng nên không thể tạo hoặc áp dụng thêm yêu cầu.")
    return occurrence


def _ensure_published(official: OfficialTimetableModel) -> None:
    if official.status != "PUBLISHED":
        raise ScheduleChangeRequestError(409, "Lịch chính thức đã bị thay thế; không thể xử lý yêu cầu này.")


def _require_status(
    request: ScheduleChangeRequestModel,
    required: ScheduleChangeRequestStatus,
    message: str,
) -> None:
    if request.status != required.value:
        raise ScheduleChangeRequestError(409, message)


def _official_by_code(session: Session, official_code: str, *, lock: bool = False) -> OfficialTimetableModel:
    statement = select(OfficialTimetableModel).where(OfficialTimetableModel.official_code == official_code)
    if lock:
        statement = statement.with_for_update()
    official = session.scalar(statement)
    if official is None:
        raise ScheduleChangeRequestError(404, "Không tìm thấy lịch chính thức.")
    return official


def _official_by_id(session: Session, official_id: int, *, lock: bool = False) -> OfficialTimetableModel:
    statement = select(OfficialTimetableModel).where(OfficialTimetableModel.id == official_id)
    if lock:
        statement = statement.with_for_update()
    official = session.scalar(statement)
    if official is None:
        raise ScheduleChangeRequestError(404, "Không tìm thấy lịch chính thức của yêu cầu.")
    return official


def _request_by_code(session: Session, request_code: str, *, lock: bool = False) -> ScheduleChangeRequestModel:
    statement = select(ScheduleChangeRequestModel).where(ScheduleChangeRequestModel.request_code == request_code)
    if lock:
        statement = statement.with_for_update()
    request = session.scalar(statement)
    if request is None:
        raise ScheduleChangeRequestError(404, "Không tìm thấy yêu cầu điều chỉnh lịch.")
    return request


def _request_query():
    return select(ScheduleChangeRequestModel).options(
        joinedload(ScheduleChangeRequestModel.official_timetable),
        joinedload(ScheduleChangeRequestModel.requester),
        joinedload(ScheduleChangeRequestModel.reviewer),
        selectinload(ScheduleChangeRequestModel.events),
    )


def _add_event(
    session: Session,
    request: ScheduleChangeRequestModel,
    *,
    action: str,
    actor: AppUserModel,
    from_status: str | None,
    to_status: str | None,
    note: str | None = None,
    snapshot: dict[str, Any] | None = None,
) -> None:
    session.add(
        ScheduleChangeRequestEventModel(
            request_id=request.id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            actor_user_id=actor.id,
            actor_username=actor.username,
            note=note.strip() if note else None,
            snapshot=copy.deepcopy(snapshot),
            created_at=_now(),
        )
    )


def _serialize_request(request: ScheduleChangeRequestModel) -> dict[str, Any]:
    return {
        "request_code": request.request_code,
        "official_code": request.official_timetable.official_code,
        "requester_username": request.requester_username,
        "requester_display_name": request.requester.display_name,
        "lecturer_code": request.lecturer_code,
        "section_code": request.section_code,
        "occurrence_date": request.occurrence_date.isoformat(),
        "request_type": request.request_type,
        "reason": request.reason,
        "proposed_date": request.proposed_date.isoformat() if request.proposed_date else None,
        "proposed_slot_code": request.proposed_slot_code,
        "proposed_room_code": request.proposed_room_code,
        "current_snapshot": copy.deepcopy(request.current_snapshot),
        "proposal_snapshot": copy.deepcopy(request.proposal_snapshot),
        "status": request.status,
        "expected_official_version": request.expected_official_version,
        "reviewer_username": request.reviewer_username,
        "reviewer_display_name": request.reviewer.display_name if request.reviewer else None,
        "review_note": request.review_note,
        "validation_result": copy.deepcopy(request.validation_result),
        "validated_at": _iso(request.validated_at),
        "reviewed_at": _iso(request.reviewed_at),
        "applied_at": _iso(request.applied_at),
        "cancelled_at": _iso(request.cancelled_at),
        "created_at": _iso(request.created_at),
        "updated_at": _iso(request.updated_at),
        "events": [
            {
                "event_type": event.action,
                "action": event.action,
                "from_status": event.from_status,
                "to_status": event.to_status,
                "actor_username": event.actor_username,
                "actor_display_name": event.actor.display_name if event.actor else event.actor_username,
                "note": event.note,
                "snapshot": copy.deepcopy(event.snapshot),
                "created_at": _iso(event.created_at),
            }
            for event in request.events
        ],
    }


def _occurrence_snapshot(occurrence: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(occurrence.get(key))
        for key in ("section_code", "date", "academic_week", "room_code", "slot_code", "status")
    }


def _proposal_snapshot(
    request_type: ScheduleChangeRequestType,
    proposed_date: date | None,
    proposed_slot_code: str | None,
    proposed_room_code: str | None,
) -> dict[str, Any] | None:
    if request_type == ScheduleChangeRequestType.SUSPEND_ONE_OCCURRENCE:
        return {"status": "SUSPENDED"}
    if proposed_date is None:
        return None
    return {
        "date": proposed_date.isoformat(),
        "slot_code": proposed_slot_code,
        "room_code": proposed_room_code,
        "status": "MOVED",
    }


def _new_request_code() -> str:
    return f"REQ-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid4().hex[:6].upper()}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _periods_overlap(first: Any, second: Any) -> bool:
    return first.start_period <= second.end_period and second.start_period <= first.end_period


def _error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _invalid_detail(result: dict[str, Any], *, prefix: str = "Phương án đề xuất không hợp lệ") -> dict[str, Any]:
    return {"message": f"{prefix}. Hãy sửa các lỗi được liệt kê.", "validation": result}


def _lecturer_code(user: AppUserModel) -> str:
    if not user.lecturer_code:
        raise ScheduleChangeRequestError(403, "Tài khoản giảng viên chưa được gắn mã giảng viên.")
    return user.lecturer_code
