"""add state companies

Revision ID: c4e7b92d5a18
Revises: c41d7a9e5b30
Create Date: 2026-11-15 15:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4e7b92d5a18"
down_revision: str | Sequence[str] | None = "c41d7a9e5b30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ticker_profile",
        sa.Column("shares_outstanding", sa.BigInteger(), nullable=True),
    )
    op.create_table(
        "state_owned_stocks",
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("government_share", sa.Numeric(precision=6, scale=5), nullable=False),
        sa.Column("shares", sa.BigInteger(), nullable=False),
        sa.Column("lever", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "government_share > 0 AND government_share <= 1",
            name="state_owned_stocks_share_check",
        ),
        sa.CheckConstraint("shares > 0", name="state_owned_stocks_shares_check"),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="state_owned_stocks_stock_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("stock_id", name="state_owned_stocks_pkey"),
    )
    op.create_table(
        "state_companies",
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
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("government_share", sa.Numeric(precision=6, scale=5), nullable=False),
        sa.Column("shares", sa.BigInteger(), nullable=False),
        sa.Column("lever", sa.Text(), nullable=True),
        sa.Column("size", sa.Text(), nullable=True),
        sa.Column(
            "invested",
            sa.Numeric(precision=20, scale=6),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("mean_return", sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column("seed", sa.BigInteger(), nullable=True),
        sa.Column(
            "status", sa.Text(), server_default=sa.text("'ACTIVE'"), nullable=False
        ),
        sa.Column("founded_on", sa.Date(), nullable=True),
        sa.Column("offer_opened_on", sa.Date(), nullable=True),
        sa.Column("privatized_on", sa.Date(), nullable=True),
        sa.Column("proceeds", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="state_companies_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="state_companies_stock_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="state_companies_pkey"),
        sa.UniqueConstraint(
            "simulation_id", "stock_id", name="state_companies_simulation_stock_key"
        ),
    )
    op.create_table(
        "state_company_months",
        sa.Column("state_company_id", sa.BigInteger(), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("fair_value", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("profit", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column(
            "treasury_dividend", sa.Numeric(precision=20, scale=6), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["state_company_id"],
            ["state_companies.id"],
            name="state_company_months_state_company_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "state_company_id", "month", name="state_company_months_pkey"
        ),
    )
    op.create_table(
        "state_offer_reservations",
        sa.Column("state_company_id", sa.BigInteger(), nullable=False),
        sa.Column("portfolio_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("reserved_on", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "quantity > 0", name="state_offer_reservations_quantity_check"
        ),
        sa.ForeignKeyConstraint(
            ["state_company_id"],
            ["state_companies.id"],
            name="state_offer_reservations_state_company_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
            name="state_offer_reservations_portfolio_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "state_company_id", "portfolio_id", name="state_offer_reservations_pkey"
        ),
    )


def downgrade() -> None:
    op.drop_table("state_offer_reservations")
    op.drop_table("state_company_months")
    op.drop_table("state_companies")
    op.drop_table("state_owned_stocks")
    op.drop_column("ticker_profile", "shares_outstanding")
