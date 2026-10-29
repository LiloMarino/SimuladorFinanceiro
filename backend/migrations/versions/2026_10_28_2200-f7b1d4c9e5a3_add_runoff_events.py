"""add runoff events

Revision ID: f7b1d4c9e5a3
Revises: e6a0c3b8d4f2
Create Date: 2026-10-28 22:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "f7b1d4c9e5a3"
down_revision: str | Sequence[str] | None = "e6a0c3b8d4f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in ("RUNOFF_ENDORSED", "RUNOFF_CONTRIBUTION", "RUNOFF_POLL"):
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
