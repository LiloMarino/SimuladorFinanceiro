"""fund issuance buyback

Revision ID: c7e2a91d5b34
Revises: a6151a1b749d
Create Date: 2026-11-14 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c7e2a91d5b34"
down_revision: str | Sequence[str] | None = "a6151a1b749d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _identity() -> sa.Identity:
    return sa.Identity(
        always=True,
        start=1,
        increment=1,
        minvalue=1,
        maxvalue=9223372036854775807,
        cycle=False,
        cache=1,
    )


def upgrade() -> None:
    op.create_table(
        "fund_issuances",
        sa.Column("id", sa.BigInteger(), _identity(), nullable=False),
        sa.Column("fund_id", sa.BigInteger(), nullable=False),
        sa.Column("announced_on", sa.Date(), nullable=False),
        sa.Column("quotas", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("preference_ends_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("sold", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("closed_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            name="fund_issuances_fund_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="fund_issuances_pkey"),
    )
    op.create_table(
        "fund_issuance_rights",
        sa.Column("issuance_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rights", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("bought", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.ForeignKeyConstraint(
            ["issuance_id"],
            ["fund_issuances.id"],
            name="fund_issuance_rights_issuance_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fund_issuance_rights_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "issuance_id", "user_id", name="fund_issuance_rights_pkey"
        ),
    )
    op.create_table(
        "fund_buybacks",
        sa.Column("id", sa.BigInteger(), _identity(), nullable=False),
        sa.Column("fund_id", sa.BigInteger(), nullable=False),
        sa.Column("announced_on", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("max_price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("bought", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("paid", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            name="fund_buybacks_fund_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="fund_buybacks_pkey"),
    )
    op.add_column(
        "fund_offer_sales", sa.Column("issuance_id", sa.BigInteger(), nullable=True)
    )
    op.create_foreign_key(
        "fund_offer_sales_issuance_id_fkey",
        "fund_offer_sales",
        "fund_issuances",
        ["issuance_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fund_offer_sales_issuance_id_fkey", "fund_offer_sales", type_="foreignkey"
    )
    op.drop_column("fund_offer_sales", "issuance_id")
    op.drop_table("fund_buybacks")
    op.drop_table("fund_issuance_rights")
    op.drop_table("fund_issuances")
