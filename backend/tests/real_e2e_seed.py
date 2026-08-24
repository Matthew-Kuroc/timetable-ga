"""Seed the minimum accounts required by the real PostgreSQL E2E workflow."""

from __future__ import annotations

import os

from backend.app.db.session import reset_database_state
from backend.app.domain.auth import UserRole
from backend.app.services.user_service import bootstrap_admin, create_user


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Thiếu biến môi trường {name} cho E2E thật.")
    return value


def main() -> int:
    database_url = _required("E2E_DATABASE_URL")
    if not database_url.rsplit("/", 1)[-1].split("?", 1)[0].endswith("_e2e"):
        raise SystemExit("Chỉ được seed database riêng có hậu tố _e2e.")
    os.environ["DATABASE_URL"] = database_url
    reset_database_state()

    password = _required("E2E_ACCOUNT_PASSWORD")
    admin = bootstrap_admin(
        username=os.getenv("E2E_ADMIN_USERNAME", "admin.e2e"),
        display_name="Quản trị viên E2E",
        password=password,
    )
    create_user(
        username=os.getenv("E2E_OFFICE_USERNAME", "office.e2e"),
        display_name="Phòng Đào tạo E2E",
        password=password,
        role=UserRole.TRAINING_OFFICE,
        lecturer_code=None,
        actor=admin,
    )
    print("Đã tạo tài khoản ADMIN và TRAINING_OFFICE cho E2E.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
