from __future__ import annotations

import csv
import zipfile
from datetime import date, datetime, timezone
from html import escape
from io import StringIO
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.algorithms.genetic.simple_ga import GeneticAlgorithmConfig, run_simple_genetic_algorithm
from backend.app.algorithms.genetic.soft_constraints import SoftConstraintWeights
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.scheduling.calendar_expansion import expand_base_assignments_to_occurrences
from backend.app.services.runtime_store import batch_directory, create_run, list_runs, persist_change_log, persist_ga_run, read_run, write_run


router = APIRouter(prefix="/api/ga", tags=["ga"])


class SoftWeightsRequest(BaseModel):
    lecturer_preferences: float = Field(default=10.0, ge=0)
    room_capacity_waste: float = Field(default=1.0, ge=0)
    large_room_small_class: float = Field(default=25.0, ge=0)
    schedule_gaps: float = Field(default=4.0, ge=0)
    scattered_days: float = Field(default=8.0, ge=0)
    consecutive_sessions: float = Field(default=6.0, ge=0)
    evening_weekend_avoidance: float = Field(default=5.0, ge=0)


class GaRunRequest(BaseModel):
    batch_code: str | None = None
    data_dir: str | None = None
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
    data_dir = batch_directory(request.batch_code) if request.batch_code else Path(request.data_dir or "data/samples/small")
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
    if request.batch_code:
        response["batch_code"] = request.batch_code
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
    """Change one dated session without altering its weekly base assignment."""
    run = read_run(run_code)
    data_result = validate_sample_dataset(batch_directory(str(run.get("batch_code", ""))))
    if not data_result.is_valid or data_result.data is None:
        raise HTTPException(status_code=422, detail="Không thể kiểm tra bộ dữ liệu của lần chạy.")
    data = data_result.data
    section = data.course_sections.get(request.section_code)
    room, slot = data.rooms.get(request.room_code), data.time_slots.get(request.slot_code)
    occurrences = list(run.get("occurrences", []))
    target = next((item for item in occurrences if item.get("section_code") == request.section_code and item.get("date") == request.occurrence_date.isoformat()), None)
    calendar_date = data.academic_calendar_dates.get(request.new_date)
    if section is None or target is None or room is None or slot is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy buổi học, phòng hoặc khung giờ.")
    if calendar_date is None or not calendar_date.is_teaching_day or calendar_date.is_holiday or slot.day_of_week != request.new_date.isoweekday() + 1:
        raise HTTPException(status_code=422, detail="Ngày hoặc khung giờ mới không hợp lệ trong lịch học kỳ.")
    if not room.available or room.room_type != section.required_room_type or room.capacity < section.scheduling_student_count:
        raise HTTPException(status_code=422, detail="Phòng không phù hợp với loại lớp hoặc sĩ số.")
    if not slot.active or section.course_type not in slot.supports_course_types or slot.duration != section.periods_per_session:
        raise HTTPException(status_code=422, detail="Khung giờ không phù hợp với loại lớp hoặc số tiết.")
    if (room.room_code, slot.slot_code) in {(item.room_code, item.slot_code) for item in data.room_unavailable_slots}:
        raise HTTPException(status_code=422, detail="Phòng không sử dụng được tại khung giờ đã chọn.")
    for item in occurrences:
        if item is target or item.get("date") != request.new_date.isoformat():
            continue
        other_slot = data.time_slots[str(item["slot_code"])]
        other_section = data.course_sections[str(item["section_code"])]
        if _periods_overlap(slot, other_slot) and (item["room_code"] == room.room_code or other_section.lecturer_code == section.lecturer_code):
            raise HTTPException(status_code=422, detail="Thay đổi tạo xung đột phòng hoặc giảng viên với một buổi học khác.")
    if any(item is not target and item.get("section_code") == request.section_code and item.get("date") == request.new_date.isoformat() for item in occurrences):
        raise HTTPException(status_code=422, detail="Lớp học phần đã có một buổi khác vào ngày mới.")

    previous = {key: target.get(key) for key in ("date", "room_code", "slot_code", "academic_week", "status")}
    target.update({"date": request.new_date.isoformat(), "room_code": room.room_code, "slot_code": slot.slot_code, "academic_week": calendar_date.academic_week, "status": "EXCEPTION"})
    current = {key: target.get(key) for key in previous}
    history = list(run.get("change_history", []))
    history.append({"section_code": request.section_code, "occurrence_date": request.occurrence_date.isoformat(), "previous": previous, "current": current, "reason": request.reason.strip(), "changed_at": datetime.now(timezone.utc).isoformat(), "scope": "ONE_OCCURRENCE"})
    run["occurrences"], run["change_history"] = occurrences, history
    write_run(run_code, run)
    persist_change_log(run_code, request.section_code, previous, current, scope="ONE_OCCURRENCE", reason=request.reason.strip())
    return {"message": "Đã cập nhật một buổi học và không phát hiện xung đột.", "run": run}


@router.put("/runs/{run_code}/assignments")
def adjust_assignment(run_code: str, request: AdjustmentRequest) -> dict[str, object]:
    run = read_run(run_code)
    batch_code = str(run.get("batch_code", ""))
    data_result = validate_sample_dataset(batch_directory(batch_code))
    if not data_result.is_valid or data_result.data is None:
        raise HTTPException(status_code=422, detail="Không thể kiểm tra bộ dữ liệu của lần chạy.")
    data = data_result.data
    if request.room_code not in data.rooms or request.slot_code not in data.time_slots or request.section_code not in data.course_sections:
        raise HTTPException(status_code=422, detail="Phòng, khung giờ hoặc lớp học phần không tồn tại.")
    section = data.course_sections[request.section_code]
    room = data.rooms[request.room_code]
    slot = data.time_slots[request.slot_code]
    if room.room_type != section.required_room_type or room.capacity < section.scheduling_student_count:
        raise HTTPException(status_code=422, detail="Phòng không phù hợp với loại lớp hoặc sĩ số.")
    assignments = list(run.get("assignments", []))
    target = next((item for item in assignments if item["section_code"] == request.section_code), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần trong kết quả.")
    for item in assignments:
        if item is target:
            continue
        other_slot = data.time_slots[str(item["slot_code"])]
        overlaps = slot.day_of_week == other_slot.day_of_week and slot.start_period <= other_slot.end_period and other_slot.start_period <= slot.end_period
        if overlaps and (item["room_code"] == request.room_code or item["lecturer_code"] == section.lecturer_code):
            raise HTTPException(status_code=422, detail="Thay đổi tạo xung đột phòng hoặc giảng viên với một lớp khác.")
    previous = {key: target[key] for key in ("room_code", "slot_code", "day_of_week", "start_period", "end_period")}
    target.update({"room_code": request.room_code, "slot_code": request.slot_code, "day_of_week": slot.day_of_week, "start_period": slot.start_period, "end_period": slot.end_period})
    history = list(run.get("change_history", []))
    history.append({"section_code": request.section_code, "previous": previous, "current": {key: target[key] for key in previous}, "changed_at": datetime.now(timezone.utc).isoformat(), "scope": "BASE_WEEKLY_SCHEDULE"})
    run["change_history"] = history
    write_run(run_code, run)
    persist_change_log(run_code, request.section_code, previous, {key: target[key] for key in previous})
    return {"message": "Đã cập nhật lịch và không phát hiện xung đột.", "run": run}


@router.get("/runs/{run_code}/export.csv")
def export_run_csv(run_code: str) -> StreamingResponse:
    run = read_run(run_code)
    stream = StringIO()
    fields, rows = _export_rows(run)
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return StreamingResponse(iter(["\ufeff" + stream.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{run_code}.csv"'})


@router.get("/runs/{run_code}/export.xlsx")
def export_run_xlsx(run_code: str) -> StreamingResponse:
    run = read_run(run_code)
    fields, export_rows = _export_rows(run)
    rows = [fields, *[[str(item.get(field, "")) for field in fields] for item in export_rows]]
    output = BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Thoi khoa bieu" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        sheet_rows = "".join(f'<row r="{row_index}">' + "".join(f'<c r="{_excel_column(column_index)}{row_index}" t="inlineStr"><is><t>{escape(value)}</t></is></c>' for column_index, value in enumerate(row, start=1)) + "</row>" for row_index, row in enumerate(rows, start=1))
        archive.writestr("xl/worksheets/sheet1.xml", f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet_rows}</sheetData></worksheet>')
    return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{run_code}.xlsx"'})


def _excel_column(index: int) -> str:
    label = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        label = chr(65 + remainder) + label
    return label


def _export_rows(run: dict[str, object]) -> tuple[list[str], list[dict[str, object]]]:
    """Export the effective dated timetable, including one-session changes."""
    fields = ["date", "academic_week", "status", "section_code", "course_code", "course_name", "lecturer_code", "lecturer_name", "room_code", "slot_code", "day_of_week", "start_period", "end_period", "course_type", "scheduling_student_count"]
    assignments = {str(item["section_code"]): item for item in run.get("assignments", [])}
    occurrences = run.get("occurrences", [])
    if occurrences:
        rows: list[dict[str, object]] = []
        for occurrence in occurrences:
            assignment = assignments.get(str(occurrence["section_code"]), {})
            combined = {**assignment, **occurrence}
            rows.append({field: combined.get(field, "") for field in fields})
        return fields, sorted(rows, key=lambda item: (str(item.get("date", "")), str(item.get("section_code", ""))))
    return fields, [{field: item.get(field, "") for field in fields} for item in run.get("assignments", [])]


def _slots_overlap(first: object, second: object) -> bool:
    return first.day_of_week == second.day_of_week and first.start_period <= second.end_period and second.start_period <= first.end_period  # type: ignore[attr-defined]


def _periods_overlap(first: object, second: object) -> bool:
    return first.start_period <= second.end_period and second.start_period <= first.end_period  # type: ignore[attr-defined]
