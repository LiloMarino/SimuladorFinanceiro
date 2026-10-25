"""create initial schema

Revision ID: f3a6c2d85b17
Revises:
Create Date: 2026-10-25 19:27:34.727354
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f3a6c2d85b17"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Os prontos do app: o que cada um não traz vem do padrão ao carregar
BUILT_IN_PRESETS: list[tuple[str, dict[str, object]]] = [
    (
        "Iniciante",
        {
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "starting_cash": "10000",
            "monthly_contribution": "500",
            "game_type": "CLASSIC",
            "victory_criterion": "NETWORTH",
        },
    ),
    (
        "Clássico",
        {
            "start_date": "2010-01-01",
            "end_date": "2024-12-31",
            "starting_cash": "100000",
            "monthly_contribution": "1000",
            "game_type": "CLASSIC",
            "victory_criterion": "SCORE",
        },
    ),
    (
        "Realista",
        {
            "start_date": "2000-01-01",
            "end_date": "2024-12-31",
            "game_type": "FINANCIAL_INDEPENDENCE",
            "price_impact_enabled": True,
            "price_impact_k": 0.02,
            "price_impact_decay_days": 20,
            "show_equivalent_rate": False,
            "show_maturity_projection": False,
        },
    ),
]


def upgrade() -> None:
    op.create_table(
        "economic_indicator_history",
        sa.Column(
            "series",
            sa.Enum("CDI", "SELIC", "IPCA", "IBOV", name="indicator_series"),
            nullable=False,
        ),
        sa.Column("ref_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column(
            "origin", sa.Enum("REAL", "GENERATED", name="data_origin"), nullable=False
        ),
        sa.Column(
            "version", sa.BigInteger(), server_default=sa.text("0"), nullable=False
        ),
        sa.PrimaryKeyConstraint(
            "series", "ref_date", "version", name="economic_indicator_history_pkey"
        ),
    )
    op.create_table(
        "fetch_log",
        sa.Column(
            "series",
            sa.Enum("CDI", "SELIC", "IPCA", "IBOV", name="indicator_series"),
            nullable=False,
        ),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("succeeded_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("series", name="fetch_log_pkey"),
    )
    op.create_table(
        "fixed_income_asset",
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
        sa.Column("asset_uuid", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("issuer", sa.Text(), nullable=False),
        sa.Column(
            "investment_type",
            sa.Enum("CDB", "LCI", "LCA", "TESOURO_DIRETO", name="investment_type"),
            nullable=False,
        ),
        sa.Column(
            "rate_type",
            sa.Enum("SELIC", "IPCA", "CDI", "PREFIXADO", name="rate_type"),
            nullable=False,
        ),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column("interest_rate", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column(
            "daily_liquidity",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("player_cap", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column("offered_until", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="fixed_income_asset_pkey"),
        sa.UniqueConstraint("asset_uuid", name="fixed_income_asset_uuid_key"),
    )
    op.create_table(
        "generated_future",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("seed", sa.BigInteger(), nullable=False),
        sa.Column("temperature", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column(
            "start_regime",
            sa.Enum("CALM", "NORMAL", "AGITATED", name="market_regime"),
            nullable=True,
        ),
        sa.Column("inflation_shock", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("until", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("real_advanced_until", sa.Date(), nullable=True),
        sa.CheckConstraint("id = 1", name="generated_future_single_row"),
        sa.PrimaryKeyConstraint("id", name="generated_future_pkey"),
    )
    op.create_table(
        "import_settings",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column(
            "correct_price_errors",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name="import_settings_single_row"),
        sa.PrimaryKeyConstraint("id", name="import_settings_pkey"),
    )
    op.create_table(
        "last_simulation_settings",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("id = 1", name="last_simulation_settings_single_row"),
        sa.PrimaryKeyConstraint("id", name="last_simulation_settings_pkey"),
    )
    preset = op.create_table(
        "preset",
        sa.Column("id", sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "built_in", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="preset_pkey"),
    )
    op.create_index(
        "preset_name_lower_key",
        "preset",
        [sa.literal_column("lower(name)")],
        unique=True,
    )
    op.bulk_insert(
        preset,
        [
            {"name": name, "built_in": True, "config": config}
            for name, config in BUILT_IN_PRESETS
        ],
    )
    op.create_table(
        "sectors",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="sectors_pkey"),
        sa.UniqueConstraint("name", name="sectors_name_key"),
    )
    op.create_table(
        "simulations",
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
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("starting_cash", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column(
            "monthly_contribution", sa.Numeric(precision=20, scale=6), nullable=False
        ),
        sa.Column("price_impact_enabled", sa.Boolean(), nullable=False),
        sa.Column("price_impact_k", sa.Double(precision=53), nullable=False),
        sa.Column("price_impact_decay_days", sa.Integer(), nullable=False),
        sa.Column(
            "victory_criterion",
            sa.Enum("SCORE", "RETURN", "NETWORTH", "SHARPE", name="victory_criterion"),
            server_default=sa.text("'SCORE'"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_simulated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "player_grouping",
            sa.Enum("INDIVIDUAL", "TEAMS", name="player_grouping"),
            server_default=sa.text("'INDIVIDUAL'"),
            nullable=False,
        ),
        sa.Column(
            "team_naming",
            sa.Enum("COLOR", "NUMBER", name="team_naming"),
            server_default=sa.text("'COLOR'"),
            nullable=False,
        ),
        sa.Column(
            "game_type",
            sa.Enum("CLASSIC", "GOAL_RACE", "FINANCIAL_INDEPENDENCE", name="game_type"),
            server_default=sa.text("'CLASSIC'"),
            nullable=False,
        ),
        sa.Column("goal_net_worth", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("monthly_salary", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("monthly_expense", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("unexpected_per_year", sa.SmallInteger(), nullable=False),
        sa.Column("withdrawal_rate", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column("inflation_adjusted", sa.Boolean(), nullable=False),
        sa.Column("random_seed", sa.BigInteger(), nullable=False),
        sa.Column(
            "show_equivalent_rate",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "show_maturity_projection",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "is_backtest", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result_as_of", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="simulations_pkey"),
        sa.UniqueConstraint("name", name="simulations_name_key"),
    )
    op.create_table(
        "ticker_profile",
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("quote_type", sa.Text(), nullable=True),
        sa.Column("sector", sa.Text(), nullable=True),
        sa.Column("industry", sa.Text(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("ticker", name="ticker_profile_pkey"),
    )
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("nickname", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "is_bot", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("client_id", name="users_client_id_key"),
    )
    op.create_index(
        "users_nickname_key",
        "users",
        ["nickname"],
        unique=True,
        postgresql_where=sa.text("NOT is_bot"),
    )
    op.create_table(
        "achievement_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("best", sa.Numeric(precision=30, scale=6), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="achievement_progress_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "code", name="achievement_progress_pkey"),
    )
    op.create_table(
        "achievements",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("game_date", sa.Date(), nullable=False),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="achievements_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="achievements_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "code", name="achievements_pkey"),
    )
    op.create_table(
        "event_cashflow",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "DEPOSIT",
                "WITHDRAW",
                "DIVIDEND",
                "CONTRIBUTION",
                "TAX",
                "SALARY",
                "EXPENSE",
                "UNEXPECTED_EXPENSE",
                "OVERDRAFT_INTEREST",
                "LOAN_PROCEEDS",
                "LOAN_PAYMENT",
                name="cashflow_event_type",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("life_event_key", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="event_cashflow_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="event_cashflow_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="event_cashflow_pkey"),
    )
    op.create_table(
        "event_credit",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("loan_id", sa.Uuid(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "CONTRACT",
                "INSTALLMENT_PAID",
                "INSTALLMENT_LATE",
                "OVERDUE_PAID",
                "PREPAYMENT",
                "PAYOFF",
                name="credit_event_type",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("installment_number", sa.Integer(), nullable=True),
        sa.Column("annual_rate", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("term_months", sa.Integer(), nullable=True),
        sa.Column(
            "grade",
            sa.Enum(
                "AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D", name="credit_grade"
            ),
            nullable=True,
        ),
        sa.Column(
            "prepayment_mode",
            sa.Enum(
                "SHORTEN_TERM", "REDUCE_INSTALLMENT", name="credit_prepayment_mode"
            ),
            nullable=True,
        ),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="event_credit_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="event_credit_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="event_credit_pkey"),
    )
    op.create_table(
        "event_fixed_income",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum("BUY", "REDEEM", name="fixed_income_event_type"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["fixed_income_asset.id"],
            name="event_fixed_income_asset_id_fkey",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="event_fixed_income_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="event_fixed_income_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="event_fixed_income_pkey"),
    )
    op.create_table(
        "segments",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sector_id"],
            ["sectors.id"],
            name="segments_sector_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="segments_pkey"),
        sa.UniqueConstraint("sector_id", "name", name="segments_sector_id_name_key"),
    )
    op.create_table(
        "simulation_players",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("color", sa.Text(), nullable=False),
        sa.Column("team", sa.SmallInteger(), nullable=True),
        sa.CheckConstraint(
            "team BETWEEN 1 AND 10", name="simulation_players_team_check"
        ),
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
    op.create_table(
        "snapshots",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("total_equity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("total_fixed", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("total_cash", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column(
            "total_contribution", sa.Numeric(precision=20, scale=6), nullable=False
        ),
        sa.Column("total_networth", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "total_debt",
            sa.Numeric(precision=20, scale=6),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="snapshots_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="snapshots_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id", "user_id", "snapshot_date", name="snapshots_pkey"
        ),
    )
    op.create_table(
        "strategy_log",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("strategy_key", sa.Text(), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("action", sa.Text(), nullable=True),
        sa.Column("ticker", sa.Text(), nullable=True),
        sa.Column("asset_uuid", sa.Uuid(), nullable=True),
        sa.Column("asset_name", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column("price", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("order_type", sa.Text(), nullable=True),
        sa.Column("order_id", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="strategy_log_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="strategy_log_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="strategy_log_pkey"),
    )
    op.create_index(
        "strategy_log_user_idx",
        "strategy_log",
        ["simulation_id", "user_id", "event_date"],
        unique=False,
    )
    op.create_table(
        "stock",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "asset_class",
            sa.Enum("STOCK", "FII", "ETF", "BDR", "CRYPTO", name="asset_class"),
            nullable=False,
        ),
        sa.Column("segment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["segment_id"],
            ["segments.id"],
            name="stock_segment_id_fkey",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="stock_pkey"),
        sa.UniqueConstraint("ticker", name="stock_ticker_key"),
    )
    op.create_table(
        "event_equity",
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
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum("BUY", "SELL", name="equity_event_type"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="event_equity_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="event_equity_stock_id_fkey",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="event_equity_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="event_equity_pkey"),
    )
    op.create_table(
        "stock_price_history",
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Double(precision=53), nullable=False),
        sa.Column("high", sa.Double(precision=53), nullable=False),
        sa.Column("low", sa.Double(precision=53), nullable=False),
        sa.Column("close", sa.Double(precision=53), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column(
            "origin",
            sa.Enum("REAL", "GENERATED", name="data_origin"),
            server_default=sa.text("'REAL'"),
            nullable=False,
        ),
        sa.Column(
            "version", sa.BigInteger(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "price_corrected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="stock_price_history_stock_id_fkey",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "stock_id", "price_date", "version", name="stock_price_history_pkey"
        ),
    )


def downgrade() -> None:
    op.drop_table("stock_price_history")
    op.drop_table("event_equity")
    op.drop_table("stock")
    op.drop_index("strategy_log_user_idx", table_name="strategy_log")
    op.drop_table("strategy_log")
    op.drop_table("snapshots")
    op.drop_table("simulation_players")
    op.drop_table("segments")
    op.drop_table("event_fixed_income")
    op.drop_table("event_credit")
    op.drop_table("event_cashflow")
    op.drop_table("achievements")
    op.drop_table("achievement_progress")
    op.drop_index(
        "users_nickname_key", table_name="users", postgresql_where=sa.text("NOT is_bot")
    )
    op.drop_table("users")
    op.drop_table("ticker_profile")
    op.drop_table("simulations")
    op.drop_table("sectors")
    op.drop_index("preset_name_lower_key", table_name="preset")
    op.drop_table("preset")
    op.drop_table("last_simulation_settings")
    op.drop_table("import_settings")
    op.drop_table("generated_future")
    op.drop_table("fixed_income_asset")
    op.drop_table("fetch_log")
    op.drop_table("economic_indicator_history")
    # Os ENUM nativos do Postgres sobrevivem ao drop das tabelas que os usam
    for enum_name in (
        "asset_class",
        "cashflow_event_type",
        "credit_event_type",
        "credit_grade",
        "credit_prepayment_mode",
        "data_origin",
        "equity_event_type",
        "fixed_income_event_type",
        "game_type",
        "indicator_series",
        "investment_type",
        "market_regime",
        "player_grouping",
        "rate_type",
        "team_naming",
        "victory_criterion",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind())
