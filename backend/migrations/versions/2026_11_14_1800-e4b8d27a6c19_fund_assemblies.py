"""fund assemblies

Revision ID: e4b8d27a6c19
Revises: c7e2a91d5b34
Create Date: 2026-11-14 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e4b8d27a6c19"
down_revision: str | Sequence[str] | None = "c7e2a91d5b34"
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


def _user_fk(column: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(
        [column],
        ["users.id"],
        name=f"fund_assemblies_{column}_fkey",
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def upgrade() -> None:
    op.create_table(
        "fund_assemblies",
        sa.Column("id", sa.BigInteger(), _identity(), nullable=False),
        sa.Column("fund_id", sa.BigInteger(), nullable=False),
        sa.Column("convener_user_id", sa.Integer(), nullable=False),
        sa.Column("candidate_user_id", sa.Integer(), nullable=False),
        sa.Column("previous_manager_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("called_on", sa.Date(), nullable=False),
        sa.Column("started_on", sa.Date(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("closed_on", sa.Date(), nullable=True),
        sa.Column("in_favor_quotas", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("against_quotas", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column(
            "abstention_quotas", sa.Numeric(precision=20, scale=6), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            name="fund_assemblies_fund_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        _user_fk("convener_user_id"),
        _user_fk("candidate_user_id"),
        _user_fk("previous_manager_user_id"),
        sa.PrimaryKeyConstraint("id", name="fund_assemblies_pkey"),
    )
    op.create_table(
        "fund_assembly_votes",
        sa.Column("assembly_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("in_favor", sa.Boolean(), nullable=False),
        sa.Column("voted_on", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assembly_id"],
            ["fund_assemblies.id"],
            name="fund_assembly_votes_assembly_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fund_assembly_votes_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "assembly_id", "user_id", name="fund_assembly_votes_pkey"
        ),
    )


def downgrade() -> None:
    op.drop_table("fund_assembly_votes")
    op.drop_table("fund_assemblies")
