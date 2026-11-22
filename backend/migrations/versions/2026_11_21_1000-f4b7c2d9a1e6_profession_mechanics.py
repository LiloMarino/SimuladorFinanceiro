"""profession mechanics

Revision ID: f4b7c2d9a1e6
Revises: e2a9c4b7d531
Create Date: 2026-11-21 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f4b7c2d9a1e6"
down_revision: str | Sequence[str] | None = "e2a9c4b7d531"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profession_states",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id", "user_id"],
            ["simulation_players.simulation_id", "simulation_players.user_id"],
            name="profession_states_player_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id", "user_id", name="profession_states_pkey"
        ),
    )
    op.create_table(
        "profession_periods",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("profession", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id", "user_id"],
            ["simulation_players.simulation_id", "simulation_players.user_id"],
            name="profession_periods_player_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id", "user_id", "start_date", name="profession_periods_pkey"
        ),
    )
    # O estado de toda profissão existente é o inicial, que não guarda nada
    op.execute(
        """
        INSERT INTO profession_states (simulation_id, user_id, state)
        SELECT simulation_id, user_id, '{}'::jsonb FROM simulation_players
        """
    )
    # Cada jogador já na partida exerce a profissão dele desde o início dela; a regra
    # sem data de início abre o período no começo dos tempos, que cobre a partida toda
    op.execute(
        """
        INSERT INTO profession_periods (simulation_id, user_id, start_date, profession)
        SELECT p.simulation_id,
               p.user_id,
               COALESCE((s.rules ->> 'start_date')::date, DATE '1970-01-01'),
               COALESCE(p.profession, 'CLT')
        FROM simulation_players p
        JOIN simulations s ON s.id = p.simulation_id
        """
    )


def downgrade() -> None:
    op.drop_table("profession_periods")
    op.drop_table("profession_states")
