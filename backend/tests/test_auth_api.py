from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.core.security import (
    PASSWORD_ITERATIONS,
    hash_password,
    verify_password,
)
from backend.app.db.models import AccountAuditModel, AuthSessionModel
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.app.main import create_app
from backend.tests.auth_helpers import TEST_PASSWORD, authenticated_client, create_test_user


def test_password_hash_uses_pbkdf2_with_individual_salts() -> None:
    first = hash_password(TEST_PASSWORD)
    second = hash_password(TEST_PASSWORD)

    assert first != TEST_PASSWORD
    assert first != second
    assert first.startswith(f"pbkdf2_sha256${PASSWORD_ITERATIONS}$")
    assert verify_password(TEST_PASSWORD, first)
    assert not verify_password("SaiMatKhau", first)


def test_login_me_and_logout_revoke_the_session() -> None:
    user = create_test_user(UserRole.ADMIN, username="quantri")
    client = TestClient(create_app())

    login = client.post(
        "/api/auth/login",
        json={"username": "  QUANTRI ", "password": TEST_PASSWORD},
    )

    assert login.status_code == 200
    assert login.json()["user"]["id"] == user.id
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=lax" in login.headers["set-cookie"]
    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def test_bearer_token_is_supported_and_expired_session_is_rejected() -> None:
    create_test_user(UserRole.TRAINING_OFFICE, username="phongdaotao")
    login_client = TestClient(create_app())
    login = login_client.post(
        "/api/auth/login",
        json={"username": "phongdaotao", "password": TEST_PASSWORD},
    )
    token = login_client.cookies.get("timetable_session")
    assert token
    bearer_client = TestClient(create_app())
    assert bearer_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 200

    with get_session_local()() as session:
        auth_session = session.scalar(select(AuthSessionModel))
        assert auth_session is not None
        auth_session.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        session.commit()
    assert bearer_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 401
    assert bearer_client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 200


def test_failed_and_inactive_logins_are_safe_and_unauthenticated_in_audit() -> None:
    create_test_user(UserRole.LECTURER, username="giangvien", active=False, lecturer_code="GV001")
    client = TestClient(create_app())

    unknown = client.post(
        "/api/auth/login",
        json={"username": "khongtonTai", "password": TEST_PASSWORD},
    )
    inactive = client.post(
        "/api/auth/login",
        json={"username": "giangvien", "password": TEST_PASSWORD},
    )

    assert unknown.status_code == inactive.status_code == 401
    assert unknown.json()["detail"] == inactive.json()["detail"]
    with get_session_local()() as session:
        failures = session.scalars(
            select(AccountAuditModel).where(AccountAuditModel.action == "LOGIN_FAILED")
        ).all()
        assert len(failures) == 2
        assert all(item.actor_user_id is None and item.actor_username is None for item in failures)


def test_temporary_password_must_be_changed_before_normal_portal() -> None:
    create_test_user(UserRole.ADMIN, username="admin_temp")
    admin_client = authenticated_client(UserRole.ADMIN, username="admin_temp")
    created = admin_client.post(
        "/api/admin/users",
        json={"username": "gv.temp", "display_name": "Giang vien tam", "password": TEST_PASSWORD, "role": "LECTURER", "lecturer_code": "GV001"},
    )
    assert created.status_code == 201
    lecturer = TestClient(create_app())
    login = lecturer.post("/api/auth/login", json={"username": "gv.temp", "password": TEST_PASSWORD})
    assert login.status_code == 200
    assert login.json()["user"]["must_change_password"] is True
    assert lecturer.get("/api/lecturer/timetable", params={"week": 1}).status_code == 403
    changed = lecturer.post("/api/auth/change-password", json={"current_password": TEST_PASSWORD, "new_password": "MatKhauMoi!123"})
    assert changed.status_code == 200
    assert lecturer.get("/api/auth/me").status_code == 401
    relogin = lecturer.post("/api/auth/login", json={"username": "gv.temp", "password": "MatKhauMoi!123"})
    assert relogin.status_code == 200
    assert relogin.json()["user"]["must_change_password"] is False
