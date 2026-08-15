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
    auth_session_ttl_minutes: int = 480
    auth_cookie_secure: bool = False
    cors_origins: tuple[str, ...] = (
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    )


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Timetable GA API"),
        database_url=os.getenv("DATABASE_URL"),
        auth_session_ttl_minutes=max(1, int(os.getenv("AUTH_SESSION_TTL_MINUTES", "480"))),
        auth_cookie_secure=os.getenv("AUTH_COOKIE_SECURE", "false").strip().lower()
        in {"1", "true", "yes", "on"},
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://127.0.0.1:5173,http://localhost:5173",
            ).split(",")
            if origin.strip()
        ),
    )
