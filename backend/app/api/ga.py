from __future__ import annotations

import csv
import unicodedata
import zipfile
from datetime import date, datetime, timezone
from html import escape
from io import StringIO
from io import BytesIO
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from backend.app.api.dependencies import require_roles
from backend.app.algorithms.genetic.simple_ga import GeneticAlgorithmConfig, run_simple_genetic_algorithm
from backend.app.algorithms.genetic.soft_constraints import SoftConstraintWeights
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.db.models import AppUserModel
from backend.app.domain.auth import UserRole
from backend.app.scheduling.calendar_expansion import expand_base_assignments_to_occurrences
from backend.app.services.runtime_store import (
    batch_directory,
    batch_summary,
    create_run,
    list_official_timetables,
    list_runs,
    persist_change_log,
    persist_ga_run,
    publish_run_as_official,
    read_official_timetable,
    read_run,
    sync_official_segments_and_makeups,
    write_official_timetable,
)


router = APIRouter(
    prefix="/api/ga",
    tags=["ga"],
    dependencies=[Depends(require_roles(UserRole.TRAINING_OFFICE))],
)

TrainingOfficeUser = Annotated[
    AppUserModel,
    Depends(require_roles(UserRole.TRAINING_OFFICE)),
]


class SoftWeightsRequest(BaseModel):
    lecturer_preferences: float = Field(default=10.0, ge=0)
    room_capacity_waste: float = Field(default=1.0, ge=0)
    large_room_small_class: float = Field(default=25.0, ge=0)
    schedule_gaps: float = Field(default=4.0, ge=0)
    scattered_days: float = Field(default=8.0, ge=0)
    consecutive_sessions: float = Field(default=6.0, ge=0)
    evening_weekend_avoidance: float = Field(default=5.0, ge=0)


class GaRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_code: str = Field(min_length=1)
    population_size: int = Field(default=80, ge=1)
    generations: int = Field(default=200, ge=1)
    seed: int | None = 42
    crossover_rate: float = Field(default=0.8, ge=0, le=1)
    mutation_rate: float = Field(default=0.1, ge=0, le=1)
    elite_count: int = Field(default=2, ge=0)
    tournament_size: int = Field(default=3, ge=1)
    target_soft_cost: float | None = Field(default=None, ge=0)
    soft_weights: SoftWeightsRequest = Field(default_factory=SoftWeightsRequest)


@router.post("/runs/preview")
def run_ga_preview(request: GaRunRequest) -> dict[str, object]:
    data_dir = batch_directory(request.batch_code)
    validation_result = validate_sample_dataset(data_dir)
    if not validation_result.is_valid or validation_result.data is None:
        return {
            "status": "FAILED",
            "stop_reason": "INVALID_INPUT_DATA",
            "errors": [
                {
                    "file": error.file,
                    "row": error.row,
                    "column": error.column,
                    "value": error.value,
                    "reason": error.reason,
                }
                for error in validation_result.errors
            ],
        }

    result = run_simple_genetic_algorithm(
        validation_result.data,
        GeneticAlgorithmConfig(
            population_size=request.population_size,
            generations=request.generations,
            seed=request.seed,
            crossover_rate=request.crossover_rate,
            mutation_rate=request.mutation_rate,
            elite_count=request.elite_count,
            tournament_size=request.tournament_size,
            target_soft_cost=request.target_soft_cost,
            soft_weights=SoftConstraintWeights(**request.soft_weights.model_dump()),
        ),
    )
    if result.best_candidate is None:
        raise HTTPException(status_code=422, detail={"status": result.status, "diagnostics": list(result.diagnostics)})

    data = validation_result.data
    response = {
        "status": result.status,
        "stop_reason": result.stop_reason,
        "generation_count": result.generation_count,
        "seed": result.seed,
        "execution_time_seconds": result.execution_time_seconds,
        "diagnostics": list(result.diagnostics),
        "evaluation": {
            "hard_violation_count": result.best_candidate.evaluation.hard_violation_count,
            "soft_cost": result.best_candidate.evaluation.soft_cost,
            "total_cost": result.best_candidate.evaluation.total_cost,
            "soft_breakdown": result.best_candidate.evaluation.soft_breakdown,
            "hard_violations": [
                {
                    "code": violation.code,
                    "message": violation.message,
                    "section_code": violation.section_code,
                    "other_section_code": violation.other_section_code,
                    "lecturer_code": violation.lecturer_code,
                    "room_code": violation.room_code,
                    "slot_code": violation.slot_code,
                }
                for violation in result.best_candidate.evaluation.hard_violations
            ],
        },
        "assignments": [
            {
                "section_code": assignment.section_code,
                "course_code": data.course_sections[assignment.section_code].course_code,
                "course_name": data.course_sections[assignment.section_code].course_name,
                "lecturer_code": data.course_sections[assignment.section_code].lecturer_code,
                "lecturer_name": data.lecturers[data.course_sections[assignment.section_code].lecturer_code].lecturer_name,
                "room_code": assignment.room_code,
                "slot_code": assignment.slot_code,
                "day_of_week": data.time_slots[assignment.slot_code].day_of_week,
                "start_period": data.time_slots[assignment.slot_code].start_period,
                "end_period": data.time_slots[assignment.slot_code].end_period,
                "course_type": data.course_sections[assignment.section_code].course_type,
                "required_room_type": data.course_sections[assignment.section_code].required_room_type,
                "scheduling_student_count": data.course_sections[assignment.section_code].scheduling_student_count,
            }
            for assignment in sorted(result.best_candidate.assignments, key=lambda item: item.section_code)
        ],
        "configuration": {
            "population_size": request.population_size,
            "generations": request.generations,
            "seed": request.seed,
            "crossover_rate": request.crossover_rate,
            "mutation_rate": request.mutation_rate,
            "elite_count": request.elite_count,
            "tournament_size": request.tournament_size,
            "target_soft_cost": request.target_soft_cost,
            "soft_weights": request.soft_weights.model_dump(),
        },
    }
    expansion = expand_base_assignments_to_occurrences(validation_result.data, result.best_candidate.assignments)
    response["occurrence_summary"] = {
        "scheduled_count": len(expansion.occurrences),
        "skipped_holiday_count": len(expansion.skipped_holiday_sessions),
        "missing_session_count": max(0, sum(section.required_sessions for section in data.course_sections.values()) - len(expansion.occurrences)),
    }
    response["occurrences"] = [
        {"section_code": item.section_code, "room_code": item.room_code, "slot_code": item.slot_code, "date": item.date.isoformat(), "academic_week": item.academic_week, "status": item.status}
        for item in expansion.occurrences
    ]
    response["skipped_holiday_sessions"] = [
        {
            "section_code": item.section_code,
            "course_code": data.course_sections[item.section_code].course_code,
            "course_name": data.course_sections[item.section_code].course_name,
            "lecturer_code": data.course_sections[item.section_code].lecturer_code,
            "lecturer_name": data.lecturers[data.course_sections[item.section_code].lecturer_code].lecturer_name,
            "course_type": data.course_sections[item.section_code].course_type,
            "room_code": item.room_code,
            "slot_code": item.slot_code,
            "date": item.date.isoformat(),
            "academic_week": item.academic_week,
            "holiday_name": item.holiday_name,
            "status": "MISSING",
        }
        for item in expansion.skipped_holiday_sessions
    ]
    response["batch_code"] = request.batch_code
    response["batch_display_name"] = str(batch_summary(request.batch_code).get("display_name") or request.batch_code)
    response["run_code"] = create_run(response)
    persist_ga_run(request.batch_code, response, validation_result.data)
    return response


@router.get("/runs")
def get_ga_runs(limit: int = 20) -> dict[str, object]:
    return {"runs": list_runs(max(1, min(limit, 100)))}


@router.get("/runs/{run_code}")
def get_ga_run(run_code: str) -> dict[str, object]:
    return read_run(run_code)


class AdjustmentRequest(BaseModel):
    section_code: str
    room_code: str
    slot_code: str


class OccurrenceAdjustmentRequest(BaseModel):
    """A direct change to exactly one dated teaching session."""

    section_code: str
    occurrence_date: date
    new_date: date
    room_code: str
    slot_code: str
    reason: str = Field(min_length=1, max_length=1000)


@router.get("/runs/{run_code}/adjustment-options/{section_code}")
def get_adjustment_options(run_code: str, section_code: str) -> dict[str, object]:
    run = read_run(run_code)
    data_result = validate_sample_dataset(batch_directory(str(run.get("batch_code", ""))))
    if not data_result.is_valid or data_result.data is None or section_code not in data_result.data.course_sections:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần hoặc bộ dữ liệu.")
    data = data_result.data
    section = data.course_sections[section_code]
    other_assignments = [item for item in run.get("assignments", []) if item["section_code"] != section_code]
    compatible_rooms = [room for room in data.rooms.values() if room.available and room.room_type == section.required_room_type and room.capacity >= section.scheduling_student_count]
    unavailable_slots = {(item.room_code, item.slot_code) for item in data.room_unavailable_slots}
    options: list[dict[str, object]] = []
    for slot in data.time_slots.values():
        if not slot.active or section.course_type not in slot.supports_course_types or slot.duration != section.periods_per_session:
            continue
        conflicts = [item for item in other_assignments if _slots_overlap(slot, data.time_slots[str(item["slot_code"])])]
        if any(item["lecturer_code"] == section.lecturer_code for item in conflicts):
            continue
        rooms = [
            {"room_code": room.room_code, "room_name": room.room_name, "capacity": room.capacity}
            for room in compatible_rooms
            if (room.room_code, slot.slot_code) not in unavailable_slots
            and not any(item["room_code"] == room.room_code for item in conflicts)
        ]
        if rooms:
            options.append({"slot_code": slot.slot_code, "day_of_week": slot.day_of_week, "start_period": slot.start_period, "end_period": slot.end_period, "rooms": sorted(rooms, key=lambda item: str(item["room_code"]))})
    return {"slots": sorted(options, key=lambda item: (int(item["day_of_week"]), int(item["start_period"])))}


@router.get("/runs/{run_code}/occurrence-adjustment-options/{section_code}/{occurrence_date}")
def get_occurrence_adjustment_options(
    run_code: str, section_code: str, occurrence_date: date, target_date: date | None = None
) -> dict[str, object]:
    """Return valid slot/room choices for one occurrence on its chosen date."""
    run = read_run(run_code)
    data_result = validate_sample_dataset(batch_directory(str(run.get("batch_code", ""))))
    if not data_result.is_valid or data_result.data is None:
        raise HTTPException(status_code=422, detail="Không thể kiểm tra bộ dữ liệu của lần chạy.")
    data = data_result.data
    section = data.course_sections.get(section_code)
    selected_date = target_date or occurrence_date
    occurrences = list(run.get("occurrences", []))
    target = next((item for item in occurrences if item.get("section_code") == section_code and item.get("date") == occurrence_date.isoformat()), None)
    if section is None or target is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy buổi học cần điều chỉnh.")
    calendar_date = data.academic_calendar_dates.get(selected_date)
    if calendar_date is None or not calendar_date.is_teaching_day or calendar_date.is_holiday:
        raise HTTPException(status_code=422, detail="Ngày mới không phải ngày học hợp lệ trong lịch học kỳ.")

    compatible_rooms = [room for room in data.rooms.values() if room.available and room.room_type == section.required_room_type and room.capacity >= section.scheduling_student_count]
    unavailable_slots = {(item.room_code, item.slot_code) for item in data.room_unavailable_slots}
    other_occurrences = [item for item in occurrences if item is not target and item.get("date") == selected_date.isoformat()]
    options: list[dict[str, object]] = []
    for slot in data.time_slots.values():
        if slot.day_of_week != selected_date.isoweekday() + 1 or not slot.active or section.course_type not in slot.supports_course_types or slot.duration != section.periods_per_session:
            continue
        conflicts = [item for item in other_occurrences if _periods_overlap(slot, data.time_slots[str(item["slot_code"])])]
        if any(data.course_sections[str(item["section_code"])].lecturer_code == section.lecturer_code for item in conflicts):
            continue
        rooms = [
            {"room_code": room.room_code, "room_name": room.room_name, "capacity": room.capacity}
            for room in compatible_rooms
            if (room.room_code, slot.slot_code) not in unavailable_slots and not any(item["room_code"] == room.room_code for item in conflicts)
        ]
        if rooms:
            options.append({"slot_code": slot.slot_code, "day_of_week": slot.day_of_week, "start_period": slot.start_period, "end_period": slot.end_period, "rooms": sorted(rooms, key=lambda item: str(item["room_code"]))})
    return {"date": selected_date.isoformat(), "slots": sorted(options, key=lambda item: int(item["start_period"]))}


@router.put("/runs/{run_code}/occurrences")
def adjust_occurrence(run_code: str, request: OccurrenceAdjustmentRequest) -> dict[str, object]:
    raise HTTPException(
        status_code=409,
        detail="Phương án GA là bất biến. Hãy công bố phương án thành lịch chính thức trước khi điều chỉnh.",
    )


@router.put("/runs/{run_code}/assignments")
def adjust_assignment(run_code: str, request: AdjustmentRequest) -> dict[str, object]:
    raise HTTPException(
        status_code=409,
        detail="Phương án GA là bất biến. Hãy công bố phương án thành lịch chính thức trước khi điều chỉnh.",
    )


class PublishRunRequest(BaseModel):
    note: str = Field(default="", max_length=1000)


class OfficialAdjustmentRequest(BaseModel):
    section_code: str
    scope: Literal["ONE_OCCURRENCE", "DATE_RANGE", "FROM_DATE_TO_END"]
    occurrence_date: date | None = None
    effective_start_date: date | None = None
    effective_end_date: date | None = None
    room_code: str
    slot_code: str
    reason: str = Field(min_length=1, max_length=1000)


class ScheduleSegmentRequest(BaseModel):
    section_code: str
    effective_start_date: date
    effective_end_date: date
    room_code: str
    slot_code: str
    reason: str = Field(min_length=1, max_length=1000)


class MakeupSessionRequest(BaseModel):
    section_code: str
    makeup_date: date
    room_code: str
    slot_code: str
    original_missing_date: date | None = None
    reason: str = Field(min_length=1, max_length=1000)


@router.post("/runs/{run_code}/publish")
def publish_ga_run(run_code: str, request: PublishRunRequest) -> dict[str, object]:
    return publish_run_as_official(run_code, request.note)


@router.get("/official-timetables")
def get_official_timetables() -> dict[str, object]:
    return {"official_timetables": list_official_timetables()}


@router.get("/official-timetables/{official_code}")
def get_official_timetable(official_code: str) -> dict[str, object]:
    return read_official_timetable(official_code)


@router.put("/official-timetables/{official_code}/adjustments")
def adjust_official_timetable(
    official_code: str,
    request: OfficialAdjustmentRequest,
    current_user: TrainingOfficeUser,
) -> dict[str, object]:
    official = read_official_timetable(official_code)
    data = _official_input_data(official)
    affected = _select_affected_occurrences(official, request)
    _validate_adjustment_input(data, official, request.section_code, request.room_code, request.slot_code, affected)
    room, slot = data.rooms[request.room_code], data.time_slots[request.slot_code]
    previous = [{key: item.get(key) for key in ("date", "room_code", "slot_code", "academic_week", "status")} for item in affected]
    for item in affected:
        item.update({"room_code": room.room_code, "slot_code": slot.slot_code, "status": "EXCEPTION" if request.scope == "ONE_OCCURRENCE" else "ADJUSTED"})
    _validate_effective_occurrence_conflicts(data, official)
    current = [{key: item.get(key) for key in ("date", "room_code", "slot_code", "academic_week", "status")} for item in affected]
    history = list(official.get("change_history", []))
    history.append({"section_code": request.section_code, "scope": request.scope, "previous": previous, "current": current, "reason": request.reason.strip(), "changed_by": current_user.username, "changed_at": datetime.now(timezone.utc).isoformat()})
    official["change_history"] = history
    write_official_timetable(official_code, official)
    persist_change_log(None, request.section_code, {"occurrences": previous}, {"occurrences": current}, scope=request.scope, reason=request.reason.strip(), official_code=official_code, changed_by=current_user.username)
    return {"message": "Đã điều chỉnh lịch chính thức sau khi kiểm tra ràng buộc.", "official": official}


@router.post("/official-timetables/{official_code}/segments")
def create_schedule_segment(
    official_code: str,
    request: ScheduleSegmentRequest,
    current_user: TrainingOfficeUser,
) -> dict[str, object]:
    if request.effective_end_date < request.effective_start_date:
        raise HTTPException(status_code=422, detail="Ngày kết thúc phân đoạn phải sau hoặc bằng ngày bắt đầu.")
    official = read_official_timetable(official_code)
    data = _official_input_data(official)
    existing_segments = list(official.get("segments", []))
    for item in existing_segments:
        if item.get("section_code") != request.section_code:
            continue
        start, end = date.fromisoformat(str(item["effective_start_date"])), date.fromisoformat(str(item["effective_end_date"]))
        if request.effective_start_date <= end and start <= request.effective_end_date:
            raise HTTPException(status_code=422, detail="Phân đoạn mới chồng lấn với một phân đoạn hiện có của lớp học phần.")
    affected = [item for item in official.get("occurrences", []) if item.get("section_code") == request.section_code and request.effective_start_date <= date.fromisoformat(str(item["date"])) <= request.effective_end_date]
    if not affected:
        raise HTTPException(status_code=422, detail="Không có buổi học thường kỳ trong khoảng ngày đã chọn để tạo phân đoạn.")
    _validate_adjustment_input(data, official, request.section_code, request.room_code, request.slot_code, affected)
    segment = request.model_dump(mode="json")
    existing_segments.append(segment)
    official["segments"] = existing_segments
    for item in affected:
        item.update({"room_code": request.room_code, "slot_code": request.slot_code, "status": "SEGMENT"})
    _validate_effective_occurrence_conflicts(data, official)
    write_official_timetable(official_code, official)
    sync_official_segments_and_makeups(official_code, official)
    persist_change_log(None, request.section_code, {}, segment, scope="DATE_RANGE_SEGMENT", reason=request.reason.strip(), official_code=official_code, changed_by=current_user.username)
    return {"message": "Đã tạo phân đoạn lịch và cập nhật các buổi nằm trong khoảng hiệu lực.", "official": official}


@router.post("/official-timetables/{official_code}/makeups")
def create_makeup_session(
    official_code: str,
    request: MakeupSessionRequest,
    current_user: TrainingOfficeUser,
) -> dict[str, object]:
    official = read_official_timetable(official_code)
    data = _official_input_data(official)
    section = data.course_sections.get(request.section_code)
    calendar_date = data.academic_calendar_dates.get(request.makeup_date)
    if section is None or calendar_date is None or not calendar_date.is_teaching_day or calendar_date.is_holiday:
        raise HTTPException(status_code=422, detail="Buổi bù phải thuộc lớp học phần và ngày học hợp lệ trong học kỳ.")
    if not section.start_date <= request.makeup_date <= section.end_date:
        raise HTTPException(status_code=422, detail="Ngày học bù phải nằm trong khoảng ngày hiệu lực của lớp học phần.")
    placeholder = {"section_code": request.section_code, "date": request.makeup_date.isoformat(), "room_code": request.room_code, "slot_code": request.slot_code, "academic_week": calendar_date.academic_week, "status": "MAKEUP"}
    _validate_adjustment_input(data, official, request.section_code, request.room_code, request.slot_code, [placeholder])
    official.setdefault("occurrences", []).append(placeholder)
    official.setdefault("makeup_sessions", []).append({**placeholder, "original_missing_date": request.original_missing_date.isoformat() if request.original_missing_date else None, "reason": request.reason.strip()})
    _validate_effective_occurrence_conflicts(data, official)
    write_official_timetable(official_code, official)
    sync_official_segments_and_makeups(official_code, official)
    persist_change_log(None, request.section_code, {}, placeholder, scope="MAKEUP", reason=request.reason.strip(), official_code=official_code, changed_by=current_user.username)
    return {"message": "Đã thêm buổi học bù sau khi kiểm tra ràng buộc.", "official": official}


def _official_input_data(official: dict[str, object]):
    batch_code = str(official.get("batch_code") or "")
    result = validate_sample_dataset(batch_directory(batch_code))
    if not result.is_valid or result.data is None:
        raise HTTPException(status_code=422, detail="Không thể đọc dữ liệu đầu vào của lịch chính thức.")
    return result.data


def _select_affected_occurrences(official: dict[str, object], request: OfficialAdjustmentRequest) -> list[dict[str, object]]:
    occurrences = [item for item in official.get("occurrences", []) if item.get("section_code") == request.section_code and item.get("status") != "MAKEUP"]
    if request.scope == "ONE_OCCURRENCE":
        if request.occurrence_date is None:
            raise HTTPException(status_code=422, detail="Phải chọn ngày của buổi học cần điều chỉnh.")
        affected = [item for item in occurrences if item.get("date") == request.occurrence_date.isoformat()]
    elif request.scope == "DATE_RANGE":
        if request.effective_start_date is None or request.effective_end_date is None or request.effective_end_date < request.effective_start_date:
            raise HTTPException(status_code=422, detail="Khoảng ngày điều chỉnh không hợp lệ.")
        affected = [item for item in occurrences if request.effective_start_date <= date.fromisoformat(str(item["date"])) <= request.effective_end_date]
    else:
        if request.effective_start_date is None:
            raise HTTPException(status_code=422, detail="Phải chọn ngày bắt đầu điều chỉnh.")
        affected = [item for item in occurrences if date.fromisoformat(str(item["date"])) >= request.effective_start_date]
    if not affected:
        raise HTTPException(status_code=404, detail="Không tìm thấy buổi học thường kỳ phù hợp với phạm vi đã chọn.")
    return affected


def _validate_adjustment_input(data, official: dict[str, object], section_code: str, room_code: str, slot_code: str, affected: list[dict[str, object]]) -> None:
    section, room, slot = data.course_sections.get(section_code), data.rooms.get(room_code), data.time_slots.get(slot_code)
    if section is None or room is None or slot is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần, phòng hoặc khung giờ.")
    if not room.available or room.room_type != section.required_room_type or room.capacity < section.scheduling_student_count:
        raise HTTPException(status_code=422, detail="Phòng không phù hợp với loại lớp hoặc sĩ số.")
    if not slot.active or section.course_type not in slot.supports_course_types or slot.duration != section.periods_per_session:
        raise HTTPException(status_code=422, detail="Khung giờ không phù hợp với loại lớp hoặc số tiết.")
    if (room_code, slot_code) in {(item.room_code, item.slot_code) for item in data.room_unavailable_slots}:
        raise HTTPException(status_code=422, detail="Phòng không sử dụng được tại khung giờ đã chọn.")
    fixed = {(item.lecturer_code, item.slot_code) for item in data.lecturer_time_preferences if item.mandatory}
    if (section.lecturer_code, slot_code) in fixed:
        raise HTTPException(status_code=422, detail="Khung giờ vi phạm ràng buộc cố định đã xác nhận của giảng viên.")
    for occurrence in affected:
        occurrence_date = date.fromisoformat(str(occurrence["date"]))
        if not section.start_date <= occurrence_date <= section.end_date:
            raise HTTPException(status_code=422, detail="Buổi điều chỉnh nằm ngoài khoảng ngày hiệu lực của lớp học phần.")
        if slot.day_of_week != occurrence_date.isoweekday() + 1:
            raise HTTPException(status_code=422, detail="Khung giờ được chọn không thuộc đúng thứ của các buổi trong phạm vi điều chỉnh.")


def _validate_effective_occurrence_conflicts(data, official: dict[str, object]) -> None:
    occurrences = list(official.get("occurrences", []))
    for index, first in enumerate(occurrences):
        first_slot = data.time_slots[str(first["slot_code"])]
        first_section = data.course_sections[str(first["section_code"])]
        for second in occurrences[index + 1 :]:
            if first.get("date") != second.get("date"):
                continue
            second_slot = data.time_slots[str(second["slot_code"])]
            if not _periods_overlap(first_slot, second_slot):
                continue
            second_section = data.course_sections[str(second["section_code"])]
            if first.get("room_code") == second.get("room_code") or first_section.lecturer_code == second_section.lecturer_code:
                raise HTTPException(status_code=422, detail="Thay đổi tạo xung đột phòng hoặc giảng viên với một buổi học khác.")


@router.get("/runs/{run_code}/export.csv")
def export_run_csv(
    run_code: str,
    lecturer_code: str | None = Query(default=None),
    room_code: str | None = Query(default=None),
    section_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> StreamingResponse:
    run = read_run(run_code)
    stream = StringIO()
    fields, rows = _export_rows(run, lecturer_code=lecturer_code, room_code=room_code, section_code=section_code, date_from=date_from, date_to=date_to)
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return StreamingResponse(iter(["\ufeff" + stream.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{_export_filename(run_code, "csv", _payload_batch_display_name(run))}"'})


@router.get("/runs/{run_code}/export.xlsx")
def export_run_xlsx(
    run_code: str,
    lecturer_code: str | None = Query(default=None),
    room_code: str | None = Query(default=None),
    section_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> StreamingResponse:
    run = read_run(run_code)
    fields, export_rows = _export_rows(run, lecturer_code=lecturer_code, room_code=room_code, section_code=section_code, date_from=date_from, date_to=date_to)
    rows = [fields, *[[str(item.get(field, "")) for field in fields] for item in export_rows]]
    output = BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Thoi khoa bieu" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        sheet_rows = "".join(f'<row r="{row_index}">' + "".join(f'<c r="{_excel_column(column_index)}{row_index}" t="inlineStr"><is><t>{escape(value)}</t></is></c>' for column_index, value in enumerate(row, start=1)) + "</row>" for row_index, row in enumerate(rows, start=1))
        archive.writestr("xl/worksheets/sheet1.xml", f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet_rows}</sheetData></worksheet>')
    return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{_export_filename(run_code, "xlsx", _payload_batch_display_name(run))}"'})


@router.get("/official-timetables/{official_code}/export.csv")
def export_official_csv(
    official_code: str,
    lecturer_code: str | None = Query(default=None),
    room_code: str | None = Query(default=None),
    section_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> StreamingResponse:
    official = read_official_timetable(official_code)
    stream = StringIO()
    fields, rows = _export_rows(official, lecturer_code=lecturer_code, room_code=room_code, section_code=section_code, date_from=date_from, date_to=date_to)
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return StreamingResponse(iter(["\ufeff" + stream.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{_export_filename(official_code, "csv", _payload_batch_display_name(official))}"'})


@router.get("/official-timetables/{official_code}/export.xlsx")
def export_official_xlsx(
    official_code: str,
    lecturer_code: str | None = Query(default=None),
    room_code: str | None = Query(default=None),
    section_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> StreamingResponse:
    official = read_official_timetable(official_code)
    fields, export_rows = _export_rows(official, lecturer_code=lecturer_code, room_code=room_code, section_code=section_code, date_from=date_from, date_to=date_to)
    rows = [fields, *[[str(item.get(field, "")) for field in fields] for item in export_rows]]
    output = BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Thoi khoa bieu" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        sheet_rows = "".join(f'<row r="{row_index}">' + "".join(f'<c r="{_excel_column(column_index)}{row_index}" t="inlineStr"><is><t>{escape(value)}</t></is></c>' for column_index, value in enumerate(row, start=1)) + "</row>" for row_index, row in enumerate(rows, start=1))
        archive.writestr("xl/worksheets/sheet1.xml", f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet_rows}</sheetData></worksheet>')
    return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{_export_filename(official_code, "xlsx", _payload_batch_display_name(official))}"'})


def _excel_column(index: int) -> str:
    label = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        label = chr(65 + remainder) + label
    return label


def _export_filename(code: str, extension: str, display_name: str | None = None) -> str:
    label = str(display_name or "").strip() or code
    transliterated = label.replace("đ", "d").replace("Đ", "D")
    ascii_label = unicodedata.normalize("NFKD", transliterated).encode("ascii", "ignore").decode("ascii")
    safe_label = "".join("-" if character in '<>:"/\\|?*' else character for character in ascii_label).strip(" .") or code
    return f"{safe_label}-{code}-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}.{extension}"


def _payload_batch_display_name(payload: dict[str, object]) -> str:
    label = str(payload.get("batch_display_name") or "").strip()
    if label:
        return label
    batch_code = str(payload.get("batch_code") or "").strip()
    if not batch_code:
        return ""
    try:
        return str(batch_summary(batch_code).get("display_name") or batch_code)
    except HTTPException:
        return batch_code


def _export_rows(
    run: dict[str, object],
    *,
    lecturer_code: str | None = None,
    room_code: str | None = None,
    section_code: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[str], list[dict[str, object]]]:
    """Export the effective dated timetable, including one-session changes."""
    fields = ["date", "academic_week", "status", "section_code", "course_code", "course_name", "lecturer_code", "lecturer_name", "room_code", "slot_code", "day_of_week", "start_period", "end_period", "course_type", "scheduling_student_count"]
    assignments = {str(item["section_code"]): item for item in run.get("assignments", [])}
    occurrences = run.get("occurrences", [])
    if occurrences:
        rows: list[dict[str, object]] = []
        for occurrence in occurrences:
            assignment = assignments.get(str(occurrence["section_code"]), {})
            combined = {**assignment, **occurrence}
            row = {field: combined.get(field, "") for field in fields}
            if _export_row_matches(row, lecturer_code, room_code, section_code, date_from, date_to):
                rows.append(row)
        return fields, sorted(rows, key=lambda item: (str(item.get("date", "")), str(item.get("section_code", ""))))
    rows = [{field: item.get(field, "") for field in fields} for item in run.get("assignments", [])]
    return fields, [row for row in rows if _export_row_matches(row, lecturer_code, room_code, section_code, date_from, date_to)]


def _export_row_matches(
    row: dict[str, object],
    lecturer_code: str | None,
    room_code: str | None,
    section_code: str | None,
    date_from: date | None,
    date_to: date | None,
) -> bool:
    if lecturer_code and str(row.get("lecturer_code") or "") != lecturer_code:
        return False
    if room_code and str(row.get("room_code") or "") != room_code:
        return False
    if section_code and str(row.get("section_code") or "") != section_code:
        return False
    if date_from or date_to:
        value = str(row.get("date") or "")
        if not value:
            return False
        try:
            row_date = date.fromisoformat(value)
        except ValueError:
            return False
        if date_from and row_date < date_from:
            return False
        if date_to and row_date > date_to:
            return False
    return True


def _slots_overlap(first: object, second: object) -> bool:
    return first.day_of_week == second.day_of_week and first.start_period <= second.end_period and second.start_period <= first.end_period  # type: ignore[attr-defined]


def _periods_overlap(first: object, second: object) -> bool:
    return first.start_period <= second.end_period and second.start_period <= first.end_period  # type: ignore[attr-defined]
