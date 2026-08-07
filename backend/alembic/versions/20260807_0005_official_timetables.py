from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260807_0005"
down_revision = "20260803_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ga_runs", sa.Column("payload", sa.JSON(), nullable=True))
    op.add_column("schedule_change_logs", sa.Column("official_code", sa.String(length=50), nullable=True))
    op.create_index("ix_schedule_change_logs_official_code", "schedule_change_logs", ["official_code"], unique=False)
    op.create_table(
        "official_timetables",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("official_code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("source_ga_run_id", sa.Integer(), sa.ForeignKey("ga_runs.id"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_official_timetables_official_code", "official_timetables", ["official_code"], unique=True)
    op.create_table(
        "schedule_segments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("official_timetable_id", sa.Integer(), sa.ForeignKey("official_timetables.id"), nullable=False),
        sa.Column("section_code", sa.String(length=80), nullable=False),
        sa.Column("effective_start_date", sa.Date(), nullable=False),
        sa.Column("effective_end_date", sa.Date(), nullable=False),
        sa.Column("room_code", sa.String(length=50), nullable=False),
        sa.Column("slot_code", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_schedule_segments_official_timetable_id", "schedule_segments", ["official_timetable_id"], unique=False)
    op.create_index("ix_schedule_segments_section_code", "schedule_segments", ["section_code"], unique=False)
    op.create_table(
        "makeup_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("official_timetable_id", sa.Integer(), sa.ForeignKey("official_timetables.id"), nullable=False),
        sa.Column("section_code", sa.String(length=80), nullable=False),
        sa.Column("original_missing_date", sa.Date(), nullable=True),
        sa.Column("makeup_date", sa.Date(), nullable=False),
        sa.Column("academic_week", sa.Integer(), nullable=False),
        sa.Column("room_code", sa.String(length=50), nullable=False),
        sa.Column("slot_code", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_makeup_sessions_official_timetable_id", "makeup_sessions", ["official_timetable_id"], unique=False)
    op.create_index("ix_makeup_sessions_section_code", "makeup_sessions", ["section_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_makeup_sessions_section_code", table_name="makeup_sessions")
    op.drop_index("ix_makeup_sessions_official_timetable_id", table_name="makeup_sessions")
    op.drop_table("makeup_sessions")
    op.drop_index("ix_schedule_segments_section_code", table_name="schedule_segments")
    op.drop_index("ix_schedule_segments_official_timetable_id", table_name="schedule_segments")
    op.drop_table("schedule_segments")
    op.drop_index("ix_official_timetables_official_code", table_name="official_timetables")
    op.drop_table("official_timetables")
    op.drop_index("ix_schedule_change_logs_official_code", table_name="schedule_change_logs")
    op.drop_column("schedule_change_logs", "official_code")
    op.drop_column("ga_runs", "payload")
