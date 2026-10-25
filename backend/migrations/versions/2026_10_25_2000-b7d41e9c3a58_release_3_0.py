"""release 3.0: government, measures, candle challenge, achievements and rules in json

Revision ID: b7d41e9c3a58
Revises: f3a6c2d85b17
Create Date: 2026-10-25 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7d41e9c3a58"
down_revision: str | Sequence[str] | None = "f3a6c2d85b17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

GOVERNMENT_EVENT_TYPE = postgresql.ENUM(
    "PARTY_FOUNDED",
    "COMPUTER_PARTY_ADDED",
    "COMPUTER_PARTY_REMOVED",
    "PARTY_JOINED",
    "PARTY_LEFT",
    "MEMBER_EXPELLED",
    "CONTRIBUTION_SET",
    "TICKET_SET",
    "VICE_ANSWERED",
    "CAMPAIGN_SPENT",
    "DONATION_MADE",
    "ELECTION_ROUND",
    "TERM_STARTED",
    name="government_event_type",
    create_type=False,
)
COMPUTER_DIFFICULTY = postgresql.ENUM(
    "EASY", "NORMAL", "HARD", name="computer_difficulty", create_type=False
)

NEW_EVENT_TYPES = (
    "MEASURE_PROPOSED",
    "MEASURE_WITHDRAWN",
    "MEASURE_VOTED",
    "APPROVAL_MEASURED",
    "IMPEACHED",
)

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


# A 3.0 junta as migrations desde a 2.3.0, na ordem em que nasceram; cada etapa
# vira um par de funções, e o `downgrade` desfaz na ordem inversa.
def upgrade() -> None:
    _government_expansion_up()
    _government_measures_up()
    _candle_challenge_up()
    _keep_achievements_up()
    _rules_to_json_up()


def downgrade() -> None:
    _rules_to_json_down()
    _keep_achievements_down()
    _candle_challenge_down()
    _government_measures_down()
    _government_expansion_down()


def _government_expansion_up() -> None:
    # ADD VALUE não roda dentro de transação em alguns bancos; o bloco autocommit vale para todos
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE game_type ADD VALUE IF NOT EXISTS 'POLITICAL'")
        op.execute(
            "ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN_CONTRIBUTION'"
        )
        op.execute(
            "ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN_DONATION'"
        )
    COMPUTER_DIFFICULTY.create(op.get_bind(), checkfirst=True)
    GOVERNMENT_EVENT_TYPE.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "simulations",
        sa.Column(
            "government_enabled",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column("simulations", sa.Column("first_election", sa.Date(), nullable=True))
    op.add_column(
        "simulations",
        sa.Column(
            "computer_difficulty",
            COMPUTER_DIFFICULTY,
            server_default=sa.text("'NORMAL'"),
            nullable=False,
        ),
    )
    op.create_table(
        "government_event",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=9223372036854775807,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("event_type", GOVERNMENT_EVENT_TYPE, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="government_event_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="government_event_pkey"),
    )
    op.create_index(
        "government_event_simulation_id_idx",
        "government_event",
        ["simulation_id", "id"],
        unique=False,
    )


def _government_expansion_down() -> None:
    op.drop_index("government_event_simulation_id_idx", table_name="government_event")
    op.drop_table("government_event")
    op.drop_column("simulations", "computer_difficulty")
    op.drop_column("simulations", "first_election")
    op.drop_column("simulations", "government_enabled")
    GOVERNMENT_EVENT_TYPE.drop(op.get_bind(), checkfirst=True)
    COMPUTER_DIFFICULTY.drop(op.get_bind(), checkfirst=True)
    # O Postgres não remove valor de ENUM: os valores novos ficam, sem uso
    op.execute(
        "UPDATE simulations SET game_type = 'CLASSIC' WHERE game_type = 'POLITICAL'"
    )


def _government_measures_up() -> None:
    # ADD VALUE não roda dentro de transação em alguns bancos; o bloco autocommit vale para todos
    with op.get_context().autocommit_block():
        for value in NEW_EVENT_TYPES:
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def _government_measures_down() -> None:
    # Valor de enum do Postgres não sai sem recriar o tipo; os eventos novos ficam sem uso
    pass


def _candle_challenge_up() -> None:
    op.create_table(
        "candle_challenges",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("pattern_date", sa.Date(), nullable=False),
        sa.Column("pattern_code", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("answered_on", sa.Date(), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("settled_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="candle_challenges_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="candle_challenges_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id",
            "user_id",
            "ticker",
            "pattern_date",
            name="candle_challenges_pkey",
        ),
    )
    op.create_index(
        "candle_challenges_open_idx",
        "candle_challenges",
        ["simulation_id", "result"],
        unique=False,
    )
    op.add_column(
        "simulations",
        sa.Column(
            "show_chart_hints",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    # O Realista já desliga as outras ajudas: a das dicas de análise técnica vai junto
    op.execute(
        "UPDATE preset SET config = config || jsonb_build_object('show_chart_hints', false) "
        "WHERE built_in AND name = 'Realista'"
    )


def _candle_challenge_down() -> None:
    op.execute(
        "UPDATE preset SET config = config - 'show_chart_hints' "
        "WHERE built_in AND name = 'Realista'"
    )
    op.drop_column("simulations", "show_chart_hints")
    op.drop_index("candle_challenges_open_idx", table_name="candle_challenges")
    op.drop_table("candle_challenges")


def _keep_achievements_up() -> None:
    op.alter_column(
        "achievements", "simulation_id", existing_type=sa.BIGINT(), nullable=True
    )
    op.drop_constraint(
        op.f("achievements_simulation_id_fkey"), "achievements", type_="foreignkey"
    )
    op.create_foreign_key(
        "achievements_simulation_id_fkey",
        "achievements",
        "simulations",
        ["simulation_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )


def _keep_achievements_down() -> None:
    # O schema anterior exige a partida: a conquista sem ela sai junto
    op.execute("DELETE FROM achievements WHERE simulation_id IS NULL")
    op.drop_constraint(
        "achievements_simulation_id_fkey", "achievements", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("achievements_simulation_id_fkey"),
        "achievements",
        "simulations",
        ["simulation_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.alter_column(
        "achievements", "simulation_id", existing_type=sa.BIGINT(), nullable=False
    )


def _rules_to_json_up() -> None:
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


def _rules_to_json_down() -> None:
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
