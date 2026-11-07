"""add federation events

Revision ID: d1f6a3c8e2b7
Revises: c9d4f7a2e8b3
Create Date: 2026-11-07 15:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "d1f6a3c8e2b7"
down_revision: str | Sequence[str] | None = "c9d4f7a2e8b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in (
            "FEDERATION_PROPOSED",
            "FEDERATION_WITHDRAWN",
            "FEDERATION_ANSWERED",
            "FEDERATION_LEFT",
            "FEDERATION_ENDED",
        ):
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
