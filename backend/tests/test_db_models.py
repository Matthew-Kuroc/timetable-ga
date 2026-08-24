from __future__ import annotations

import unittest

from sqlalchemy import create_engine

from backend.app.db.base import Base
from backend.app.db import models


class DatabaseModelTests(unittest.TestCase):
    def test_core_tables_are_declared(self) -> None:
        expected_tables = {
            "account_audit_logs",
            "academic_calendar_dates",
            "academic_terms",
            "app_users",
            "auth_sessions",
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

    def test_auth_tables_have_required_columns(self) -> None:
        user_columns = Base.metadata.tables["app_users"].columns.keys()
        session_columns = Base.metadata.tables["auth_sessions"].columns.keys()
        audit_columns = Base.metadata.tables["account_audit_logs"].columns.keys()

        for column in ("username", "password_hash", "role", "active", "lecturer_code"):
            self.assertIn(column, user_columns)
        for column in ("user_id", "token_hash", "expires_at", "revoked_at"):
            self.assertIn(column, session_columns)
        for column in ("actor_user_id", "target_user_id", "action", "old_value", "new_value"):
            self.assertIn(column, audit_columns)

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
            "second_session_periods",
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
        self.assertIn("meeting_number", Base.metadata.tables["schedule_assignments"].columns.keys())


if __name__ == "__main__":
    unittest.main()
