"""Fix merge conflict migration

Revision ID: 8948beecdf64
Revises: 20260813_0007, 5fcbcb8e498f
Create Date: 2026-08-14 23:36:41.477744
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa



revision = '8948beecdf64'
down_revision = ('20260813_0007', '5fcbcb8e498f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
