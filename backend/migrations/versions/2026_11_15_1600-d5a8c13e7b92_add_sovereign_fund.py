"""add sovereign fund

Revision ID: d5a8c13e7b92
Revises: c4e7b92d5a18
Create Date: 2026-11-15 16:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d5a8c13e7b92"
down_revision: str | Sequence[str] | None = "c4e7b92d5a18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sovereign_funds",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("portfolio_id", sa.BigInteger(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
            name="sovereign_funds_portfolio_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="sovereign_funds_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("simulation_id", name="sovereign_funds_pkey"),
        sa.UniqueConstraint("portfolio_id", name="sovereign_funds_portfolio_id_key"),
    )
    op.create_table(
        "sovereign_fund_flows",
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
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("measure_id", sa.Integer(), nullable=True),
        sa.CheckConstraint("amount > 0", name="sovereign_fund_flows_amount_check"),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="sovereign_fund_flows_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="sovereign_fund_flows_pkey"),
        sa.UniqueConstraint(
            "simulation_id",
            "kind",
            "measure_id",
            name="sovereign_fund_flows_measure_key",
        ),
    )


def downgrade() -> None:
    op.drop_table("sovereign_fund_flows")
    op.drop_table("sovereign_funds")
