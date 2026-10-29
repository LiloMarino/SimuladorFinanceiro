"""add newsroom news types

Revision ID: b9d3f6a1c7e5
Revises: d6a28e609e11
Create Date: 2026-10-29 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "b9d3f6a1c7e5"
down_revision: str | Sequence[str] | None = "d6a28e609e11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEWSROOM_TYPES = (
    "COPOM_DECISION",
    "MONTHLY_INFLATION",
    "IBOVESPA_EXTREME",
    "STRONG_MOVE",
    "WEEK_HIGH",
    "HISTORICAL_MILESTONE",
)


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in NEWSROOM_TYPES:
            op.execute(f"ALTER TYPE news_type ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; as manchetes ficam sem uso
    pass
