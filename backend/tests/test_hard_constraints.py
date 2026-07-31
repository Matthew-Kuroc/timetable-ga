from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from backend.app.domain.models import LecturerTimePreference, ScheduleAssignment, TimeSlot, TimetableInputData
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.scheduling.hard_constraints import check_hard_constraints, period_ranges_overlap


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class HardConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        result = validate_sample_dataset(SAMPLE_DIR)
        self.assertTrue(result.is_valid)
        assert result.data is not None
        self.input_data = result.data

    def test_valid_assignment_has_no_hard_violations(self) -> None:
        violations = check_hard_constraints(self.input_data, _valid_assignments())

        self.assertEqual(violations, ())

    def test_weekend_slots_are_valid_when_configured(self) -> None:
        violations = check_hard_constraints(self.input_data, _valid_assignments())

        self.assertFalse(any(error.slot_code in {"SAT_1_6", "SUN_2_6"} for error in violations))

    def test_same_lecturer_overlap_is_reported(self) -> None:
        assignments = _replace_assignment("IT405_01", room_code="F201", slot_code="MON_1_3")

        violations = check_hard_constraints(self.input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-01"))

    def test_same_room_overlap_is_reported(self) -> None:
        assignments = _replace_assignment("IT402_01", room_code="A303", slot_code="MON_1_3")

        violations = check_hard_constraints(self.input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-02"))

    def test_room_type_mismatch_is_reported(self) -> None:
        assignments = _replace_assignment("IT403_01", room_code="A303", slot_code="FRI_1_5")

        violations = check_hard_constraints(self.input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-06"))

    def test_room_capacity_violation_is_reported(self) -> None:
        assignments = _replace_assignment("IT405_01", room_code="A303", slot_code="MON_10_12")

        violations = check_hard_constraints(self.input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-07"))

    def test_course_type_and_slot_duration_mismatch_is_reported(self) -> None:
        assignments = _replace_assignment("IT403_01", room_code="LAB301", slot_code="MON_1_3")

        violations = check_hard_constraints(self.input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-05"))

    def test_confirmed_lecturer_restriction_is_reported(self) -> None:
        input_data = _with_confirmed_lecturer_restriction(self.input_data, "GV001", "TUE_1_3")
        assignments = _replace_assignment("IT401_01", room_code="A303", slot_code="TUE_1_3")

        violations = check_hard_constraints(input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-09"))

    def test_room_unavailable_slot_is_reported(self) -> None:
        assignments = _replace_assignment("IT403_01", room_code="LAB301", slot_code="SUN_2_6")

        violations = check_hard_constraints(self.input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-08"))

    def test_partial_period_overlap_is_detected(self) -> None:
        first = TimeSlot(
            slot_code="FRI_1_5",
            day_of_week=6,
            start_period=1,
            end_period=5,
            supports_course_types=("PRACTICE", "INTEGRATED"),
            active=True,
        )
        second = TimeSlot(
            slot_code="FRI_2_6",
            day_of_week=6,
            start_period=2,
            end_period=6,
            supports_course_types=("PRACTICE", "INTEGRATED"),
            active=True,
        )

        self.assertTrue(period_ranges_overlap(first, second))

    def test_partial_room_overlap_is_reported(self) -> None:
        input_data = _with_added_slot(
            self.input_data,
            TimeSlot(
                slot_code="FRI_2_6",
                day_of_week=6,
                start_period=2,
                end_period=6,
                supports_course_types=("PRACTICE", "INTEGRATED"),
                active=True,
            ),
        )
        assignments = (
            ScheduleAssignment("IT401_01", "A303", "MON_1_3"),
            ScheduleAssignment("IT402_01", "B204", "TUE_1_3"),
            ScheduleAssignment("IT403_01", "LAB301", "FRI_1_5"),
            ScheduleAssignment("IT404_01", "LAB301", "FRI_2_6"),
            ScheduleAssignment("IT405_01", "F201", "MON_10_12"),
        )

        violations = check_hard_constraints(input_data, assignments)

        self.assertTrue(_has_code(violations, "HC-02"))


def _valid_assignments() -> tuple[ScheduleAssignment, ...]:
    return (
        ScheduleAssignment("IT401_01", "A303", "MON_1_3"),
        ScheduleAssignment("IT402_01", "B204", "TUE_1_3"),
        ScheduleAssignment("IT403_01", "LAB301", "FRI_1_5"),
        ScheduleAssignment("IT404_01", "LAB401", "SAT_1_6"),
        ScheduleAssignment("IT405_01", "F201", "MON_10_12"),
    )


def _replace_assignment(
    section_code: str,
    room_code: str,
    slot_code: str,
) -> tuple[ScheduleAssignment, ...]:
    return tuple(
        ScheduleAssignment(section_code, room_code, slot_code)
        if assignment.section_code == section_code
        else assignment
        for assignment in _valid_assignments()
    )


def _with_added_slot(input_data: TimetableInputData, slot: TimeSlot) -> TimetableInputData:
    time_slots = dict(input_data.time_slots)
    time_slots[slot.slot_code] = slot
    return replace(input_data, time_slots=time_slots)


def _with_confirmed_lecturer_restriction(
    input_data: TimetableInputData,
    lecturer_code: str,
    slot_code: str,
) -> TimetableInputData:
    return replace(
        input_data,
        lecturer_time_preferences=(
            *input_data.lecturer_time_preferences,
            LecturerTimePreference(
                lecturer_code=lecturer_code,
                slot_code=slot_code,
                mandatory=True,
                reason="Confirmed by Training Office",
            ),
        ),
    )


def _has_code(violations: tuple[object, ...], code: str) -> bool:
    return any(getattr(violation, "code") == code for violation in violations)


if __name__ == "__main__":
    unittest.main()
