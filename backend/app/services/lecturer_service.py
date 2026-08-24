from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import select

from backend.app.db.models import AcademicCalendarDateModel, CourseSectionModel, OfficialTimetableModel, TimeSlotModel
from backend.app.db.session import get_session_local


def personal_timetable(lecturer_code: str, academic_week: int | None, selected_date: date | None = None) -> dict[str, Any]:
    official = _current_official_payload()
    if official is None:
        return _empty_result(lecturer_code, academic_week, selected_date)

    week_start_date, week_end_date = _requested_week_bounds(academic_week, selected_date)
    if selected_date is not None:
        academic_week = _calendar_week_for_date(selected_date)
        if academic_week is None:
            matching_weeks = {
                int(item.get("academic_week"))
                for item in official.get("occurrences", [])
                if item.get("date") == selected_date.isoformat() and item.get("academic_week") is not None
            }
            academic_week = min(matching_weeks) if matching_weeks else None
        if academic_week is None:
            week_start_date = selected_date - timedelta(days=selected_date.weekday())
            week_end_date = week_start_date + timedelta(days=6)

    assignments = [
        dict(item)
        for item in official.get("assignments", [])
        if str(item.get("lecturer_code")) == lecturer_code
    ]
    assignments_by_section = {
        str(item["section_code"]): item for item in assignments
    }
    lecturer_section_codes = set(assignments_by_section)
    teaching_dates = sorted({
        str(item.get("date"))
        for item in official.get("occurrences", [])
        if str(item.get("section_code") or "") in lecturer_section_codes and item.get("date")
    })
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
        if (selected_date is not None and academic_week is None) or (academic_week is not None and int(item.get("academic_week") or 0) != academic_week):
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
    week_dates = sorted(
        str(item.get("date"))
        for item in official.get("occurrences", [])
        if int(item.get("academic_week") or 0) == academic_week and item.get("date")
    )
    if selected_date is None and week_dates:
        first_date = date.fromisoformat(week_dates[0])
        week_start_date = (first_date - timedelta(days=first_date.weekday())).isoformat()
        week_end_date = (first_date + timedelta(days=6 - first_date.weekday())).isoformat()
    elif selected_date is None:
        week_start_date, week_end_date = _calendar_week_bounds(academic_week)
    course_sections = sorted(
        assignments,
        key=lambda item: str(item.get("section_code") or ""),
    )
    section_dates: dict[str, list[str]] = {}
    for item in official.get("occurrences", []):
        section_code = str(item.get("section_code") or "")
        occurrence_date = str(item.get("date") or "")
        if section_code and occurrence_date:
            section_dates.setdefault(section_code, []).append(occurrence_date)
    for section in course_sections:
        dates = sorted(section_dates.get(str(section.get("section_code") or ""), []))
        section["start_date"] = dates[0] if dates else None
        section["end_date"] = dates[-1] if dates else None
    missing_required = [str(item.get("section_code") or "") for item in course_sections if item.get("required_sessions") is None]
    if missing_required:
        with get_session_local()() as session:
            required_rows = session.scalars(
                select(CourseSectionModel).where(CourseSectionModel.section_code.in_(missing_required))
            ).all()
        required_by_section = {item.section_code: item.required_sessions for item in required_rows}
        for section in course_sections:
            if section.get("required_sessions") is None:
                section["required_sessions"] = required_by_section.get(str(section.get("section_code") or ""))
    return {
        "official_code": official.get("official_code"),
        "academic_week": academic_week,
        "week_start_date": week_start_date,
        "week_end_date": week_end_date,
        "lecturer_code": lecturer_code,
        "lecturer_name": assignments[0].get("lecturer_name") if assignments else "",
        "occurrences": occurrences,
        "teaching_dates": teaching_dates,
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


def _calendar_week_bounds(academic_week: int | None) -> tuple[str | None, str | None]:
    if academic_week is None:
        return None, None
    with get_session_local()() as session:
        dates = session.scalars(
            select(AcademicCalendarDateModel.date)
            .where(AcademicCalendarDateModel.academic_week == academic_week)
            .order_by(AcademicCalendarDateModel.date)
        ).all()
        calendar_anchor = session.execute(
            select(AcademicCalendarDateModel.date, AcademicCalendarDateModel.academic_week)
            .order_by(AcademicCalendarDateModel.date)
            .limit(1)
        ).first()
    if dates:
        start = dates[0] - timedelta(days=dates[0].weekday())
    elif calendar_anchor:
        anchor_date, anchor_week = calendar_anchor
        start = anchor_date - timedelta(days=anchor_date.weekday()) + timedelta(days=(academic_week - anchor_week) * 7)
    else:
        return None, None
    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def _calendar_week_for_date(value: date) -> int | None:
    with get_session_local()() as session:
        return session.scalar(
            select(AcademicCalendarDateModel.academic_week)
            .where(AcademicCalendarDateModel.date == value)
        )


def _requested_week_bounds(academic_week: int | None, selected_date: date | None) -> tuple[str | None, str | None]:
    if selected_date is not None:
        start = selected_date - timedelta(days=selected_date.weekday())
        return start.isoformat(), (start + timedelta(days=6)).isoformat()
    return _calendar_week_bounds(academic_week)


def _empty_result(lecturer_code: str, academic_week: int | None, selected_date: date | None = None) -> dict[str, Any]:
    week_start_date, week_end_date = _requested_week_bounds(academic_week, selected_date)
    return {
        "official_code": None,
        "academic_week": academic_week,
        "week_start_date": week_start_date,
        "week_end_date": week_end_date,
        "lecturer_code": lecturer_code,
        "lecturer_name": "",
        "occurrences": [],
        "teaching_dates": [],
        "course_sections": [],
    }
