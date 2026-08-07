from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pytest


fastapi = pytest.importorskip("fastapi")
pytest.importorskip("pydantic")

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.services import runtime_store


REPO_ROOT = Path(__file__).resolve().parents[2]


def _published_official(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", tmp_path / "runtime" / "batches")
    monkeypatch.setattr(runtime_store, "RUN_ROOT", tmp_path / "runtime" / "runs")
    source = tmp_path / "source"
    shutil.copytree(REPO_ROOT / "data" / "samples" / "small", source)
    batch = runtime_store.create_confirmed_batch(source)
    client = TestClient(create_app())
    run = client.post("/api/ga/runs/preview", json={"batch_code": batch["batch_code"], "population_size": 12, "generations": 4, "seed": 42}).json()
    official_response = client.post(f"/api/ga/runs/{run['run_code']}/publish", json={"note": "Kiểm thử lịch chính thức"})
    assert official_response.status_code == 200
    return client, run, official_response.json()


def test_publish_makes_an_independent_official_timetable(tmp_path, monkeypatch) -> None:
    client, run, official = _published_official(tmp_path, monkeypatch)

    listing = client.get("/api/ga/official-timetables")

    assert listing.status_code == 200
    assert listing.json()["official_timetables"][0]["official_code"] == official["official_code"]
    assert official["source_run_code"] == run["run_code"]
    rejected = client.put(
        f"/api/ga/runs/{run['run_code']}/occurrences",
        json={"section_code": "missing", "occurrence_date": "2026-09-01", "new_date": "2026-09-01", "room_code": "missing", "slot_code": "missing", "reason": "Không được sửa run"},
    )
    assert rejected.status_code == 409


def test_date_range_adjustment_and_segment_are_recorded(tmp_path, monkeypatch) -> None:
    client, _run, official = _published_official(tmp_path, monkeypatch)
    first = official["occurrences"][0]
    same_section = [item for item in official["occurrences"] if item["section_code"] == first["section_code"]]
    start, end = same_section[0]["date"], same_section[-1]["date"]

    adjustment = client.put(
        f"/api/ga/official-timetables/{official['official_code']}/adjustments",
        json={"section_code": first["section_code"], "scope": "DATE_RANGE", "effective_start_date": start, "effective_end_date": end, "room_code": first["room_code"], "slot_code": first["slot_code"], "reason": "Kiểm thử phạm vi ngày"},
    )
    assert adjustment.status_code == 200
    assert adjustment.json()["official"]["change_history"][-1]["scope"] == "DATE_RANGE"

    segment = client.post(
        f"/api/ga/official-timetables/{official['official_code']}/segments",
        json={"section_code": first["section_code"], "effective_start_date": start, "effective_end_date": end, "room_code": first["room_code"], "slot_code": first["slot_code"], "reason": "Kiểm thử phân đoạn"},
    )
    assert segment.status_code == 200
    assert segment.json()["official"]["segments"][0]["section_code"] == first["section_code"]


def test_makeup_session_is_added_only_after_conflict_check(tmp_path, monkeypatch) -> None:
    client, _run, official = _published_official(tmp_path, monkeypatch)
    first = official["occurrences"][0]
    batch_dir = runtime_store.batch_directory(official["batch_code"])
    from backend.app.importing.csv_validator import validate_sample_dataset

    data = validate_sample_dataset(batch_dir).data
    assert data is not None
    section = data.course_sections[first["section_code"]]
    makeup_date = room_code = slot_code = None
    for calendar_date in data.academic_calendar_dates.values():
        if not calendar_date.is_teaching_day or calendar_date.is_holiday or not section.start_date <= calendar_date.date <= section.end_date:
            continue
        for candidate_slot in data.time_slots.values():
            if candidate_slot.day_of_week != calendar_date.day_of_week or not candidate_slot.active or section.course_type not in candidate_slot.supports_course_types or candidate_slot.duration != section.periods_per_session:
                continue
            for candidate_room in data.rooms.values():
                if not candidate_room.available or candidate_room.room_type != section.required_room_type or candidate_room.capacity < section.scheduling_student_count:
                    continue
                conflicts = [item for item in official["occurrences"] if item["date"] == calendar_date.date.isoformat()]
                if any(
                    candidate_slot.start_period <= data.time_slots[item["slot_code"]].end_period
                    and data.time_slots[item["slot_code"]].start_period <= candidate_slot.end_period
                    and (item["room_code"] == candidate_room.room_code or data.course_sections[item["section_code"]].lecturer_code == section.lecturer_code)
                    for item in conflicts
                ):
                    continue
                makeup_date, room_code, slot_code = calendar_date.date, candidate_room.room_code, candidate_slot.slot_code
                break
            if makeup_date:
                break
        if makeup_date:
            break
    assert makeup_date and room_code and slot_code

    response = client.post(
        f"/api/ga/official-timetables/{official['official_code']}/makeups",
        json={"section_code": first["section_code"], "makeup_date": makeup_date.isoformat(), "room_code": room_code, "slot_code": slot_code, "reason": "Bù buổi nghỉ lễ"},
    )

    assert response.status_code == 200
    assert response.json()["official"]["makeup_sessions"][0]["status"] == "MAKEUP"
