"""add house events

Revision ID: d8a3b5c7e9f1
Revises: c7f2a9d4b1e8
Create Date: 2026-10-29 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "d8a3b5c7e9f1"
down_revision: str | Sequence[str] | None = "c7f2a9d4b1e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in (
            "HOUSE_ELECTED",
            "BLOC_GUIDED",
            "GUIDANCE_RULE_SET",
            "IMPEACHMENT_REQUESTED",
            "IMPEACHMENT_VOTED",
        ):
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres só sai recriando o tipo; os eventos ficam sem uso
    pass
