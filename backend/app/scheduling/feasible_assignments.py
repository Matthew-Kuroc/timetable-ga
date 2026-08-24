from __future__ import annotations

from backend.app.domain.models import (
    FeasibleAssignmentDomain,
    ScheduleAssignment,
    TimetableInputData,
)
from backend.app.scheduling.hard_constraints import check_hard_constraints


def build_feasible_assignment_domains(
    input_data: TimetableInputData,
) -> tuple[FeasibleAssignmentDomain, ...]:
    domains: list[FeasibleAssignmentDomain] = []
    for section in input_data.course_sections.values():
        for meeting_number in range(1, section.weekly_sessions + 1):
            feasible_assignments: list[ScheduleAssignment] = []
            for slot in input_data.time_slots.values():
                for room in input_data.rooms.values():
                    assignment = ScheduleAssignment(
                        section_code=section.section_code,
                        room_code=room.room_code,
                        slot_code=slot.slot_code,
                        meeting_number=meeting_number,
                    )
                    local_input = _single_section_input(input_data, section.section_code)
                    if not check_hard_constraints(local_input, (assignment,), check_structure=False):
                        feasible_assignments.append(assignment)
            domains.append(
                FeasibleAssignmentDomain(
                    section_code=section.section_code,
                    meeting_number=meeting_number,
                    assignments=tuple(feasible_assignments),
                )
            )
    return tuple(domains)


def find_sections_without_feasible_assignments(
    domains: tuple[FeasibleAssignmentDomain, ...],
) -> tuple[str, ...]:
    return tuple(domain.section_code for domain in domains if not domain.assignments)


def _single_section_input(
    input_data: TimetableInputData,
    section_code: str,
) -> TimetableInputData:
    return TimetableInputData(
        lecturers=input_data.lecturers,
        rooms=input_data.rooms,
        time_slots=input_data.time_slots,
        course_sections={section_code: input_data.course_sections[section_code]},
        lecturer_time_preferences=input_data.lecturer_time_preferences,
        room_unavailable_slots=input_data.room_unavailable_slots,
        academic_calendar_dates=input_data.academic_calendar_dates,
    )
