"""move simulation rules to json

Revision ID: b7d41e9c3a58
Revises: 5836e0819ac7
Create Date: 2026-10-25 19:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7d41e9c3a58"
down_revision: str | Sequence[str] | None = "5836e0819ac7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

VICTORY_CRITERION = postgresql.ENUM(
    "SCORE", "RETURN", "NETWORTH", "SHARPE", name="victory_criterion", create_type=False
)
GAME_TYPE = postgresql.ENUM(
    "CLASSIC",
    "GOAL_RACE",
    "FINANCIAL_INDEPENDENCE",
    "POLITICAL",
    name="game_type",
    create_type=False,
)
PLAYER_GROUPING = postgresql.ENUM(
    "INDIVIDUAL", "TEAMS", name="player_grouping", create_type=False
)
TEAM_NAMING = postgresql.ENUM("COLOR", "NUMBER", name="team_naming", create_type=False)
COMPUTER_DIFFICULTY = postgresql.ENUM(
    "EASY", "NORMAL", "HARD", name="computer_difficulty", create_type=False
)
ENUMS = (
    VICTORY_CRITERION,
    GAME_TYPE,
    PLAYER_GROUPING,
    TEAM_NAMING,
    COMPUTER_DIFFICULTY,
)

# Cada coluna de regra com o SQL do valor dela no JSON, no formato do
# `SimulationSettingsDTO.model_dump(mode="json")`: Decimal como texto, data ISO
# e enum como texto
RULES = {
    "start_date": "to_char(start_date, 'YYYY-MM-DD')",
    "end_date": "to_char(end_date, 'YYYY-MM-DD')",
    "starting_cash": "starting_cash::text",
    "monthly_contribution": "monthly_contribution::text",
    "price_impact_enabled": "price_impact_enabled",
    "price_impact_k": "price_impact_k",
    "price_impact_decay_days": "price_impact_decay_days",
    "victory_criterion": "victory_criterion::text",
    "game_type": "game_type::text",
    "goal_net_worth": "goal_net_worth::text",
    "monthly_salary": "monthly_salary::text",
    "monthly_expense": "monthly_expense::text",
    "unexpected_per_year": "unexpected_per_year",
    "withdrawal_rate": "withdrawal_rate::text",
    "inflation_adjusted": "inflation_adjusted",
    "player_grouping": "player_grouping::text",
    "team_naming": "team_naming::text",
    "show_equivalent_rate": "show_equivalent_rate",
    "show_maturity_projection": "show_maturity_projection",
    "show_chart_hints": "show_chart_hints",
    "government_enabled": "government_enabled",
    "first_election": "to_char(first_election, 'YYYY-MM-DD')",
    "computer_difficulty": "computer_difficulty::text",
}


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column("rules", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    pairs = ", ".join(f"'{key}', {value}" for key, value in RULES.items())
    op.execute(f"UPDATE simulations SET rules = jsonb_build_object({pairs})")
    op.alter_column("simulations", "rules", nullable=False)
    for column in RULES:
        op.drop_column("simulations", column)
    for enum in ENUMS:
        enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    for enum in ENUMS:
        enum.create(op.get_bind(), checkfirst=True)
    columns = [
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("starting_cash", sa.Numeric(20, 6)),
        sa.Column("monthly_contribution", sa.Numeric(20, 6)),
        sa.Column("price_impact_enabled", sa.Boolean()),
        sa.Column("price_impact_k", sa.Double(precision=53)),
        sa.Column("price_impact_decay_days", sa.Integer()),
        sa.Column("victory_criterion", VICTORY_CRITERION),
        sa.Column("game_type", GAME_TYPE),
        sa.Column("goal_net_worth", sa.Numeric(20, 6)),
        sa.Column("monthly_salary", sa.Numeric(20, 6)),
        sa.Column("monthly_expense", sa.Numeric(20, 6)),
        sa.Column("unexpected_per_year", sa.SmallInteger()),
        sa.Column("withdrawal_rate", sa.Numeric(10, 6)),
        sa.Column("inflation_adjusted", sa.Boolean()),
        sa.Column("player_grouping", PLAYER_GROUPING),
        sa.Column("team_naming", TEAM_NAMING),
        sa.Column("show_equivalent_rate", sa.Boolean()),
        sa.Column("show_maturity_projection", sa.Boolean()),
        sa.Column("show_chart_hints", sa.Boolean()),
        sa.Column("government_enabled", sa.Boolean()),
        sa.Column("first_election", sa.Date()),
        sa.Column("computer_difficulty", COMPUTER_DIFFICULTY),
    ]
    for column in columns:
        op.add_column("simulations", column)
    assignments = ", ".join(
        f"{column.name} = (rules->>'{column.name}')::{_sql_type(column)}"
        for column in columns
    )
    op.execute(f"UPDATE simulations SET {assignments}")
    defaults = {
        "victory_criterion": "'SCORE'",
        "game_type": "'CLASSIC'",
        "player_grouping": "'INDIVIDUAL'",
        "team_naming": "'COLOR'",
        "show_equivalent_rate": "true",
        "show_maturity_projection": "true",
        "show_chart_hints": "true",
        "government_enabled": "false",
        "computer_difficulty": "'NORMAL'",
    }
    for column in columns:
        if column.name != "first_election":
            op.alter_column("simulations", column.name, nullable=False)
        if column.name in defaults:
            op.alter_column(
                "simulations",
                column.name,
                server_default=sa.text(defaults[column.name]),
            )
    op.drop_column("simulations", "rules")


def _sql_type(column: sa.Column) -> str:
    """O tipo do Postgres para onde o texto do JSON é convertido."""
    return column.type.compile(dialect=postgresql.dialect())
