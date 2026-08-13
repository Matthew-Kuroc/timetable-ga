from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.core.security import hash_password
from backend.app.db.models import AppUserModel
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.app.main import create_app


TEST_PASSWORD = "MatKhau!123"
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


def create_test_user(
    role: UserRole,
    *,
    username: str | None = None,
    active: bool = True,
    lecturer_code: str | None = None,
) -> AppUserModel:
    resolved_username = username or role.value.lower()
    now = datetime.now(timezone.utc)
    with get_session_local()() as session:
        existing = session.scalar(
            select(AppUserModel).where(AppUserModel.username == resolved_username)
        )
        if existing is not None:
            return existing
        user = AppUserModel(
            username=resolved_username,
            display_name=f"Kiểm thử {role.value}",
            password_hash=TEST_PASSWORD_HASH,
            role=role.value,
            active=active,
            lecturer_code=lecturer_code,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.commit()
        return user


def authenticated_client(
    role: UserRole = UserRole.TRAINING_OFFICE,
    *,
    username: str | None = None,
    lecturer_code: str | None = None,
) -> TestClient:
    user = create_test_user(
        role,
        username=username,
        lecturer_code=lecturer_code,
    )
    client = TestClient(create_app())
    response = client.post(
        "/api/auth/login",
        json={"username": user.username, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return client
