"""Store declared multi-meeting course sections and meeting identities."""

from alembic import op
import sqlalchemy as sa


revision = "20260824_0010"
down_revision = "20260821_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("course_sections", sa.Column("second_session_periods", sa.Integer(), nullable=True))
    op.add_column(
        "schedule_assignments",
        sa.Column("meeting_number", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_constraint("uq_schedule_assignments_run_section", "schedule_assignments", type_="unique")
    op.create_unique_constraint(
        "uq_schedule_assignments_run_section_meeting",
        "schedule_assignments",
        ["ga_run_id", "course_section_id", "meeting_number"],
    )
    op.alter_column("schedule_assignments", "meeting_number", server_default=None)


def downgrade() -> None:
    op.drop_constraint("uq_schedule_assignments_run_section_meeting", "schedule_assignments", type_="unique")
    op.create_unique_constraint(
        "uq_schedule_assignments_run_section",
        "schedule_assignments",
        ["ga_run_id", "course_section_id"],
    )
    op.drop_column("schedule_assignments", "meeting_number")
    op.drop_column("course_sections", "second_session_periods")
