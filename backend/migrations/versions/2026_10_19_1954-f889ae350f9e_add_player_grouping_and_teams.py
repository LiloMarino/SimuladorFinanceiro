"""add player grouping and teams

Revision ID: f889ae350f9e
Revises: c0b110c6a2e8
Create Date: 2026-10-19 19:54:39.472598
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f889ae350f9e"
down_revision: str | Sequence[str] | None = "c0b110c6a2e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # add_column não cria o tipo ENUM nativo: ele nasce antes das colunas
    sa.Enum("INDIVIDUAL", "TEAMS", name="player_grouping").create(op.get_bind())
    sa.Enum("COLOR", "NUMBER", name="team_naming").create(op.get_bind())
    op.add_column(
        "simulation_players", sa.Column("team", sa.SmallInteger(), nullable=True)
    )
    op.create_check_constraint(
        "simulation_players_team_check", "simulation_players", "team BETWEEN 1 AND 10"
    )
    op.add_column(
        "simulations",
        sa.Column(
            "player_grouping",
            sa.Enum("INDIVIDUAL", "TEAMS", name="player_grouping", create_type=False),
            server_default=sa.text("'INDIVIDUAL'"),
            nullable=False,
        ),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "team_naming",
            sa.Enum("COLOR", "NUMBER", name="team_naming", create_type=False),
            server_default=sa.text("'COLOR'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("simulations", "team_naming")
    op.drop_column("simulations", "player_grouping")
    op.drop_constraint(
        "simulation_players_team_check", "simulation_players", type_="check"
    )
    op.drop_column("simulation_players", "team")
    sa.Enum(name="team_naming").drop(op.get_bind())
    sa.Enum(name="player_grouping").drop(op.get_bind())
