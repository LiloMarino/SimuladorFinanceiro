"""add deal events

Revision ID: e9b4c6d8f0a2
Revises: d8a3b5c7e9f1
Create Date: 2026-10-29 22:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "e9b4c6d8f0a2"
down_revision: str | Sequence[str] | None = "d8a3b5c7e9f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in (
            "DEAL_PROPOSED",
            "DEAL_ANSWERED",
            "DEAL_WITHDRAWN",
            "DEAL_BROKEN",
        ):
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
