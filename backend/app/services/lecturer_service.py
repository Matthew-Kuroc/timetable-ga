from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select

from backend.app.db.models import OfficialTimetableModel, TimeSlotModel
from backend.app.db.session import get_session_local


def personal_timetable(lecturer_code: str, academic_week: int | None) -> dict[str, Any]:
    official = _current_official_payload()
    if official is None:
        return _empty_result(lecturer_code, academic_week)

    assignments = [
        dict(item)
        for item in official.get("assignments", [])
        if str(item.get("lecturer_code")) == lecturer_code
    ]
    assignments_by_section = {
        str(item["section_code"]): item for item in assignments
    }
    slot_details = _slot_details(
        {
            str(item.get("slot_code"))
            for item in official.get("occurrences", [])
            if item.get("slot_code")
        }
    )
    occurrences = []
    for item in official.get("occurrences", []):
        section_code = str(item.get("section_code") or "")
        assignment = assignments_by_section.get(section_code)
        if assignment is None:
            continue
        if academic_week is not None and int(item.get("academic_week") or 0) != academic_week:
            continue
        combined = {**assignment, **dict(item)}
        current_slot = slot_details.get(str(item.get("slot_code") or ""))
        if current_slot is not None:
            combined.update(
                {
                    "start_period": current_slot.start_period,
                    "end_period": current_slot.end_period,
                }
            )
        if item.get("date"):
            combined["day_of_week"] = date.fromisoformat(str(item["date"])).isoweekday() + 1
        occurrences.append(combined)
    occurrences.sort(key=lambda item: (str(item.get("date") or ""), int(item.get("start_period") or 0)))
    course_sections = sorted(
        assignments,
        key=lambda item: str(item.get("section_code") or ""),
    )
    return {
        "official_code": official.get("official_code"),
        "academic_week": academic_week,
        "lecturer_code": lecturer_code,
        "lecturer_name": assignments[0].get("lecturer_name") if assignments else "",
        "occurrences": occurrences,
        "course_sections": course_sections,
    }


def assigned_course_sections(lecturer_code: str) -> dict[str, Any]:
    result = personal_timetable(lecturer_code, None)
    return {
        "official_code": result["official_code"],
        "lecturer_code": lecturer_code,
        "lecturer_name": result["lecturer_name"],
        "course_sections": result["course_sections"],
    }


def _current_official_payload() -> dict[str, Any] | None:
    with get_session_local()() as session:
        model = session.scalar(
            select(OfficialTimetableModel)
            .where(OfficialTimetableModel.status == "PUBLISHED")
            .order_by(OfficialTimetableModel.published_at.desc())
            .limit(1)
        )
        return dict(model.payload) if model is not None else None


def _slot_details(slot_codes: set[str]) -> dict[str, TimeSlotModel]:
    if not slot_codes:
        return {}
    with get_session_local()() as session:
        models = session.scalars(
            select(TimeSlotModel).where(TimeSlotModel.slot_code.in_(slot_codes))
        ).all()
        return {item.slot_code: item for item in models}


def _empty_result(lecturer_code: str, academic_week: int | None) -> dict[str, Any]:
    return {
        "official_code": None,
        "academic_week": academic_week,
        "lecturer_code": lecturer_code,
        "lecturer_name": "",
        "occurrences": [],
        "course_sections": [],
    }
