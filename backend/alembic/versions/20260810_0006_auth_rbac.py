"""Add authentication sessions, account audit logs and complete app users."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260810_0006"
down_revision = "20260807_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("app_users", sa.Column("password_hash", sa.Text(), nullable=True))
    op.add_column("app_users", sa.Column("lecturer_code", sa.String(length=50), nullable=True))
    op.add_column(
        "app_users",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column(
        "app_users",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("app_users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    # The old table was only a placeholder and had no usable credentials. Keep
    # any legacy rows for traceability, but make them impossible to authenticate.
    op.execute(
        "UPDATE app_users "
        "SET active = false, password_hash = '!legacy-account-without-password!' "
        "WHERE password_hash IS NULL"
    )
    op.alter_column("app_users", "password_hash", existing_type=sa.Text(), nullable=False)
    op.create_index("ix_app_users_lecturer_code", "app_users", ["lecturer_code"], unique=True)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)
    op.create_index("ix_auth_sessions_token_hash", "auth_sessions", ["token_hash"], unique=True)
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"], unique=False)

    op.create_table(
        "account_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_username", sa.String(length=80), nullable=True),
        sa.Column("target_username", sa.String(length=80), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["actor_user_id"], ["app_users.id"]),
        sa.ForeignKeyConstraint(["target_user_id"], ["app_users.id"]),
    )
    op.create_index("ix_account_audit_logs_actor_user_id", "account_audit_logs", ["actor_user_id"], unique=False)
    op.create_index("ix_account_audit_logs_target_user_id", "account_audit_logs", ["target_user_id"], unique=False)
    op.create_index("ix_account_audit_logs_target_username", "account_audit_logs", ["target_username"], unique=False)
    op.create_index("ix_account_audit_logs_action", "account_audit_logs", ["action"], unique=False)
    op.create_index("ix_account_audit_logs_created_at", "account_audit_logs", ["created_at"], unique=False)

    # Official timetable changes intentionally have no GA run code.
    op.alter_column(
        "schedule_change_logs",
        "run_code",
        existing_type=sa.String(length=50),
        nullable=True,
    )


def downgrade() -> None:
    op.execute(
        "UPDATE schedule_change_logs "
        "SET run_code = official_code "
        "WHERE run_code IS NULL AND official_code IS NOT NULL"
    )
    op.alter_column(
        "schedule_change_logs",
        "run_code",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.drop_index("ix_account_audit_logs_created_at", table_name="account_audit_logs")
    op.drop_index("ix_account_audit_logs_action", table_name="account_audit_logs")
    op.drop_index("ix_account_audit_logs_target_username", table_name="account_audit_logs")
    op.drop_index("ix_account_audit_logs_target_user_id", table_name="account_audit_logs")
    op.drop_index("ix_account_audit_logs_actor_user_id", table_name="account_audit_logs")
    op.drop_table("account_audit_logs")

    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_token_hash", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index("ix_app_users_lecturer_code", table_name="app_users")
    op.drop_column("app_users", "last_login_at")
    op.drop_column("app_users", "updated_at")
    op.drop_column("app_users", "created_at")
    op.drop_column("app_users", "lecturer_code")
    op.drop_column("app_users", "password_hash")
