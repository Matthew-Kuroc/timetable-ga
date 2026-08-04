from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select, text

from backend.app.importing.import_preview import REQUIRED_DATASET_FILES
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.db.session import get_session_local
from backend.app.db.models import (
    AcademicCalendarDateModel,
    AcademicTermModel,
    CourseSectionModel,
    GaRunModel,
    ImportBatchModel,
    LecturerModel,
    RoomModel,
    ScheduleAssignmentModel,
    ScheduleOccurrenceModel,
    TimeSlotModel,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_ROOT = REPO_ROOT / "data" / "runtime"
BATCH_ROOT = RUNTIME_ROOT / "batches"
RUN_ROOT = RUNTIME_ROOT / "runs"


def create_confirmed_batch(
    source_directory: Path,
    *,
    display_name: str = "",
    semester: str = "",
    academic_year: str = "",
    note: str = "",
) -> dict[str, object]:
    validation = validate_sample_dataset(source_directory)
    if not validation.is_valid:
        raise HTTPException(status_code=422, detail={"message": "Bộ CSV chưa hợp lệ.", "errors": errors_payload(validation)})
    batch_code = f"BATCH-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid4().hex[:6].upper()}"
    target = BATCH_ROOT / batch_code
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_directory, target)
    confirmed_at = _now()
    manifest = {
        "batch_code": batch_code,
        "display_name": display_name.strip() or "Bộ dữ liệu đã xác nhận",
        "semester": semester.strip(),
        "academic_year": academic_year.strip(),
        "version_number": 1,
        "status": "CONFIRMED",
        "note": note.strip(),
        "created_at": confirmed_at,
        "confirmed_at": confirmed_at,
        "files": list(REQUIRED_DATASET_FILES),
    }
    _write_json(target / "manifest.json", manifest)
    _persist_snapshot(manifest, target)
    return batch_summary(batch_code)


def list_batches() -> list[dict[str, object]]:
    if not BATCH_ROOT.exists():
        return []
    return sorted((batch_summary(path.name) for path in BATCH_ROOT.iterdir() if path.is_dir() and (path / "manifest.json").exists()), key=lambda item: str(item["created_at"]), reverse=True)


def batch_directory(batch_code: str) -> Path:
    path = BATCH_ROOT / batch_code
    if not path.is_dir() or not (path / "manifest.json").exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ dữ liệu đã xác nhận.")
    return path


def batch_summary(batch_code: str) -> dict[str, object]:
    directory = batch_directory(batch_code)
    manifest = _read_json(directory / "manifest.json")
    validation = validate_sample_dataset(directory)
    return {
        **manifest,
        "display_name": str(manifest.get("display_name") or "Bộ dữ liệu đã xác nhận"),
        "semester": str(manifest.get("semester") or ""),
        "academic_year": str(manifest.get("academic_year") or ""),
        "version_number": int(manifest.get("version_number") or 1),
        "confirmed_at": str(manifest.get("confirmed_at") or manifest.get("created_at") or ""),
        "valid": validation.is_valid,
        "file_count": len(REQUIRED_DATASET_FILES),
        "section_count": len(validation.data.course_sections) if validation.data else 0,
    }


def read_batch_file(batch_code: str, file_name: str) -> dict[str, object]:
    path = _csv_path(batch_code, file_name)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = [{key: value or "" for key, value in row.items()} for row in reader]
        return {"file": file_name, "headers": list(reader.fieldnames or []), "rows": rows, "row_count": len(rows)}


def update_batch_file(batch_code: str, file_name: str, rows: list[dict[str, str]]) -> dict[str, object]:
    directory = batch_directory(batch_code)
    headers = read_batch_file(batch_code, file_name)["headers"]
    staged = directory.parent / f".staging-{uuid4().hex}"
    shutil.copytree(directory, staged)
    _write_csv(staged / file_name, headers, rows)
    validation = validate_sample_dataset(staged)
    if not validation.is_valid:
        shutil.rmtree(staged, ignore_errors=True)
        raise HTTPException(status_code=422, detail={"message": "Không thể lưu vì bộ CSV có dữ liệu không hợp lệ.", "errors": errors_payload(validation)})
    manifest = _read_json(staged / "manifest.json")
    new_batch_code = f"BATCH-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid4().hex[:6].upper()}"
    confirmed_at = _now()
    manifest.update({
        "batch_code": new_batch_code,
        "parent_batch_code": batch_code,
        "version_number": int(manifest.get("version_number") or 1) + 1,
        "created_at": confirmed_at,
        "confirmed_at": confirmed_at,
        "note": f"Phiên bản chỉnh sửa từ {batch_code}",
    })
    _write_json(staged / "manifest.json", manifest)
    target = directory.parent / new_batch_code
    staged.rename(target)
    _persist_snapshot(manifest, target)
    return {"file": file_name, "row_count": len(rows), "batch": batch_summary(new_batch_code), "message": "Đã tạo phiên bản dữ liệu mới. Bộ dữ liệu cũ được giữ nguyên."}


def create_run(payload: dict[str, object]) -> str:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    run_code = f"RUN-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid4().hex[:6].upper()}"
    payload["run_code"] = run_code
    payload["created_at"] = _now()
    _write_json(RUN_ROOT / f"{run_code}.json", payload)
    return run_code


def list_runs(limit: int = 20) -> list[dict[str, object]]:
    """Return compact, newest-first run records without loading full schedules."""
    if not RUN_ROOT.exists():
        return []

    summaries: list[dict[str, object]] = []
    for path in RUN_ROOT.glob("RUN-*.json"):
        payload = _read_json(path)
        evaluation = payload.get("evaluation") if isinstance(payload.get("evaluation"), dict) else {}
        assignments = payload.get("assignments") if isinstance(payload.get("assignments"), list) else []
        summaries.append(
            {
                "run_code": payload.get("run_code", path.stem),
                "batch_code": payload.get("batch_code"),
                "status": payload.get("status"),
                "created_at": payload.get("created_at"),
                "generation_count": payload.get("generation_count", 0),
                "seed": payload.get("seed"),
                "hard_violation_count": evaluation.get("hard_violation_count", 0),
                "soft_cost": evaluation.get("soft_cost"),
                "assignment_count": len(assignments),
            }
        )
    return sorted(summaries, key=lambda item: str(item.get("created_at", "")), reverse=True)[:limit]


def read_run(run_code: str) -> dict[str, object]:
    path = RUN_ROOT / f"{run_code}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả chạy GA.")
    return _read_json(path)


def write_run(run_code: str, payload: dict[str, object]) -> None:
    _write_json(RUN_ROOT / f"{run_code}.json", payload)


def persist_change_log(
    run_code: str,
    section_code: str,
    previous: dict[str, object],
    current: dict[str, object],
    *,
    scope: str = "BASE_WEEKLY_SCHEDULE",
    reason: str | None = None,
) -> None:
    try:
        with get_session_local()() as session:
            session.execute(text("""insert into schedule_change_logs (run_code, section_code, scope, previous_value, current_value, reason, changed_by, changed_at) values (:run_code, :section_code, :scope, cast(:previous as json), cast(:current as json), :reason, 'training_office', now())"""), {"run_code": run_code, "section_code": section_code, "scope": scope, "previous": json.dumps(previous), "current": json.dumps(current), "reason": reason})
            session.commit()
    except Exception:
        return


def persist_ga_run(batch_code: str, payload: dict[str, object], input_data: object) -> None:
    """Persist normalized input and one immutable GA result for later queries."""
    try:
        with get_session_local()() as session:
            configuration = payload.get("configuration") if isinstance(payload.get("configuration"), dict) else {}
            batch = session.scalar(select(ImportBatchModel).where(ImportBatchModel.batch_code == batch_code))
            if batch is None:
                batch = ImportBatchModel(batch_code=batch_code, display_name=batch_code, status="CONFIRMED", note="CSV snapshot")
                session.add(batch)
                session.flush()
            lecturers = {}
            for value in input_data.lecturers.values():
                model = session.scalar(select(LecturerModel).where(LecturerModel.lecturer_code == value.lecturer_code))
                if model is None:
                    model = LecturerModel(lecturer_code=value.lecturer_code, lecturer_name=value.lecturer_name)
                    session.add(model)
                model.lecturer_name, model.preferred_days, model.preferred_slots = value.lecturer_name, list(value.preferred_days), list(value.preferred_slots)
                model.undesired_days, model.undesired_slots = list(value.undesired_days), list(value.undesired_slots)
                model.max_days_per_week, model.max_consecutive_sessions = value.max_days_per_week, value.max_consecutive_sessions
                session.flush(); lecturers[value.lecturer_code] = model
            rooms = {}
            for value in input_data.rooms.values():
                model = session.scalar(select(RoomModel).where(RoomModel.room_code == value.room_code))
                if model is None:
                    model = RoomModel(room_code=value.room_code, room_name=value.room_name, capacity=value.capacity, room_type=value.room_type)
                    session.add(model)
                model.room_name, model.capacity, model.room_type, model.room_size_category, model.available = value.room_name, value.capacity, value.room_type, value.room_size_category, value.available
                session.flush(); rooms[value.room_code] = model
            slots = {}
            for value in input_data.time_slots.values():
                model = session.scalar(select(TimeSlotModel).where(TimeSlotModel.slot_code == value.slot_code))
                if model is None:
                    model = TimeSlotModel(slot_code=value.slot_code, day_of_week=value.day_of_week, start_period=value.start_period, end_period=value.end_period)
                    session.add(model)
                model.day_of_week, model.start_period, model.end_period = value.day_of_week, value.start_period, value.end_period
                model.supports_course_types, model.active = list(value.supports_course_types), value.active
                session.flush(); slots[value.slot_code] = model
            sections = {}
            for value in input_data.course_sections.values():
                model = session.scalar(select(CourseSectionModel).where(CourseSectionModel.import_batch_id == batch.id, CourseSectionModel.section_code == value.section_code))
                if model is None:
                    model = CourseSectionModel(import_batch_id=batch.id, section_code=value.section_code, lecturer_id=lecturers[value.lecturer_code].id, course_code=value.course_code, course_name=value.course_name, required_sessions=value.required_sessions, periods_per_session=value.periods_per_session, expected_students=value.expected_students, scheduling_student_count=value.scheduling_student_count, course_type=value.course_type, required_room_type=value.required_room_type, start_date=value.start_date, end_date=value.end_date)
                    session.add(model)
                model.lecturer_id, model.weekly_sessions, model.initial_registration_limit, model.approved_max_students = lecturers[value.lecturer_code].id, value.weekly_sessions, value.initial_registration_limit, value.approved_max_students
                session.flush(); sections[value.section_code] = model
            run = GaRunModel(
                run_code=str(payload["run_code"]),
                import_batch_id=batch.id,
                status=str(payload["status"]),
                population_size=int(configuration.get("population_size", 0)),
                generations=int(configuration.get("generations", payload.get("generation_count", 0))),
                mutation_rate=float(configuration["mutation_rate"]) if configuration.get("mutation_rate") is not None else None,
                crossover_rate=float(configuration["crossover_rate"]) if configuration.get("crossover_rate") is not None else None,
                seed=payload.get("seed"),
                best_fitness=float(payload["evaluation"]["total_cost"]),
                hard_violation_count=int(payload["evaluation"]["hard_violation_count"]),
                soft_cost=float(payload["evaluation"]["soft_cost"]),
                soft_breakdown=payload["evaluation"]["soft_breakdown"],
                finished_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            session.add(run); session.flush()
            assignment_models = {}
            for value in payload.get("assignments", []):
                model = ScheduleAssignmentModel(ga_run_id=run.id, course_section_id=sections[value["section_code"]].id, lecturer_id=lecturers[value["lecturer_code"]].id, room_id=rooms[value["room_code"]].id, time_slot_id=slots[value["slot_code"]].id, status="SCHEDULED")
                session.add(model); session.flush(); assignment_models[value["section_code"]] = model
            for value in payload.get("occurrences", []):
                assignment = assignment_models[value["section_code"]]
                session.add(ScheduleOccurrenceModel(schedule_assignment_id=assignment.id, course_section_id=sections[value["section_code"]].id, date=__import__("datetime").date.fromisoformat(value["date"]), academic_week=int(value["academic_week"]), room_id=rooms[value["room_code"]].id, time_slot_id=slots[value["slot_code"]].id, status=value["status"]))
            session.commit()
    except Exception:
        return


def errors_payload(validation: object) -> list[dict[str, object]]:
    return [error.__dict__ for error in validation.errors]  # type: ignore[attr-defined]


def _csv_path(batch_code: str, file_name: str) -> Path:
    if file_name not in REQUIRED_DATASET_FILES:
        raise HTTPException(status_code=404, detail="File không thuộc bộ CSV yêu cầu.")
    path = batch_directory(batch_code) / file_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file CSV.")
    return path


def _write_csv(path: Path, headers: object, rows: list[dict[str, str]]) -> None:
    fieldnames = list(headers)  # type: ignore[arg-type]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{field: str(row.get(field, "")) for field in fieldnames} for row in rows])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _persist_snapshot(manifest: dict[str, object], path: Path) -> None:
    try:
        with get_session_local()() as session:
            batch = session.scalar(select(ImportBatchModel).where(ImportBatchModel.batch_code == manifest["batch_code"]))
            if batch is None:
                session.add(ImportBatchModel(
                    batch_code=str(manifest["batch_code"]),
                    display_name=str(manifest.get("display_name") or manifest["batch_code"]),
                    semester=str(manifest.get("semester") or "") or None,
                    academic_year=str(manifest.get("academic_year") or "") or None,
                    version_number=int(manifest.get("version_number") or 1),
                    status="CONFIRMED",
                    note=str(manifest.get("note") or "") or None,
                    uploaded_at=_parse_timestamp(str(manifest.get("created_at") or _now())),
                    confirmed_at=_parse_timestamp(str(manifest.get("confirmed_at") or _now())),
                ))
            session.execute(text("""insert into dataset_snapshots (batch_code, parent_batch_code, snapshot_path, manifest, created_at) values (:batch_code, :parent_batch_code, :snapshot_path, cast(:manifest as json), now()) on conflict (batch_code) do nothing"""), {"batch_code": manifest["batch_code"], "parent_batch_code": manifest.get("parent_batch_code"), "snapshot_path": str(path), "manifest": json.dumps(manifest)})
            session.commit()
    except Exception:
        return


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
