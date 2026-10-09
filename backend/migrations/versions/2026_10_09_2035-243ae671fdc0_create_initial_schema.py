"""create initial schema

Revision ID: 243ae671fdc0
Revises:
Create Date: 2026-10-09 20:35:46.154794
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "243ae671fdc0"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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
        "ipca_history",
        sa.Column("ref_month", sa.Date(), nullable=False),
        sa.Column("rate_value", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.PrimaryKeyConstraint("ref_month", name="ipca_history_pkey"),
    )
    op.create_table(
        "selic_history",
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("rate_value", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.PrimaryKeyConstraint("rate_date", name="selic_history_pkey"),
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
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_simulated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="simulations_pkey"),
        sa.UniqueConstraint("name", name="simulations_name_key"),
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
        sa.PrimaryKeyConstraint("id", name="stock_pkey"),
        sa.UniqueConstraint("name", name="stock_name_key"),
        sa.UniqueConstraint("ticker", name="stock_ticker_key"),
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
        "stock_price_history",
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Double(precision=53), nullable=False),
        sa.Column("high", sa.Double(precision=53), nullable=False),
        sa.Column("low", sa.Double(precision=53), nullable=False),
        sa.Column("close", sa.Double(precision=53), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
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
    op.drop_table("snapshots")
    op.drop_table("event_fixed_income")
    op.drop_table("event_equity")
    op.drop_table("event_cashflow")
    op.drop_table("users")
    op.drop_table("stock")
    op.drop_table("simulations")
    op.drop_table("selic_history")
    op.drop_table("ipca_history")
    op.drop_table("fixed_income_asset")
    # Os ENUM nativos do Postgres sobrevivem ao drop das tabelas que os usam
    for enum_name in (
        "investment_type",
        "rate_type",
        "cashflow_event_type",
        "equity_event_type",
        "fixed_income_event_type",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind())
