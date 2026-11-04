"""add gdp growth and unemployment series

Revision ID: d5a9e3c7b1f2
Revises: 82052494f0aa
Create Date: 2026-11-04 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "d5a9e3c7b1f2"
down_revision: str | Sequence[str] | None = "82052494f0aa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS 'GDP_GROWTH'")
        op.execute("ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS 'UNEMPLOYMENT'")


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; as linhas das séries saem
    op.execute(
        "DELETE FROM economic_indicator_history "
        "WHERE series IN ('GDP_GROWTH', 'UNEMPLOYMENT')"
    )
    op.execute("DELETE FROM fetch_log WHERE series IN ('GDP_GROWTH', 'UNEMPLOYMENT')")
