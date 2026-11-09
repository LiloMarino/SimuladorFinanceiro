"""add focus series

Revision ID: 1f97f957f270
Revises: b7d2e94a1c35
Create Date: 2026-11-09 12:02:39.717441
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "1f97f957f270"
down_revision: str | Sequence[str] | None = "b7d2e94a1c35"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FOCUS_SERIES = ("FOCUS_SELIC", "FOCUS_IPCA", "FOCUS_GDP", "FOCUS_FX")


def upgrade() -> None:
    # Todas as tabelas que usam o enum compartilham o tipo indicator_series
    for series in FOCUS_SERIES:
        op.execute(f"ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS '{series}'")


def downgrade() -> None:
    # O PostgreSQL não remove valor de enum: os valores novos ficam no tipo
    pass
