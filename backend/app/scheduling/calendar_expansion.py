from __future__ import annotations

from dataclasses import dataclass

from backend.app.domain.models import (
    ScheduleAssignment,
    ScheduleOccurrence,
    SkippedHolidaySession,
    TimetableInputData,
)


@dataclass(frozen=True)
class CalendarExpansionResult:
    occurrences: tuple[ScheduleOccurrence, ...]
    skipped_holiday_sessions: tuple[SkippedHolidaySession, ...]


def expand_base_assignments_to_occurrences(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> CalendarExpansionResult:
    occurrences: list[ScheduleOccurrence] = []
    skipped_holidays: list[SkippedHolidaySession] = []

    for assignment in sorted(assignments, key=lambda item: item.section_code):
        section = input_data.course_sections[assignment.section_code]
        slot = input_data.time_slots[assignment.slot_code]
        matching_dates = [
            calendar_date
            for calendar_date in input_data.academic_calendar_dates.values()
            if section.start_date <= calendar_date.date <= section.end_date
            and calendar_date.day_of_week == slot.day_of_week
        ]

        for calendar_date in sorted(matching_dates, key=lambda item: item.date):
            if calendar_date.is_holiday or not calendar_date.is_teaching_day:
                skipped_holidays.append(
                    SkippedHolidaySession(
                        section_code=assignment.section_code,
                        room_code=assignment.room_code,
                        slot_code=assignment.slot_code,
                        date=calendar_date.date,
                        academic_week=calendar_date.academic_week,
                        holiday_name=calendar_date.holiday_name,
                        meeting_number=assignment.meeting_number,
                    )
                )
                continue

            occurrences.append(
                ScheduleOccurrence(
                    section_code=assignment.section_code,
                    room_code=assignment.room_code,
                    slot_code=assignment.slot_code,
                    date=calendar_date.date,
                    academic_week=calendar_date.academic_week,
                    status="SCHEDULED",
                    meeting_number=assignment.meeting_number,
                )
            )

    return CalendarExpansionResult(
        occurrences=tuple(occurrences),
        skipped_holiday_sessions=tuple(skipped_holidays),
    )
