from __future__ import annotations

import shutil

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.core.security import verify_password
from backend.app.db.models import AccountAuditModel, AppUserModel
from backend.app.db.session import get_session_local
from backend.app.domain.auth import UserRole
from backend.app.main import create_app
from backend.tests.auth_helpers import TEST_PASSWORD, authenticated_client
from backend.app.services import runtime_store


def test_admin_lecturer_catalog_and_account_binding_use_confirmed_batch(tmp_path, monkeypatch) -> None:
    source = tmp_path / "source"
    shutil.copytree("data/samples/small", source)
    runtime_root = tmp_path / "runtime"
    monkeypatch.setattr(runtime_store, "RUNTIME_ROOT", runtime_root)
    monkeypatch.setattr(runtime_store, "BATCH_ROOT", runtime_root / "batches")
    monkeypatch.setattr(runtime_store, "RUN_ROOT", runtime_root / "runs")
    batch = runtime_store.create_confirmed_batch(source)

    admin = authenticated_client(UserRole.ADMIN, username="admin_catalog")
    catalog = admin.get("/api/admin/lecturers")
    assert catalog.status_code == 200
    assert catalog.json()["batch_code"] == batch["batch_code"]
    assert catalog.json()["batch_display_name"] == batch["display_name"]
    assert {item["lecturer_code"] for item in catalog.json()["lecturers"]} >= {"GV001"}

    invalid = admin.post(
        "/api/admin/users",
        json={
            "username": "gv.invalid.catalog",
            "display_name": "Giảng viên sai mã",
            "password": TEST_PASSWORD,
            "role": "LECTURER",
            "lecturer_code": "GV999",
        },
    )
    assert invalid.status_code == 422
    first = admin.post("/api/admin/users", json={"username": "gv001.account", "display_name": "Giảng viên GV001", "password": TEST_PASSWORD, "role": "LECTURER", "lecturer_code": "GV001"})
    second = admin.post("/api/admin/users", json={"username": "gv002.account", "display_name": "Giảng viên GV002", "password": TEST_PASSWORD, "role": "LECTURER", "lecturer_code": "GV002"})
    assert first.status_code == 201
    assert second.status_code == 201
    duplicate_code = admin.post("/api/admin/users", json={"username": "gv001.duplicate", "display_name": "Giảng viên trùng mã", "password": TEST_PASSWORD, "role": "LECTURER", "lecturer_code": "GV001"})
    assert duplicate_code.status_code == 409
    assert "không tồn tại" in invalid.json()["detail"]


def test_role_matrix_is_enforced_by_backend() -> None:
    anonymous = TestClient(create_app())
    admin = authenticated_client(UserRole.ADMIN, username="admin_matrix")
    training_office = authenticated_client(UserRole.TRAINING_OFFICE, username="office_matrix")
    lecturer = authenticated_client(
        UserRole.LECTURER,
        username="lecturer_matrix",
        lecturer_code="GV001",
    )

    assert anonymous.get("/api/batches").status_code == 401
    assert admin.get("/api/batches").status_code == 403
    assert lecturer.get("/api/batches").status_code == 403
    assert training_office.get("/api/batches").status_code == 200

    assert admin.get("/api/admin/users").status_code == 200
    assert training_office.get("/api/admin/users").status_code == 403
    assert lecturer.get("/api/admin/users").status_code == 403

    assert lecturer.get("/api/lecturer/timetable", params={"week": 1}).status_code == 200
    assert admin.get("/api/lecturer/timetable", params={"week": 1}).status_code == 403
    assert training_office.get("/api/lecturer/timetable", params={"week": 1}).status_code == 403
    assert lecturer.get("/api/ga/official-timetables").status_code == 403


def test_admin_can_manage_accounts_and_audit_without_exposing_passwords() -> None:
    admin = authenticated_client(UserRole.ADMIN, username="admin_users")
    raw_password = "MatKhauGiangVien!123"

    created = admin.post(
        "/api/admin/users",
        json={
            "username": "gv.moi",
            "display_name": "Giảng viên mới",
            "password": raw_password,
            "role": "LECTURER",
            "lecturer_code": "GV001",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["user"]["id"]
    assert admin.post(
        "/api/admin/users",
        json={
            "username": "gv.moi",
            "display_name": "Trùng",
            "password": raw_password,
            "role": "TRAINING_OFFICE",
        },
    ).status_code == 409

    with get_session_local()() as session:
        user = session.get(AppUserModel, user_id)
        assert user is not None
        assert user.password_hash != raw_password
        assert verify_password(raw_password, user.password_hash)

    updated = admin.patch(f"/api/admin/users/{user_id}", json={"active": False})
    assert updated.status_code == 200
    assert updated.json()["user"]["active"] is False
    rejected_login = TestClient(create_app()).post(
        "/api/auth/login",
        json={"username": "gv.moi", "password": raw_password},
    )
    assert rejected_login.status_code == 401

    audit = admin.get("/api/admin/audit-logs")
    assert audit.status_code == 200
    assert {item["action"] for item in audit.json()["audit_logs"]} >= {
        "USER_CREATED",
        "USER_UPDATED",
    }
    assert raw_password not in audit.text
    assert "password_hash" not in audit.text
    with get_session_local()() as session:
        created_log = session.scalar(
            select(AccountAuditModel).where(AccountAuditModel.action == "USER_CREATED")
        )
        assert created_log is not None
        assert created_log.actor_username == "admin_users"


def test_admin_and_training_office_roles_are_singletons() -> None:
    admin = authenticated_client(UserRole.ADMIN, username="admin_singleton")
    duplicate_admin = admin.post(
        "/api/admin/users",
        json={"username": "admin.second", "display_name": "Admin 2", "password": TEST_PASSWORD, "role": "ADMIN"},
    )
    first_office = admin.post(
        "/api/admin/users",
        json={"username": "office.first", "display_name": "Phòng Đào tạo 1", "password": TEST_PASSWORD, "role": "TRAINING_OFFICE"},
    )
    duplicate_office = admin.post(
        "/api/admin/users",
        json={"username": "office.second", "display_name": "Phòng Đào tạo 2", "password": TEST_PASSWORD, "role": "TRAINING_OFFICE"},
    )
    assert duplicate_admin.status_code == 409
    assert first_office.status_code == 201
    assert duplicate_office.status_code == 409


def test_system_admin_account_cannot_be_edited_or_disabled() -> None:
    admin = authenticated_client(UserRole.ADMIN, username="admin_protected")
    with get_session_local()() as session:
        user = session.scalar(select(AppUserModel).where(AppUserModel.username == "admin_protected"))
        assert user is not None
        user.system_account = True
        session.commit()
        user_id = user.id

    response = admin.patch(f"/api/admin/users/{user_id}", json={"active": False, "display_name": "Tên mới"})
    assert response.status_code == 422
    assert "cố định" in response.json()["detail"]
