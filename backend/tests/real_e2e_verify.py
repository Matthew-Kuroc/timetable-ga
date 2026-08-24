"""Verify that the browser workflow persisted its important records in PostgreSQL."""

from __future__ import annotations

import os

from sqlalchemy import func, select

from backend.app.db.models import (
    AppUserModel,
    GaRunModel,
    ImportBatchModel,
    MakeupSessionModel,
    OfficialTimetableModel,
    ScheduleChangeRequestModel,
)
from backend.app.db.session import get_session_local, reset_database_state


def main() -> int:
    database_url = os.getenv("E2E_DATABASE_URL", "").strip()
    if not database_url.rsplit("/", 1)[-1].split("?", 1)[0].endswith("_e2e"):
        raise SystemExit("Chỉ xác minh database E2E có hậu tố _e2e.")
    os.environ["DATABASE_URL"] = database_url
    reset_database_state()

    models = {
        "app_users": AppUserModel,
        "import_batches": ImportBatchModel,
        "ga_runs": GaRunModel,
        "official_timetables": OfficialTimetableModel,
        "makeup_sessions": MakeupSessionModel,
        "schedule_change_requests": ScheduleChangeRequestModel,
    }
    with get_session_local()() as session:
        counts = {
            name: int(session.scalar(select(func.count()).select_from(model)) or 0)
            for name, model in models.items()
        }
    missing = [name for name, count in counts.items() if count < 1]
    if missing:
        raise SystemExit(f"E2E chưa ghi dữ liệu vào các bảng: {', '.join(missing)}")
    print("Đã xác minh PostgreSQL: " + ", ".join(f"{name}={count}" for name, count in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
