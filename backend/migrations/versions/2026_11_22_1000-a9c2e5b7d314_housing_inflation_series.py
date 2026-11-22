"""housing inflation series

Revision ID: a9c2e5b7d314
Revises: f4b7c2d9a1e6
Create Date: 2026-11-22 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a9c2e5b7d314"
down_revision: str | Sequence[str] | None = "f4b7c2d9a1e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A ordem dos valores segue a do enum do Python
INDICATOR_SERIES = ("IVG_R", "IGP_M", "TR")


def upgrade() -> None:
    # Todas as tabelas que usam o enum compartilham o tipo indicator_series
    for series in INDICATOR_SERIES:
        op.execute(f"ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS '{series}'")


def downgrade() -> None:
    # O PostgreSQL não remove valor de enum: os valores novos ficam no tipo
    pass
