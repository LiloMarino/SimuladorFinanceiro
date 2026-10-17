"""create initial schema

Revision ID: c0b110c6a2e8
Revises:
Create Date: 2026-10-17 14:03:42.083780
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c0b110c6a2e8"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


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
        sa.PrimaryKeyConstraint(
            "series", "ref_date", name="economic_indicator_history_pkey"
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
        sa.PrimaryKeyConstraint("id", name="fixed_income_asset_pkey"),
        sa.UniqueConstraint("asset_uuid", name="fixed_income_asset_uuid_key"),
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
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("client_id", name="users_client_id_key"),
        sa.UniqueConstraint("nickname", name="users_nickname_key"),
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
                name="cashflow_event_type",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
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
            sa.Enum("STOCK", "FII", "ETF", "BDR", name="asset_class"),
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
        sa.UniqueConstraint("name", name="stock_name_key"),
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
        sa.Column("quantity", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="stock_price_history_stock_id_fkey",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "stock_id", "price_date", name="stock_price_history_pkey"
        ),
    )


def downgrade() -> None:
    op.drop_table("stock_price_history")
    op.drop_table("event_equity")
    op.drop_table("stock")
    op.drop_table("snapshots")
    op.drop_table("simulation_players")
    op.drop_table("segments")
    op.drop_table("event_fixed_income")
    op.drop_table("event_cashflow")
    op.drop_table("users")
    op.drop_table("ticker_profile")
    op.drop_table("simulations")
    op.drop_table("sectors")
    op.drop_table("fixed_income_asset")
    op.drop_table("fetch_log")
    op.drop_table("economic_indicator_history")
    # Os ENUM nativos do Postgres sobrevivem ao drop das tabelas que os usam
    for enum_name in (
        "indicator_series",
        "data_origin",
        "investment_type",
        "rate_type",
        "victory_criterion",
        "cashflow_event_type",
        "fixed_income_event_type",
        "equity_event_type",
        "asset_class",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind())
