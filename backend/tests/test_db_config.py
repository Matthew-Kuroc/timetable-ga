from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.core.config import DEFAULT_DATABASE_URL, get_settings
from backend.app.db.session import create_database_engine


REPO_ROOT = Path(__file__).resolve().parents[2]


class DatabaseConfigTests(unittest.TestCase):
    def test_default_database_url_uses_postgresql(self) -> None:
        self.assertTrue(DEFAULT_DATABASE_URL.startswith("postgresql+psycopg://"))
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(get_settings().database_url, DEFAULT_DATABASE_URL)

    def test_engine_factory_can_use_explicit_sqlite_url_for_tests(self) -> None:
        engine = create_database_engine("sqlite:///:memory:")

        self.assertEqual(engine.url.drivername, "sqlite")

    def test_alembic_files_exist(self) -> None:
        self.assertTrue((REPO_ROOT / "alembic.ini").exists())
        self.assertTrue((REPO_ROOT / "backend" / "alembic" / "env.py").exists())
        self.assertTrue((REPO_ROOT / "backend" / "alembic" / "versions" / "20260730_0001_initial_schema.py").exists())


if __name__ == "__main__":
    unittest.main()
