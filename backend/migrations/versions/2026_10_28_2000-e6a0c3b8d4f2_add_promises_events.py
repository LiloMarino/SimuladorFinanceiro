"""add promises events

Revision ID: e6a0c3b8d4f2
Revises: d5f9b2a7c3e1
Create Date: 2026-10-28 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "e6a0c3b8d4f2"
down_revision: str | Sequence[str] | None = "d5f9b2a7c3e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in ("PROMISES_SET", "PROMISES_WEIGHED", "PROMISES_SETTLED"):
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
