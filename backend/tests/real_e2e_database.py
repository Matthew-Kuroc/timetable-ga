"""Prepare an isolated PostgreSQL database for the real browser workflow.

This helper is intentionally guarded: it refuses to reset a database whose
name does not end in ``_e2e``.  It is invoked by the PowerShell E2E runner,
not by the normal application.
"""

from __future__ import annotations

import os

import psycopg
from psycopg import sql
from sqlalchemy.engine import URL, make_url


def _target_url() -> URL:
    raw_url = os.getenv("E2E_DATABASE_URL", "").strip()
    if not raw_url:
        raise SystemExit("E2E_DATABASE_URL phải được cấu hình trước khi chạy E2E thật.")
    url = make_url(raw_url)
    database = url.database or ""
    if not database.endswith("_e2e"):
        raise SystemExit(
            "Từ chối reset database không có hậu tố _e2e. "
            "Hãy dùng database riêng, ví dụ timetable_ga_e2e."
        )
    if not url.username:
        raise SystemExit("E2E_DATABASE_URL phải có tên người dùng PostgreSQL.")
    return url


def _connect_kwargs(url: URL, database: str) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "dbname": database,
        "user": url.username,
    }
    if url.password is not None:
        kwargs["password"] = url.password
    if url.host is not None:
        kwargs["host"] = url.host
    if url.port is not None:
        kwargs["port"] = url.port
    for key in ("sslmode", "connect_timeout"):
        if key in url.query:
            kwargs[key] = url.query[key]
    return kwargs


def main() -> int:
    url = _target_url()
    target_database = str(url.database)

    with psycopg.connect(
        **_connect_kwargs(url, "postgres"),
        autocommit=True,
    ) as admin_connection:
        exists = admin_connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (target_database,),
        ).fetchone()
        if exists is None:
            admin_connection.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_database))
            )

    with psycopg.connect(
        **_connect_kwargs(url, target_database),
        autocommit=True,
    ) as target_connection:
        target_connection.execute("DROP SCHEMA IF EXISTS public CASCADE")
        target_connection.execute("CREATE SCHEMA public")

    print(f"Đã chuẩn bị database E2E riêng: {target_database}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
