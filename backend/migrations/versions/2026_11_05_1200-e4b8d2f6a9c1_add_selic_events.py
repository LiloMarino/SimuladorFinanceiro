"""add selic events

Revision ID: e4b8d2f6a9c1
Revises: d5a9e3c7b1f2
Create Date: 2026-11-05 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "e4b8d2f6a9c1"
down_revision: str | Sequence[str] | None = "d5a9e3c7b1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in ("SELIC_SET", "SELIC_DECIDED"):
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
