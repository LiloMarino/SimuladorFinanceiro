"""fund distributions

Revision ID: b3f19c6e2a85
Revises: e4b8d27a6c19
Create Date: 2026-11-15 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3f19c6e2a85"
down_revision: str | Sequence[str] | None = "e4b8d27a6c19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _money_column(name: str) -> sa.Column:
    return sa.Column(
        name,
        sa.Numeric(precision=20, scale=6),
        server_default=sa.text("0"),
        nullable=False,
    )


def upgrade() -> None:
    op.add_column(
        "funds",
        sa.Column(
            "distribution_rate",
            sa.Numeric(precision=8, scale=6),
            server_default=sa.text("0.95"),
            nullable=False,
        ),
    )
    op.add_column(
        "funds",
        sa.Column(
            "pending_distribution_rate",
            sa.Numeric(precision=8, scale=6),
            nullable=True,
        ),
    )
    op.add_column("funds", _money_column("month_dividends"))
    op.add_column("funds", _money_column("month_interest"))
    op.add_column("funds", _money_column("month_sales_gain"))
    op.add_column("funds", _money_column("month_fees"))
    op.create_table(
        "fund_distributions",
        sa.Column("fund_id", sa.BigInteger(), nullable=False),
        sa.Column("data_com", sa.Date(), nullable=False),
        sa.Column("realized_profit", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("rate", sa.Numeric(precision=8, scale=6), nullable=False),
        sa.Column("quotas", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("per_quota", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("paid_per_quota", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("paid", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("paid_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            name="fund_distributions_fund_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("fund_id", "data_com", name="fund_distributions_pkey"),
    )


def downgrade() -> None:
    op.drop_table("fund_distributions")
    op.drop_column("funds", "month_fees")
    op.drop_column("funds", "month_sales_gain")
    op.drop_column("funds", "month_interest")
    op.drop_column("funds", "month_dividends")
    op.drop_column("funds", "pending_distribution_rate")
    op.drop_column("funds", "distribution_rate")
