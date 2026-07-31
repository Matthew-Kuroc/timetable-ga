from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_DATABASE_URL = "postgresql+psycopg://timetable_user:timetable_password@localhost:5432/timetable_ga"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Timetable GA API"
    database_url: str = DEFAULT_DATABASE_URL


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Timetable GA API"),
        database_url=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
    )
