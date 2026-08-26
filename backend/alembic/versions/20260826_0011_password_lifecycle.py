"""Track accounts that must replace temporary passwords."""

from alembic import op
import sqlalchemy as sa


revision = "20260826_0011"
down_revision = "20260824_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "app_users",
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("app_users", "must_change_password", server_default=None)


def downgrade() -> None:
    op.drop_column("app_users", "must_change_password")
