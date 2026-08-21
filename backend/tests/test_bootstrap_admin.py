from __future__ import annotations

from sqlalchemy import select

from backend.app.cli import bootstrap_admin as bootstrap_cli
from backend.app.core.security import verify_password
from backend.app.db.models import AccountAuditModel, AppUserModel
from backend.app.db.session import get_session_local
from backend.app.services.user_service import LEGACY_PASSWORD_SENTINEL


def test_bootstrap_admin_prompts_for_password_and_runs_only_once(monkeypatch, capsys) -> None:
    passwords = iter(["MatKhauQuanTri!123", "MatKhauQuanTri!123"])
    monkeypatch.setattr(bootstrap_cli.getpass, "getpass", lambda _prompt: next(passwords))

    result = bootstrap_cli.main(["--username", "admin", "--display-name", "Quản trị viên"])

    assert result == 0
    output = capsys.readouterr()
    assert "MatKhauQuanTri!123" not in output.out + output.err
    with get_session_local()() as session:
        user = session.scalar(select(AppUserModel).where(AppUserModel.username == "admin"))
        assert user is not None
        assert user.role == "ADMIN"
        assert user.system_account is True
        assert verify_password("MatKhauQuanTri!123", user.password_hash)

    passwords = iter(["MatKhauKhac!123", "MatKhauKhac!123"])
    monkeypatch.setattr(bootstrap_cli.getpass, "getpass", lambda _prompt: next(passwords))
    assert bootstrap_cli.main(["--username", "admin2", "--display-name", "Admin 2"]) == 1


def test_bootstrap_admin_uses_central_password_policy(monkeypatch) -> None:
    passwords = iter(["ngan", "ngan"])
    monkeypatch.setattr(bootstrap_cli.getpass, "getpass", lambda _prompt: next(passwords))

    assert bootstrap_cli.main(["--username", "admin", "--display-name", "Admin"]) == 1
    with get_session_local()() as session:
        assert session.scalar(select(AppUserModel)) is None


def test_bootstrap_admin_recovers_legacy_inactive_admin(monkeypatch) -> None:
    with get_session_local()() as session:
        legacy = AppUserModel(
            username="legacy-admin",
            display_name="Tài khoản legacy",
            password_hash=LEGACY_PASSWORD_SENTINEL,
            role="ADMIN",
            active=False,
        )
        session.add(legacy)
        session.commit()
        legacy_id = legacy.id

    passwords = iter(["MatKhauKhoiPhuc!123", "MatKhauKhoiPhuc!123"])
    monkeypatch.setattr(bootstrap_cli.getpass, "getpass", lambda _prompt: next(passwords))

    result = bootstrap_cli.main(
        ["--username", "legacy-admin", "--display-name", "Quản trị viên khôi phục"]
    )

    assert result == 0
    with get_session_local()() as session:
        recovered = session.get(AppUserModel, legacy_id)
        assert recovered is not None
        assert recovered.active is True
        assert recovered.display_name == "Quản trị viên khôi phục"
        assert verify_password("MatKhauKhoiPhuc!123", recovered.password_hash)
        audit = session.scalar(
            select(AccountAuditModel).where(AccountAuditModel.action == "ADMIN_RECOVERED")
        )
        assert audit is not None
        assert audit.target_user_id == legacy_id
