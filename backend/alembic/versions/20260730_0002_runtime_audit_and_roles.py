from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260730_0002"
down_revision = "20260730_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dataset_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("batch_code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("parent_batch_code", sa.String(length=50), nullable=True),
        sa.Column("snapshot_path", sa.Text(), nullable=False),
        sa.Column("manifest", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "schedule_change_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_code", sa.String(length=50), nullable=False, index=True),
        sa.Column("section_code", sa.String(length=80), nullable=False),
        sa.Column("scope", sa.String(length=40), nullable=False),
        sa.Column("previous_value", sa.JSON(), nullable=False),
        sa.Column("current_value", sa.JSON(), nullable=False),
        sa.Column("changed_by", sa.String(length=80), nullable=False),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "app_users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table("app_users")
    op.drop_table("schedule_change_logs")
    op.drop_table("dataset_snapshots")
