"""add government budget: initial account rule and risk premium on fixed income

Revision ID: c7f2a9d4b1e8
Revises: b9d3f6a1c7e5
Create Date: 2026-10-29 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c7f2a9d4b1e8"
down_revision: str | Sequence[str] | None = "b9d3f6a1c7e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fixed_income_asset",
        sa.Column("risk_premium", sa.Numeric(precision=20, scale=6), nullable=True),
    )
    # As regras guardadas trazem todas as chaves das regras de hoje
    op.execute(
        "UPDATE simulations SET rules = rules || jsonb_build_object('initial_account', 'PLAYABLE') "
        "WHERE NOT rules ? 'initial_account'"
    )


def downgrade() -> None:
    op.execute("UPDATE simulations SET rules = rules - 'initial_account'")
    op.drop_column("fixed_income_asset", "risk_premium")
