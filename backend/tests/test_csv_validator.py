from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from backend.app.importing.csv_validator import validate_sample_dataset


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "data" / "samples" / "small"


class CsvValidatorTests(unittest.TestCase):
    def test_valid_week03_sample_dataset(self) -> None:
        result = validate_sample_dataset(SAMPLE_DIR)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, ())
        self.assertIsNotNone(result.data)
        assert result.data is not None
        self.assertEqual(len(result.data.lecturers), 4)
        self.assertEqual(len(result.data.rooms), 5)
        self.assertEqual(len(result.data.course_sections), 5)
        self.assertEqual(len(result.data.academic_calendar_dates), 35)
        self.assertIn("SAT_1_6", result.data.time_slots)
        self.assertIn("SUN_2_6", result.data.time_slots)

    def test_missing_required_column_is_reported(self) -> None:
        with _copied_sample_dir() as copied_dir:
            _rewrite_csv_without_column(copied_dir / "course_sections.csv", "required_room_type")

            result = validate_sample_dataset(copied_dir)

        self.assertFalse(result.is_valid)
        self.assertTrue(
            any(error.file == "course_sections.csv" and error.reason == "Thiếu cột bắt buộc" for error in result.errors)
        )

    def test_duplicate_section_code_is_reported(self) -> None:
        with _copied_sample_dir() as copied_dir:
            _replace_csv_value(copied_dir / "course_sections.csv", 1, "section_code", "IT401_01")

            result = validate_sample_dataset(copied_dir)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("trùng" in error.reason for error in result.errors))

    def test_unknown_lecturer_reference_is_reported(self) -> None:
        with _copied_sample_dir() as copied_dir:
            _replace_csv_value(copied_dir / "course_sections.csv", 0, "lecturer_code", "GV999")

            result = validate_sample_dataset(copied_dir)

        self.assertFalse(result.is_valid)
        self.assertTrue(
            any(error.column == "lecturer_code" and "không tồn tại" in error.reason for error in result.errors)
        )

    def test_scheduling_student_count_must_follow_priority_rule(self) -> None:
        with _copied_sample_dir() as copied_dir:
            _replace_csv_value(copied_dir / "course_sections.csv", 0, "scheduling_student_count", "50")

            result = validate_sample_dataset(copied_dir)

        self.assertFalse(result.is_valid)
        self.assertTrue(any(error.column == "scheduling_student_count" for error in result.errors))

    def test_makeup_window_requires_teaching_dates_through_week_18(self) -> None:
        with _copied_sample_dir() as copied_dir:
            rows = [row for row in _read_rows(copied_dir / "academic_calendar.csv") if row["academic_week"] != "18"]
            _write_rows(copied_dir / "academic_calendar.csv", list(rows[0].keys()), rows)

            result = validate_sample_dataset(copied_dir)

        self.assertFalse(result.is_valid)
        self.assertTrue(any(error.column == "academic_week" and error.value == "18" for error in result.errors))

    def test_practice_two_meeting_schema_accepts_three_plus_two(self) -> None:
        with _copied_sample_dir() as copied_dir:
            sections = _read_rows(copied_dir / "course_sections.csv")
            sections[2]["weekly_sessions"] = "2"
            sections[2]["periods_per_session"] = "3"
            sections[2]["second_session_periods"] = "2"
            _write_rows(copied_dir / "course_sections.csv", list(sections[0].keys()), sections)
            slots = _read_rows(copied_dir / "time_slots.csv")
            slots.extend(
                [
                    {"slot_code": "PRACTICE_MON_1_3", "day_of_week": "2", "start_period": "1", "end_period": "3", "session_type": "SANG", "supports_course_types": "PRACTICE|INTEGRATED", "active": "true"},
                    {"slot_code": "PRACTICE_MON_4_5", "day_of_week": "2", "start_period": "4", "end_period": "5", "session_type": "SANG", "supports_course_types": "PRACTICE|INTEGRATED", "active": "true"},
                ]
            )
            _write_rows(copied_dir / "time_slots.csv", list(slots[0].keys()), slots)

            result = validate_sample_dataset(copied_dir)

        self.assertTrue(result.is_valid, result.errors)
        assert result.data is not None
        section = result.data.course_sections["IT403_01"]
        self.assertEqual(section.weekly_sessions, 2)
        self.assertEqual(section.periods_per_session, 3)
        self.assertEqual(section.second_session_periods, 2)

    def test_room_capacity_domain_is_checked(self) -> None:
        with _copied_sample_dir() as copied_dir:
            _replace_csv_value(copied_dir / "rooms.csv", 2, "capacity", "80")

            result = validate_sample_dataset(copied_dir)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("sức chứa" in error.reason for error in result.errors))


class _copied_sample_dir:
    def __enter__(self) -> Path:
        self._temp_dir = tempfile.TemporaryDirectory()
        copied_dir = Path(self._temp_dir.name) / "sample"
        shutil.copytree(SAMPLE_DIR, copied_dir)
        return copied_dir

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


def _rewrite_csv_without_column(path: Path, column: str) -> None:
    rows = _read_rows(path)
    fieldnames = [field for field in rows[0].keys() if field != column]
    _write_rows(path, fieldnames, rows)


def _replace_csv_value(path: Path, row_index: int, column: str, value: str) -> None:
    rows = _read_rows(path)
    rows[row_index][column] = value
    _write_rows(path, list(rows[0].keys()), rows)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
