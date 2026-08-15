"""Add User model

Revision ID: 5fcbcb8e498f
Revises: 20260807_0005
Create Date: 2026-08-09 12:53:58.313350
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '5fcbcb8e498f'
down_revision = '20260807_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Legacy migration.
    # The current authentication system uses app_users,
    # so do not create/drop the users table here.
    pass


def downgrade() -> None:
    pass
