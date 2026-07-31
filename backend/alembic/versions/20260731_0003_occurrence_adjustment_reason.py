"""Store the reason required for direct timetable adjustments."""

from alembic import op
import sqlalchemy as sa


revision = "20260731_0003"
down_revision = "20260730_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("schedule_change_logs", sa.Column("reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("schedule_change_logs", "reason")
