"""add parties prepared event

Revision ID: f1c5d7e9a3b4
Revises: 083fed15fa40
Create Date: 2026-10-30 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "f1c5d7e9a3b4"
down_revision: str | Sequence[str] | None = "083fed15fa40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS 'PARTIES_PREPARED'"
        )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
