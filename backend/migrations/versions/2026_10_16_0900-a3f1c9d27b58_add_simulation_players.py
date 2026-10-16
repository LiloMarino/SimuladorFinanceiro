"""add simulation players

Revision ID: a3f1c9d27b58
Revises: d967ce5268c2
Create Date: 2026-10-16 09:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a3f1c9d27b58"
down_revision: str | Sequence[str] | None = "d967ce5268c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "simulation_players",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("color", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="simulation_players_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="simulation_players_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id", "user_id", name="simulation_players_pkey"
        ),
        sa.UniqueConstraint(
            "simulation_id", "color", name="simulation_players_simulation_id_color_key"
        ),
    )

    # As partidas salvas antes da tabela deduziam os participantes dos eventos:
    # cada um ganha a cor da própria posição na sala (chart-1 a chart-10)
    op.execute(
        """
        INSERT INTO simulation_players (simulation_id, user_id, color)
        SELECT simulation_id, user_id, 'chart-' || position
        FROM (
            SELECT
                simulation_id,
                user_id,
                row_number() OVER (PARTITION BY simulation_id ORDER BY user_id) AS position
            FROM (
                SELECT simulation_id, user_id FROM event_cashflow
                UNION
                SELECT simulation_id, user_id FROM snapshots
            ) AS participants
        ) AS ranked
        WHERE position <= 10
        """
    )


def downgrade() -> None:
    op.drop_table("simulation_players")
