from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from backend.app.domain.models import ScheduleAssignment
from backend.app.importing.csv_validator import validate_sample_dataset
from backend.app.scheduling.calendar_expansion import expand_base_assignments_to_occurrences


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class CalendarExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        result = validate_sample_dataset(SAMPLE_DIR)
        self.assertTrue(result.is_valid)
        assert result.data is not None
        self.input_data = result.data

    def test_holiday_date_does_not_generate_normal_occurrence(self) -> None:
        assignment = ScheduleAssignment("IT401_01", "A303", "MON_1_3")

        result = expand_base_assignments_to_occurrences(self.input_data, (assignment,))

        occurrence_dates = {occurrence.date for occurrence in result.occurrences}
        skipped_dates = {skipped.date for skipped in result.skipped_holiday_sessions}
        self.assertIn(date(2026, 9, 7), occurrence_dates)
        self.assertNotIn(date(2026, 9, 14), occurrence_dates)
        self.assertIn(date(2026, 9, 14), skipped_dates)
        self.assertFalse(any(occurrence.status == "SUSPENDED" for occurrence in result.occurrences))

    def test_calendar_expansion_keeps_weekend_teaching_dates(self) -> None:
        assignment = ScheduleAssignment("IT404_01", "LAB401", "SAT_1_6")

        result = expand_base_assignments_to_occurrences(self.input_data, (assignment,))

        self.assertTrue(result.occurrences)
        self.assertTrue(all(occurrence.slot_code == "SAT_1_6" for occurrence in result.occurrences))


if __name__ == "__main__":
    unittest.main()
