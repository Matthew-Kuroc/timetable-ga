"""Add lecturer schedule-change request workflow and audit events."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260813_0007"
down_revision = "20260810_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedule_change_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("request_code", sa.String(length=50), nullable=False),
        sa.Column("official_timetable_id", sa.Integer(), nullable=False),
        sa.Column("requester_user_id", sa.Integer(), nullable=False),
        sa.Column("requester_username", sa.String(length=80), nullable=False),
        sa.Column("lecturer_code", sa.String(length=50), nullable=False),
        sa.Column("section_code", sa.String(length=80), nullable=False),
        sa.Column("occurrence_date", sa.Date(), nullable=False),
        sa.Column("request_type", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("proposed_date", sa.Date(), nullable=True),
        sa.Column("proposed_slot_code", sa.String(length=50), nullable=True),
        sa.Column("proposed_room_code", sa.String(length=50), nullable=True),
        sa.Column("current_snapshot", sa.JSON(), nullable=False),
        sa.Column("proposal_snapshot", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("expected_official_version", sa.Integer(), nullable=False),
        sa.Column("reviewer_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewer_username", sa.String(length=80), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["official_timetable_id"], ["official_timetables.id"]),
        sa.ForeignKeyConstraint(["requester_user_id"], ["app_users.id"]),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["app_users.id"]),
    )
    for column in (
        "request_code",
        "official_timetable_id",
        "requester_user_id",
        "lecturer_code",
        "section_code",
        "request_type",
        "status",
        "reviewer_user_id",
        "created_at",
    ):
        op.create_index(
            f"ix_schedule_change_requests_{column}",
            "schedule_change_requests",
            [column],
            unique=column == "request_code",
        )

    op.create_table(
        "schedule_change_request_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=True),
        sa.Column("to_status", sa.String(length=20), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_username", sa.String(length=80), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["request_id"], ["schedule_change_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["app_users.id"]),
    )
    for column in ("request_id", "action", "actor_user_id", "created_at"):
        op.create_index(
            f"ix_schedule_change_request_events_{column}",
            "schedule_change_request_events",
            [column],
            unique=False,
        )

    op.add_column("schedule_change_logs", sa.Column("request_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_schedule_change_logs_request_id",
        "schedule_change_logs",
        "schedule_change_requests",
        ["request_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_schedule_change_logs_request_id", "schedule_change_logs", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_schedule_change_logs_request_id", table_name="schedule_change_logs")
    op.drop_constraint("fk_schedule_change_logs_request_id", "schedule_change_logs", type_="foreignkey")
    op.drop_column("schedule_change_logs", "request_id")

    for column in ("created_at", "actor_user_id", "action", "request_id"):
        op.drop_index(f"ix_schedule_change_request_events_{column}", table_name="schedule_change_request_events")
    op.drop_table("schedule_change_request_events")

    for column in (
        "created_at",
        "reviewer_user_id",
        "status",
        "request_type",
        "section_code",
        "lecturer_code",
        "requester_user_id",
        "official_timetable_id",
        "request_code",
    ):
        op.drop_index(f"ix_schedule_change_requests_{column}", table_name="schedule_change_requests")
    op.drop_table("schedule_change_requests")
