from __future__ import annotations

import unittest

from sqlalchemy import create_engine

from backend.app.db.base import Base
from backend.app.db import models


class DatabaseModelTests(unittest.TestCase):
    def test_core_tables_are_declared(self) -> None:
        expected_tables = {
            "academic_calendar_dates",
            "academic_terms",
            "import_batches",
            "lecturers",
            "rooms",
            "schedule_occurrences",
            "time_slots",
            "course_sections",
            "ga_runs",
            "schedule_assignments",
            "official_timetables",
            "schedule_segments",
            "makeup_sessions",
        }

        self.assertTrue(expected_tables.issubset(Base.metadata.tables.keys()))

    def test_course_sections_have_required_columns(self) -> None:
        columns = Base.metadata.tables["course_sections"].columns.keys()

        for column in (
            "course_code",
            "course_name",
            "section_code",
            "lecturer_id",
            "required_sessions",
            "weekly_sessions",
            "periods_per_session",
            "scheduling_student_count",
            "course_type",
            "required_room_type",
            "start_date",
            "end_date",
        ):
            self.assertIn(column, columns)

    def test_metadata_can_create_tables(self) -> None:
        engine = create_engine("sqlite:///:memory:")

        Base.metadata.create_all(engine)

        self.assertIn("schedule_assignments", Base.metadata.tables)


if __name__ == "__main__":
    unittest.main()
