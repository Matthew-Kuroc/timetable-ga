from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from backend.app.domain.models import LecturerTimePreference, TimetableInputData
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.scheduling.feasible_assignments import (
    build_feasible_assignment_domains,
    find_sections_without_feasible_assignments,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class FeasibleAssignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        result = validate_sample_dataset(SAMPLE_DIR)
        self.assertTrue(result.is_valid)
        assert result.data is not None
        self.input_data = result.data

    def test_builds_non_empty_domain_for_each_sample_section(self) -> None:
        domains = build_feasible_assignment_domains(self.input_data)

        self.assertEqual(len(domains), len(self.input_data.course_sections))
        self.assertEqual(find_sections_without_feasible_assignments(domains), ())

    def test_theory_section_uses_only_theory_slots_and_matching_rooms(self) -> None:
        domains = build_feasible_assignment_domains(self.input_data)
        domain = _domain_for(domains, "IT401_01")

        self.assertTrue(domain.assignments)
        for assignment in domain.assignments:
            slot = self.input_data.time_slots[assignment.slot_code]
            room = self.input_data.rooms[assignment.room_code]
            self.assertIn("THEORY", slot.supports_course_types)
            self.assertEqual(slot.duration, 3)
            self.assertEqual(room.room_type, "THEORY_ROOM")

    def test_practice_section_uses_only_practice_slots_and_computer_lab(self) -> None:
        domains = build_feasible_assignment_domains(self.input_data)
        domain = _domain_for(domains, "IT403_01")

        self.assertTrue(domain.assignments)
        for assignment in domain.assignments:
            slot = self.input_data.time_slots[assignment.slot_code]
            room = self.input_data.rooms[assignment.room_code]
            self.assertIn("PRACTICE", slot.supports_course_types)
            self.assertEqual(slot.duration, 5)
            self.assertEqual(room.room_type, "COMPUTER_LAB")

    def test_confirmed_lecturer_restriction_is_excluded(self) -> None:
        input_data = _with_confirmed_lecturer_restriction(self.input_data, "GV001", "TUE_1_3")

        domains = build_feasible_assignment_domains(input_data)
        domain = _domain_for(domains, "IT401_01")

        self.assertFalse(any(assignment.slot_code == "TUE_1_3" for assignment in domain.assignments))

    def test_room_unavailable_slot_is_excluded(self) -> None:
        domains = build_feasible_assignment_domains(self.input_data)
        domain = _domain_for(domains, "IT403_01")

        self.assertFalse(
            any(
                assignment.room_code == "LAB301" and assignment.slot_code == "SUN_2_6"
                for assignment in domain.assignments
            )
        )

    def test_reports_section_without_feasible_room(self) -> None:
        rooms = {
            room_code: replace(room, available=False)
            for room_code, room in self.input_data.rooms.items()
            if room.room_type == "SPECIALIZED_LAB"
        }
        input_data = replace(
            self.input_data,
            rooms={
                **self.input_data.rooms,
                **rooms,
            },
        )

        domains = build_feasible_assignment_domains(input_data)

        self.assertIn("IT404_01", find_sections_without_feasible_assignments(domains))


def _domain_for(domains, section_code: str):
    return next(domain for domain in domains if domain.section_code == section_code)


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


if __name__ == "__main__":
    unittest.main()
