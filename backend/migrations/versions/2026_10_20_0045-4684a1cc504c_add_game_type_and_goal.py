"""add game type and goal

Revision ID: 4684a1cc504c
Revises: f889ae350f9e
Create Date: 2026-10-20 00:45:21.985989
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4684a1cc504c"
down_revision: str | Sequence[str] | None = "f889ae350f9e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # add_column não cria o tipo ENUM nativo: ele nasce antes da coluna
    sa.Enum("CLASSIC", "GOAL_RACE", "FINANCIAL_INDEPENDENCE", name="game_type").create(
        op.get_bind()
    )
    op.add_column(
        "simulations",
        sa.Column(
            "game_type",
            sa.Enum(
                "CLASSIC",
                "GOAL_RACE",
                "FINANCIAL_INDEPENDENCE",
                name="game_type",
                create_type=False,
            ),
            server_default=sa.text("'CLASSIC'"),
            nullable=False,
        ),
    )
    # Partidas salvas ganham a meta padrão, 10x o saldo inicial
    op.add_column(
        "simulations",
        sa.Column("goal_net_worth", sa.Numeric(precision=20, scale=6), nullable=True),
    )
    op.execute("UPDATE simulations SET goal_net_worth = starting_cash * 10")
    op.alter_column("simulations", "goal_net_worth", nullable=False)


def downgrade() -> None:
    op.drop_column("simulations", "goal_net_worth")
    op.drop_column("simulations", "game_type")
    sa.Enum(name="game_type").drop(op.get_bind())
