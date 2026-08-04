"""Add human-readable metadata and confirmation timestamps to import batches."""

from alembic import op
import sqlalchemy as sa


revision = "20260803_0004"
down_revision = "20260731_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("import_batches", sa.Column("display_name", sa.String(length=120), nullable=True))
    op.add_column("import_batches", sa.Column("semester", sa.String(length=50), nullable=True))
    op.add_column("import_batches", sa.Column("academic_year", sa.String(length=30), nullable=True))
    op.add_column("import_batches", sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("import_batches", sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE import_batches SET display_name = batch_code WHERE display_name IS NULL")
    op.alter_column("import_batches", "display_name", nullable=False)


def downgrade() -> None:
    op.drop_column("import_batches", "confirmed_at")
    op.drop_column("import_batches", "version_number")
    op.drop_column("import_batches", "academic_year")
    op.drop_column("import_batches", "semester")
    op.drop_column("import_batches", "display_name")
