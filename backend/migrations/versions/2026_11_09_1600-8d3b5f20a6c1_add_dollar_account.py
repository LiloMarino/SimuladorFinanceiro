"""add dollar account

Revision ID: 8d3b5f20a6c1
Revises: 4c9e1a7d52b8
Create Date: 2026-11-09 16:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8d3b5f20a6c1"
down_revision: str | Sequence[str] | None = "4c9e1a7d52b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE investment_type ADD VALUE IF NOT EXISTS 'DOLLAR_ACCOUNT'")
    op.execute("ALTER TYPE rate_type ADD VALUE IF NOT EXISTS 'FED_FUNDS'")
    op.add_column(
        "event_fixed_income", sa.Column("fx_rate", sa.Numeric(20, 8), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("event_fixed_income", "fx_rate")
    # O PostgreSQL não remove valor de enum: os valores novos ficam nos tipos
