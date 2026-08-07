from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load local development settings from the repository root. Environment variables
# supplied by the host still take precedence over values in this file.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))


@dataclass(frozen=True)
class Settings:
    app_name: str = "Timetable GA API"
    database_url: str | None = None


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Timetable GA API"),
        database_url=os.getenv("DATABASE_URL"),
    )
