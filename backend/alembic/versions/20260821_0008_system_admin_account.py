"""Mark the bootstrap administrator as a protected system account."""

from alembic import op
import sqlalchemy as sa


revision = "20260821_0008"
down_revision = "20260813_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "app_users",
        sa.Column("system_account", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("app_users", "system_account")
