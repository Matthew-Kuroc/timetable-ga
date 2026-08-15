from __future__ import annotations

import copy
import shutil
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import select

from backend.app.db.base import Base
from backend.app.db.models import (
    ScheduleChangeLogModel,
    ScheduleChangeRequestEventModel,
    ScheduleChangeRequestModel,
)
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.services import runtime_store
from backend.tests.auth_helpers import authenticated_client


REPO_ROOT = Path(__file__).resolve().parents[2]


def _published_schedule(tmp_path: Path, monkeypatch: Any) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", tmp_path / "runtime" / "batches")
    monkeypatch.setattr(runtime_store, "RUN_ROOT", tmp_path / "runtime" / "runs")
    source = tmp_path / "source"
    shutil.copytree(REPO_ROOT / "data" / "samples" / "small", source)
    batch = runtime_store.create_confirmed_batch(source)
    training = authenticated_client(UserRole.TRAINING_OFFICE)
    run_response = training.post(
        "/api/ga/runs/preview",
        json={
            "batch_code": batch["batch_code"],
            "population_size": 12,
            "generations": 4,
            "seed": 42,
        },
    )
    assert run_response.status_code == 200, run_response.text
    run = run_response.json()
    publish_response = training.post(
        f"/api/ga/runs/{run['run_code']}/publish",
        json={"note": "Công bố để kiểm thử yêu cầu điều chỉnh"},
    )
    assert publish_response.status_code == 200, publish_response.text
    return training, run, publish_response.json()


def _owner_client(official: dict[str, Any], occurrence: dict[str, Any], *, username: str = "lecturer-owner") -> Any:
    assignment = next(
        item for item in official["assignments"] if item["section_code"] == occurrence["section_code"]
    )
    return authenticated_client(
        UserRole.LECTURER,
        username=username,
        lecturer_code=assignment["lecturer_code"],
    )


def _submit_suspend(client: Any, official: dict[str, Any], occurrence: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        "/api/lecturer/change-requests",
        json={
            "official_code": official["official_code"],
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "request_type": "SUSPEND_ONE_OCCURRENCE",
            "reason": "Xin tạm ngưng buổi học vì có lịch công tác.",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["request"]


def _find_move_option(
    lecturer: Any,
    official: dict[str, Any],
    occurrence: dict[str, Any],
) -> tuple[str, str, str]:
    data = validate_sample_dataset(runtime_store.batch_directory(official["batch_code"])).data
    assert data is not None
    section = data.course_sections[occurrence["section_code"]]
    for calendar_date in sorted(data.academic_calendar_dates.values(), key=lambda item: item.date):
        if calendar_date.date.isoformat() == occurrence["date"]:
            continue
        if not calendar_date.is_teaching_day or calendar_date.is_holiday:
            continue
        if not section.start_date <= calendar_date.date <= section.end_date:
            continue
        response = lecturer.get(
            "/api/lecturer/change-requests/options",
            params={
                "official_code": official["official_code"],
                "section_code": occurrence["section_code"],
                "occurrence_date": occurrence["date"],
                "target_date": calendar_date.date.isoformat(),
            },
        )
        assert response.status_code == 200, response.text
        slots = response.json()["slots"]
        if slots:
            return calendar_date.date.isoformat(), slots[0]["slot_code"], slots[0]["rooms"][0]["room_code"]
    raise AssertionError("Dữ liệu kiểm thử phải có ít nhất một phương án chuyển buổi hợp lệ.")


def test_lecturer_ownership_visibility_cancel_and_pending_does_not_mutate_official(tmp_path, monkeypatch) -> None:
    training, _run, official = _published_schedule(tmp_path, monkeypatch)
    occurrence = official["occurrences"][0]
    owner = _owner_client(official, occurrence)
    before = copy.deepcopy(training.get(f"/api/ga/official-timetables/{official['official_code']}").json())

    submitted = _submit_suspend(owner, official, occurrence)

    assert submitted["status"] == "PENDING"
    assert submitted["events"][0]["event_type"] == "SUBMITTED"
    assert submitted["requester_display_name"]
    after_submit = training.get(f"/api/ga/official-timetables/{official['official_code']}").json()
    assert after_submit == before
    listing = owner.get("/api/lecturer/change-requests")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    other = authenticated_client(
        UserRole.LECTURER,
        username="lecturer-other",
        lecturer_code="GV-NOT-OWNER",
    )
    assert other.get(f"/api/lecturer/change-requests/{submitted['request_code']}").status_code == 404
    forbidden_create = other.post(
        "/api/lecturer/change-requests",
        json={
            "official_code": official["official_code"],
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "request_type": "SUSPEND_ONE_OCCURRENCE",
            "reason": "Không phải lớp được phân công.",
        },
    )
    assert forbidden_create.status_code == 403
    assert training.get("/api/lecturer/change-requests").status_code == 403
    assert owner.get("/api/training-office/change-requests").status_code == 403

    cancelled = owner.post(f"/api/lecturer/change-requests/{submitted['request_code']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["request"]["status"] == "CANCELLED"
    assert owner.post(f"/api/lecturer/change-requests/{submitted['request_code']}/cancel").status_code == 409
    assert training.get(f"/api/ga/official-timetables/{official['official_code']}").json() == before


def test_training_reject_requires_reason_and_never_changes_timetable(tmp_path, monkeypatch) -> None:
    training, _run, official = _published_schedule(tmp_path, monkeypatch)
    occurrence = official["occurrences"][0]
    owner = _owner_client(official, occurrence)
    request = _submit_suspend(owner, official, occurrence)
    before = copy.deepcopy(training.get(f"/api/ga/official-timetables/{official['official_code']}").json())

    missing_reason = training.post(
        f"/api/training-office/change-requests/{request['request_code']}/reject",
        json={"reason": "   "},
    )
    assert missing_reason.status_code == 422
    rejected = training.post(
        f"/api/training-office/change-requests/{request['request_code']}/reject",
        json={"reason": "Không thể bố trí kế hoạch học bù phù hợp."},
    )

    assert rejected.status_code == 200, rejected.text
    result = rejected.json()["request"]
    assert result["status"] == "REJECTED"
    assert result["review_note"] == "Không thể bố trí kế hoạch học bù phù hợp."
    assert [event["event_type"] for event in result["events"]] == ["SUBMITTED", "REJECTED"]
    assert training.get(f"/api/ga/official-timetables/{official['official_code']}").json() == before


def test_invalid_move_proposal_and_unconfigured_recurring_request_are_blocked(tmp_path, monkeypatch) -> None:
    _training, _run, official = _published_schedule(tmp_path, monkeypatch)
    occurrence = official["occurrences"][0]
    owner = _owner_client(official, occurrence)

    incomplete = owner.post(
        "/api/lecturer/change-requests",
        json={
            "official_code": official["official_code"],
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "request_type": "MOVE_ONE_OCCURRENCE",
            "reason": "Xin chuyển buổi nhưng chưa chọn đủ phương án.",
        },
    )
    assert incomplete.status_code == 422

    recurring = owner.post(
        "/api/lecturer/change-requests",
        json={
            "official_code": official["official_code"],
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "request_type": "MOVE_RECURRING_SCHEDULE",
            "reason": "Xin đổi lịch lặp.",
        },
    )
    assert recurring.status_code == 422
    assert "thời hạn" in recurring.json()["detail"]

    invalid_date = owner.post(
        "/api/lecturer/change-requests",
        json={
            "official_code": official["official_code"],
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "request_type": "MOVE_ONE_OCCURRENCE",
            "reason": "Xin chuyển vào ngày nghỉ.",
            "proposed_date": "2026-09-14",
            "proposed_slot_code": "MON_1_3",
            "proposed_room_code": occurrence["room_code"],
        },
    )
    assert invalid_date.status_code == 422
    conflicts = invalid_date.json()["detail"]["validation"]["hard_conflicts"]
    assert any(item["code"] == "INVALID_TEACHING_DATE" for item in conflicts)


def test_valid_move_is_validated_approved_and_applied_atomically_with_audit(tmp_path, monkeypatch) -> None:
    training, _run, official = _published_schedule(tmp_path, monkeypatch)
    occurrence = official["occurrences"][0]
    owner = _owner_client(official, occurrence)
    target_date, slot_code, room_code = _find_move_option(owner, official, occurrence)
    original_official = copy.deepcopy(training.get(f"/api/ga/official-timetables/{official['official_code']}").json())

    submitted_response = owner.post(
        "/api/lecturer/change-requests",
        json={
            "official_code": official["official_code"],
            "section_code": occurrence["section_code"],
            "occurrence_date": occurrence["date"],
            "request_type": "MOVE_ONE_OCCURRENCE",
            "reason": "Xin chuyển một buổi sang thời gian phù hợp.",
            "proposed_date": target_date,
            "proposed_slot_code": slot_code,
            "proposed_room_code": room_code,
        },
    )
    assert submitted_response.status_code == 200, submitted_response.text
    request_code = submitted_response.json()["request"]["request_code"]
    assert training.get(f"/api/ga/official-timetables/{official['official_code']}").json() == original_official

    validation_response = training.post(
        f"/api/training-office/change-requests/{request_code}/validate"
    )
    assert validation_response.status_code == 200, validation_response.text
    validation = validation_response.json()["validation"]
    assert validation["valid"] is True
    assert validation["hard_conflicts"] == []
    approved = training.post(
        f"/api/training-office/change-requests/{request_code}/approve",
        json={},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["request"]["status"] == "APPROVED"
    assert training.get(f"/api/ga/official-timetables/{official['official_code']}").json() == original_official

    applied = training.post(f"/api/training-office/change-requests/{request_code}/apply")

    assert applied.status_code == 200, applied.text
    result = applied.json()
    assert result["request"]["status"] == "APPLIED"
    moved = next(
        item
        for item in result["official"]["occurrences"]
        if item["section_code"] == occurrence["section_code"] and item["status"] == "MOVED"
    )
    assert moved["date"] == target_date
    assert moved["slot_code"] == slot_code
    assert moved["room_code"] == room_code
    assert result["official"]["version_number"] == 2
    assert result["official"]["change_history"][-1]["request_code"] == request_code
    assert [item["event_type"] for item in result["request"]["events"]] == [
        "SUBMITTED",
        "VALIDATED",
        "APPROVED",
        "APPLIED",
    ]

    with get_session_local()() as session:
        request_model = session.scalar(
            select(ScheduleChangeRequestModel).where(ScheduleChangeRequestModel.request_code == request_code)
        )
        assert request_model is not None and request_model.status == "APPLIED"
        change_log = session.scalar(
            select(ScheduleChangeLogModel).where(ScheduleChangeLogModel.request_id == request_model.id)
        )
        assert change_log is not None
        assert change_log.current_value["occurrence"]["status"] == "MOVED"
        events = session.scalars(
            select(ScheduleChangeRequestEventModel)
            .where(ScheduleChangeRequestEventModel.request_id == request_model.id)
            .order_by(ScheduleChangeRequestEventModel.id)
        ).all()
        assert [event.action for event in events] == ["SUBMITTED", "VALIDATED", "APPROVED", "APPLIED"]


def test_suspend_is_applied_only_after_approval_and_schema_has_audit_tables(tmp_path, monkeypatch) -> None:
    training, _run, official = _published_schedule(tmp_path, monkeypatch)
    occurrence = official["occurrences"][0]
    owner = _owner_client(official, occurrence)
    request = _submit_suspend(owner, official, occurrence)
    request_code = request["request_code"]

    premature = training.post(f"/api/training-office/change-requests/{request_code}/apply")
    assert premature.status_code == 409
    checked = training.post(f"/api/training-office/change-requests/{request_code}/validate")
    assert checked.status_code == 200
    assert checked.json()["validation"]["valid"] is True
    assert training.post(
        f"/api/training-office/change-requests/{request_code}/approve", json={}
    ).status_code == 200
    applied = training.post(f"/api/training-office/change-requests/{request_code}/apply")

    assert applied.status_code == 200, applied.text
    suspended = next(
        item
        for item in applied.json()["official"]["occurrences"]
        if item["section_code"] == occurrence["section_code"] and item["date"] == occurrence["date"]
    )
    assert suspended["status"] == "SUSPENDED"
    assert "schedule_change_requests" in Base.metadata.tables
    assert "schedule_change_request_events" in Base.metadata.tables
    assert "request_id" in Base.metadata.tables["schedule_change_logs"].columns

