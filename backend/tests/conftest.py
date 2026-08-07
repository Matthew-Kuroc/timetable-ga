from __future__ import annotations

import pytest

from backend.app.db.base import Base
from backend.app.db.session import create_database_engine, reset_database_state


@pytest.fixture(autouse=True)
def configured_test_database(tmp_path, monkeypatch):
    """Every test gets a fresh SQL database; application code must not fall back to JSON."""
    database_path = tmp_path / "timetable-test.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    reset_database_state()
    engine = create_database_engine()
    Base.metadata.create_all(engine)
    yield
    engine.dispose()
    reset_database_state()
