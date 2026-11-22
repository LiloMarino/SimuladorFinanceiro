"""snapshot locked balance

Revision ID: b3d7f1a8c264
Revises: a9c2e5b7d314
Create Date: 2026-11-22 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3d7f1a8c264"
down_revision: str | Sequence[str] | None = "a9c2e5b7d314"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "snapshots",
        sa.Column(
            "total_locked",
            sa.Numeric(precision=20, scale=6),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("snapshots", "total_locked")
