"""add crypto asset class

Revision ID: 9b2d7c41e5a3
Revises: 4e1f9a8d6b20
Create Date: 2026-10-23 17:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9b2d7c41e5a3"
down_revision: str | Sequence[str] | None = "4e1f9a8d6b20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE asset_class ADD VALUE IF NOT EXISTS 'CRYPTO'")
    op.alter_column(
        "event_equity",
        "quantity",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=20, scale=8),
        existing_nullable=False,
    )
    op.alter_column(
        "strategy_log",
        "quantity",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=20, scale=8),
        existing_nullable=True,
    )


def downgrade() -> None:
    # O Postgres não remove valor de ENUM: a classe nova fica, sem ativos
    op.execute("UPDATE stock SET asset_class = 'STOCK' WHERE asset_class = 'CRYPTO'")
    op.alter_column(
        "strategy_log",
        "quantity",
        existing_type=sa.Numeric(precision=20, scale=8),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="round(quantity)::integer",
    )
    op.alter_column(
        "event_equity",
        "quantity",
        existing_type=sa.Numeric(precision=20, scale=8),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="round(quantity)::integer",
    )
