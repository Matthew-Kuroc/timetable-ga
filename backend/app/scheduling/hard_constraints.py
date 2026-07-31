from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from backend.app.domain.models import (
    CourseSection,
    HardConstraintViolation,
    ScheduleAssignment,
    TimeSlot,
    TimetableInputData,
)


VALID_THEORY_RANGES = {(1, 3), (4, 6), (7, 9), (10, 12), (13, 15)}
VALID_LONG_RANGES = {(1, 5), (1, 6), (2, 6)}


def check_hard_constraints(
    input_data: TimetableInputData,
    assignments: Iterable[ScheduleAssignment],
) -> tuple[HardConstraintViolation, ...]:
    violations: list[HardConstraintViolation] = []
    normalized_assignments = tuple(assignments)

    _check_assignment_structure(input_data, normalized_assignments, violations)
    valid_assignments = [
        assignment
        for assignment in normalized_assignments
        if assignment.section_code in input_data.course_sections
        and assignment.room_code in input_data.rooms
        and assignment.slot_code in input_data.time_slots
    ]

    _check_local_assignment_rules(input_data, valid_assignments, violations)
    _check_confirmed_lecturer_restrictions(input_data, valid_assignments, violations)
    _check_room_unavailable_slots(input_data, valid_assignments, violations)
    _check_lecturer_overlaps(input_data, valid_assignments, violations)
    _check_room_overlaps(input_data, valid_assignments, violations)

    return tuple(violations)


def period_ranges_overlap(first: TimeSlot, second: TimeSlot) -> bool:
    if first.day_of_week != second.day_of_week:
        return False
    return first.start_period <= second.end_period and second.start_period <= first.end_period


def _check_assignment_structure(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
    violations: list[HardConstraintViolation],
) -> None:
    assigned_sections = {assignment.section_code for assignment in assignments}
    for section_code in input_data.course_sections:
        if section_code not in assigned_sections:
            violations.append(
                HardConstraintViolation(
                    code="HC-03",
                    message=f"Lớp {section_code} chưa có lịch học cơ bản.",
                    section_code=section_code,
                )
            )

    section_counts: dict[str, int] = defaultdict(int)
    for assignment in assignments:
        section_counts[assignment.section_code] += 1
        if assignment.section_code not in input_data.course_sections:
            violations.append(
                HardConstraintViolation(
                    code="HC-10",
                    message=f"Lớp {assignment.section_code} không tồn tại trong dữ liệu đầu vào.",
                    section_code=assignment.section_code,
                    room_code=assignment.room_code,
                    slot_code=assignment.slot_code,
                )
            )
        if assignment.room_code not in input_data.rooms:
            violations.append(
                HardConstraintViolation(
                    code="HC-10",
                    message=f"Phòng {assignment.room_code} không tồn tại trong dữ liệu đầu vào.",
                    section_code=assignment.section_code,
                    room_code=assignment.room_code,
                    slot_code=assignment.slot_code,
                )
            )
        if assignment.slot_code not in input_data.time_slots:
            violations.append(
                HardConstraintViolation(
                    code="HC-04",
                    message=f"Khung giờ {assignment.slot_code} không tồn tại trong dữ liệu đầu vào.",
                    section_code=assignment.section_code,
                    room_code=assignment.room_code,
                    slot_code=assignment.slot_code,
                )
            )

    for section_code, count in section_counts.items():
        if count > 1 and section_code in input_data.course_sections:
            violations.append(
                HardConstraintViolation(
                    code="HC-03",
                    message=f"Lớp {section_code} có nhiều hơn một lịch học cơ bản.",
                    section_code=section_code,
                )
            )


def _check_local_assignment_rules(
    input_data: TimetableInputData,
    assignments: Iterable[ScheduleAssignment],
    violations: list[HardConstraintViolation],
) -> None:
    for assignment in assignments:
        section = input_data.course_sections[assignment.section_code]
        room = input_data.rooms[assignment.room_code]
        slot = input_data.time_slots[assignment.slot_code]

        if not slot.active:
            violations.append(
                HardConstraintViolation(
                    code="HC-04",
                    message=f"Khung giờ {slot.slot_code} không được kích hoạt để xếp lịch.",
                    section_code=section.section_code,
                    room_code=room.room_code,
                    slot_code=slot.slot_code,
                )
            )

        if not _slot_supports_section(slot, section):
            violations.append(
                HardConstraintViolation(
                    code="HC-05",
                    message=(
                        f"Khung giờ {slot.slot_code} không phù hợp với loại lớp "
                        f"{section.course_type} và số tiết {section.periods_per_session}."
                    ),
                    section_code=section.section_code,
                    room_code=room.room_code,
                    slot_code=slot.slot_code,
                )
            )

        if not room.available:
            violations.append(
                HardConstraintViolation(
                    code="HC-08",
                    message=f"Phòng {room.room_code} không khả dụng để xếp lịch.",
                    section_code=section.section_code,
                    room_code=room.room_code,
                    slot_code=slot.slot_code,
                )
            )

        if room.room_type != section.required_room_type:
            violations.append(
                HardConstraintViolation(
                    code="HC-06",
                    message=(
                        f"Phòng {room.room_code} có loại {room.room_type}, "
                        f"không phù hợp yêu cầu {section.required_room_type} của lớp {section.section_code}."
                    ),
                    section_code=section.section_code,
                    room_code=room.room_code,
                    slot_code=slot.slot_code,
                )
            )

        if room.capacity < section.scheduling_student_count:
            violations.append(
                HardConstraintViolation(
                    code="HC-07",
                    message=(
                        f"Phòng {room.room_code} có sức chứa {room.capacity}, "
                        f"nhỏ hơn số lượng xếp lịch {section.scheduling_student_count} của lớp {section.section_code}."
                    ),
                    section_code=section.section_code,
                    room_code=room.room_code,
                    slot_code=slot.slot_code,
                )
            )


def _check_confirmed_lecturer_restrictions(
    input_data: TimetableInputData,
    assignments: Iterable[ScheduleAssignment],
    violations: list[HardConstraintViolation],
) -> None:
    confirmed_restrictions = {
        (item.lecturer_code, item.slot_code)
        for item in input_data.lecturer_time_preferences
        if item.mandatory
    }
    for assignment in assignments:
        section = input_data.course_sections[assignment.section_code]
        if (section.lecturer_code, assignment.slot_code) in confirmed_restrictions:
            violations.append(
                HardConstraintViolation(
                    code="HC-09",
                    message=(
                        f"Giảng viên {section.lecturer_code} có ràng buộc cố định "
                        f"không dạy ở khung giờ {assignment.slot_code}."
                    ),
                    section_code=section.section_code,
                    lecturer_code=section.lecturer_code,
                    room_code=assignment.room_code,
                    slot_code=assignment.slot_code,
                )
            )


def _check_room_unavailable_slots(
    input_data: TimetableInputData,
    assignments: Iterable[ScheduleAssignment],
    violations: list[HardConstraintViolation],
) -> None:
    unavailable_rooms = {
        (item.room_code, item.slot_code)
        for item in input_data.room_unavailable_slots
    }
    for assignment in assignments:
        if (assignment.room_code, assignment.slot_code) in unavailable_rooms:
            violations.append(
                HardConstraintViolation(
                    code="HC-08",
                    message=f"Phòng {assignment.room_code} không khả dụng ở khung giờ {assignment.slot_code}.",
                    section_code=assignment.section_code,
                    room_code=assignment.room_code,
                    slot_code=assignment.slot_code,
                )
            )


def _check_lecturer_overlaps(
    input_data: TimetableInputData,
    assignments: list[ScheduleAssignment],
    violations: list[HardConstraintViolation],
) -> None:
    for index, first in enumerate(assignments):
        first_section = input_data.course_sections[first.section_code]
        first_slot = input_data.time_slots[first.slot_code]
        for second in assignments[index + 1 :]:
            second_section = input_data.course_sections[second.section_code]
            if first_section.lecturer_code != second_section.lecturer_code:
                continue
            second_slot = input_data.time_slots[second.slot_code]
            if period_ranges_overlap(first_slot, second_slot):
                violations.append(
                    HardConstraintViolation(
                        code="HC-01",
                        message=(
                            f"Giảng viên {first_section.lecturer_code} bị trùng lịch "
                            f"giữa lớp {first.section_code} và {second.section_code}."
                        ),
                        section_code=first.section_code,
                        other_section_code=second.section_code,
                        lecturer_code=first_section.lecturer_code,
                        slot_code=first.slot_code,
                    )
                )


def _check_room_overlaps(
    input_data: TimetableInputData,
    assignments: list[ScheduleAssignment],
    violations: list[HardConstraintViolation],
) -> None:
    for index, first in enumerate(assignments):
        first_slot = input_data.time_slots[first.slot_code]
        for second in assignments[index + 1 :]:
            if first.room_code != second.room_code:
                continue
            second_slot = input_data.time_slots[second.slot_code]
            if period_ranges_overlap(first_slot, second_slot):
                violations.append(
                    HardConstraintViolation(
                        code="HC-02",
                        message=(
                            f"Phòng {first.room_code} bị trùng lịch "
                            f"giữa lớp {first.section_code} và {second.section_code}."
                        ),
                        section_code=first.section_code,
                        other_section_code=second.section_code,
                        room_code=first.room_code,
                        slot_code=first.slot_code,
                    )
                )


def _slot_supports_section(slot: TimeSlot, section: CourseSection) -> bool:
    if section.course_type not in slot.supports_course_types:
        return False
    if section.course_type == "THEORY":
        return (slot.start_period, slot.end_period) in VALID_THEORY_RANGES and slot.duration == section.periods_per_session
    return (slot.start_period, slot.end_period) in VALID_LONG_RANGES and slot.duration == section.periods_per_session
