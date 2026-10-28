"""add campaign action event and cashflow type

Revision ID: d5f9b2a7c3e1
Revises: c4e8a1f2d9b6
Create Date: 2026-10-28 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "d5f9b2a7c3e1"
down_revision: str | Sequence[str] | None = "c4e8a1f2d9b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN_ACTION'"
        )
        op.execute(
            "ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN_ACTION'"
        )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
