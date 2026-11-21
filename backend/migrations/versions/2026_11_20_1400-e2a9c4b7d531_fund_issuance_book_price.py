"""fund issuance book price

Revision ID: e2a9c4b7d531
Revises: c5f1a8d3e927
Create Date: 2026-11-20 14:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e2a9c4b7d531"
down_revision: str | Sequence[str] | None = "c5f1a8d3e927"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fund_issuances",
        sa.Column("book_price", sa.Numeric(precision=20, scale=6), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("fund_issuances", "book_price")
