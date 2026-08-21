from __future__ import annotations

import os

import pytest
from sqlalchemy import inspect

from backend.app.db.session import get_engine, reset_database_state


@pytest.fixture(autouse=True)
def configured_test_database(monkeypatch):
    database_url = os.getenv("POSTGRES_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("PostgreSQL integration test chỉ chạy khi có POSTGRES_TEST_DATABASE_URL.")
    monkeypatch.setenv("DATABASE_URL", database_url)
    reset_database_state()
    yield
    reset_database_state()


def test_postgres_migrations_create_runtime_schema() -> None:
    inspector = inspect(get_engine())
    tables = set(inspector.get_table_names())
    assert {"app_users", "ga_runs", "official_timetables", "schedule_change_requests"} <= tables
