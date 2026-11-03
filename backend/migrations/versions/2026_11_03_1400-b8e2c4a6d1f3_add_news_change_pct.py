"""add news change pct

Revision ID: b8e2c4a6d1f3
Revises: a3d7f1c9e5b2
Create Date: 2026-11-03 14:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b8e2c4a6d1f3"
down_revision: str | Sequence[str] | None = "a3d7f1c9e5b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("news", sa.Column("change_pct", sa.Numeric(8, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("news", "change_pct")
