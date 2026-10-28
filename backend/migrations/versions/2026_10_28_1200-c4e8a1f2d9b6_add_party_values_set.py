"""add party values set and poll margin rule

Revision ID: c4e8a1f2d9b6
Revises: bf2cc83d1937
Create Date: 2026-10-28 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "c4e8a1f2d9b6"
down_revision: str | Sequence[str] | None = "bf2cc83d1937"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS 'PARTY_VALUES_SET'"
        )
    # As regras guardadas trazem todas as chaves das regras de hoje
    op.execute(
        "UPDATE simulations SET rules = rules || jsonb_build_object('poll_margin', true) "
        "WHERE NOT rules ? 'poll_margin'"
    )


def downgrade() -> None:
    op.execute("UPDATE simulations SET rules = rules - 'poll_margin'")
    # Valor de enum do Postgres só sai recriando o tipo; o evento fica sem uso
