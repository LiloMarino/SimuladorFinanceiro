"""add fixed income assistances

Revision ID: e5d2a9b7c314
Revises: c41a7d2e5b90
Create Date: 2026-10-21 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5d2a9b7c314"
down_revision: str | Sequence[str] | None = "c41a7d2e5b90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column(
            "show_equivalent_rate",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "show_maturity_projection",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("simulations", "show_maturity_projection")
    op.drop_column("simulations", "show_equivalent_rate")
