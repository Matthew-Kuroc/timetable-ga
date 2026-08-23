"""Protect the existing bootstrap administrator after the system-account migration."""

from alembic import op

revision = "20260821_0009"
down_revision = "20260821_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE app_users
        SET system_account = TRUE
        WHERE id = (
            SELECT MIN(id) FROM app_users WHERE role = 'ADMIN'
        )
        """
    )


def downgrade() -> None:
    op.execute("UPDATE app_users SET system_account = FALSE WHERE system_account = TRUE")
