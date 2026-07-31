from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from backend.app.domain.models import ScheduleAssignment, TimetableInputData


@dataclass(frozen=True)
class SoftConstraintWeights:
    lecturer_preferences: float = 10.0
    room_capacity_waste: float = 1.0
    large_room_small_class: float = 25.0
    schedule_gaps: float = 4.0
    scattered_days: float = 8.0
    consecutive_sessions: float = 6.0
    evening_weekend_avoidance: float = 5.0

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for name, value in self.as_dict().items():
            if value < 0:
                errors.append(f"Trọng số {name} phải lớn hơn hoặc bằng 0.")
        return tuple(errors)

    def as_dict(self) -> dict[str, float]:
        return {
            "lecturer_preferences": self.lecturer_preferences,
            "room_capacity_waste": self.room_capacity_waste,
            "large_room_small_class": self.large_room_small_class,
            "schedule_gaps": self.schedule_gaps,
            "scattered_days": self.scattered_days,
            "consecutive_sessions": self.consecutive_sessions,
            "evening_weekend_avoidance": self.evening_weekend_avoidance,
        }


def score_soft_constraints(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
    weights: SoftConstraintWeights,
) -> dict[str, float]:
    return {
        "lecturer_preferences": _lecturer_preference_cost(input_data, assignments) * weights.lecturer_preferences,
        "room_capacity_waste": _room_capacity_waste(input_data, assignments) * weights.room_capacity_waste,
        "large_room_small_class": _large_room_small_class_cost(input_data, assignments) * weights.large_room_small_class,
        "schedule_gaps": _schedule_gap_cost(input_data, assignments) * weights.schedule_gaps,
        "scattered_days": _scattered_day_cost(input_data, assignments) * weights.scattered_days,
        "consecutive_sessions": _consecutive_session_cost(input_data, assignments) * weights.consecutive_sessions,
        "evening_weekend_avoidance": _evening_weekend_cost(input_data, assignments) * weights.evening_weekend_avoidance,
    }


def _lecturer_preference_cost(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> float:
    non_mandatory_undesired_slots = {
        (preference.lecturer_code, preference.slot_code)
        for preference in input_data.lecturer_time_preferences
        if not preference.mandatory
    }
    total = 0.0
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        slot = input_data.time_slots.get(assignment.slot_code)
        if section is None or slot is None:
            continue
        lecturer = input_data.lecturers.get(section.lecturer_code)
        if lecturer is None:
            continue

        if lecturer.preferred_days and slot.day_of_week not in lecturer.preferred_days:
            total += 1.0
        if lecturer.preferred_slots and slot.slot_code not in lecturer.preferred_slots:
            total += 1.0
        if slot.day_of_week in lecturer.undesired_days:
            total += 2.0
        if slot.slot_code in lecturer.undesired_slots:
            total += 2.0
        if (lecturer.lecturer_code, slot.slot_code) in non_mandatory_undesired_slots:
            total += 1.0
    return total


def _room_capacity_waste(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> float:
    total = 0.0
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        room = input_data.rooms.get(assignment.room_code)
        if section is None or room is None:
            continue
        total += max(0, room.capacity - section.scheduling_student_count)
    return total


def _large_room_small_class_cost(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> float:
    total = 0.0
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        room = input_data.rooms.get(assignment.room_code)
        if section is None or room is None:
            continue
        if room.room_size_category == "LARGE_HALL" and section.scheduling_student_count < 80:
            total += 1.0
    return total


def _schedule_gap_cost(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> float:
    by_lecturer_day: dict[tuple[str, int], list[tuple[int, int]]] = defaultdict(list)
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        slot = input_data.time_slots.get(assignment.slot_code)
        if section is None or slot is None:
            continue
        by_lecturer_day[(section.lecturer_code, slot.day_of_week)].append((slot.start_period, slot.end_period))

    total = 0.0
    for ranges in by_lecturer_day.values():
        for first, second in zip(sorted(ranges), sorted(ranges)[1:]):
            gap = second[0] - first[1] - 1
            if gap > 0:
                total += gap
    return total


def _scattered_day_cost(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> float:
    days_by_lecturer: dict[str, set[int]] = defaultdict(set)
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        slot = input_data.time_slots.get(assignment.slot_code)
        if section is None or slot is None:
            continue
        days_by_lecturer[section.lecturer_code].add(slot.day_of_week)

    total = 0.0
    for lecturer_code, teaching_days in days_by_lecturer.items():
        lecturer = input_data.lecturers.get(lecturer_code)
        if lecturer is None or lecturer.max_days_per_week is None:
            continue
        total += max(0, len(teaching_days) - lecturer.max_days_per_week)
    return total


def _consecutive_session_cost(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
) -> float:
    by_lecturer_day: dict[tuple[str, int], list[tuple[int, int]]] = defaultdict(list)
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        slot = input_data.time_slots.get(assignment.slot_code)
        if section is None or slot is None:
            continue
        by_lecturer_day[(section.lecturer_code, slot.day_of_week)].append((slot.start_period, slot.end_period))

    total = 0.0
    for (lecturer_code, _day), ranges in by_lecturer_day.items():
        lecturer = input_data.lecturers.get(lecturer_code)
        if lecturer is None or lecturer.max_consecutive_sessions is None:
            continue
        total += max(0, _longest_consecutive_run(sorted(ranges)) - lecturer.max_consecutive_sessions)
    return total


def _evening_weekend_cost(input_data: TimetableInputData, assignments: tuple[ScheduleAssignment, ...]) -> float:
    total = 0.0
    for assignment in assignments:
        section = input_data.course_sections.get(assignment.section_code)
        slot = input_data.time_slots.get(assignment.slot_code)
        if section is None or slot is None:
            continue
        lecturer = input_data.lecturers.get(section.lecturer_code)
        if lecturer is None:
            continue
        is_weekend = slot.day_of_week in {7, 8}
        is_evening = slot.start_period >= 13
        if is_weekend and slot.day_of_week not in lecturer.preferred_days:
            total += 1.0
        if is_evening and slot.slot_code not in lecturer.preferred_slots:
            total += 1.0
    return total


def _longest_consecutive_run(ranges: list[tuple[int, int]]) -> int:
    if not ranges:
        return 0
    longest = 1
    current = 1
    for first, second in zip(ranges, ranges[1:]):
        if second[0] == first[1] + 1:
            current += 1
        else:
            current = 1
        longest = max(longest, current)
    return longest
