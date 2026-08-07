from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.core.config import get_settings
from backend.app.db.session import DatabaseConfigurationError, create_database_engine


REPO_ROOT = Path(__file__).resolve().parents[2]


class DatabaseConfigTests(unittest.TestCase):
    def test_database_url_must_be_explicit(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(get_settings().database_url)
            with self.assertRaises(DatabaseConfigurationError):
                create_database_engine()

    def test_engine_factory_can_use_explicit_sqlite_url_for_tests(self) -> None:
        engine = create_database_engine("sqlite:///:memory:")

        self.assertEqual(engine.url.drivername, "sqlite")

    def test_alembic_files_exist(self) -> None:
        self.assertTrue((REPO_ROOT / "alembic.ini").exists())
        self.assertTrue((REPO_ROOT / "backend" / "alembic" / "env.py").exists())
        self.assertTrue((REPO_ROOT / "backend" / "alembic" / "versions" / "20260730_0001_initial_schema.py").exists())


if __name__ == "__main__":
    unittest.main()
