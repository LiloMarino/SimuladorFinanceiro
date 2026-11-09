"""add fed funds series

Revision ID: 4c9e1a7d52b8
Revises: 1f97f957f270
Create Date: 2026-11-09 15:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "4c9e1a7d52b8"
down_revision: str | Sequence[str] | None = "1f97f957f270"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Todas as tabelas que usam o enum compartilham o tipo indicator_series
    op.execute("ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS 'FED_FUNDS'")


def downgrade() -> None:
    # O PostgreSQL não remove valor de enum: o valor novo fica no tipo
    pass
