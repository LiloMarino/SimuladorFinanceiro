"""add simulation is_backtest

Revision ID: 4bf5950342b9
Revises: c5a81e3f7d29
Create Date: 2026-10-24 14:54:55.336485
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4bf5950342b9"
down_revision: str | Sequence[str] | None = "c5a81e3f7d29"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column(
            "is_backtest", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("simulations", "is_backtest")
