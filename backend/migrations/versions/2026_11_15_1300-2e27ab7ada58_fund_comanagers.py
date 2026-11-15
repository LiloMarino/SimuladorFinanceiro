"""fund comanagers

Revision ID: 2e27ab7ada58
Revises: a6d4e81c2f07
Create Date: 2026-11-14 21:59:17.255558
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "2e27ab7ada58"
down_revision: str | Sequence[str] | None = "a6d4e81c2f07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fund_comanager_events",
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
        sa.Column("fund_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("share", sa.Numeric(precision=7, scale=6), nullable=True),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            name="fund_comanager_events_fund_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fund_comanager_events_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="fund_comanager_events_pkey"),
    )
    op.create_table(
        "fund_comanagers",
        sa.Column("fund_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("share", sa.Numeric(precision=7, scale=6), nullable=False),
        sa.Column("pending_share", sa.Numeric(precision=7, scale=6), nullable=True),
        sa.Column("pending_from", sa.Date(), nullable=True),
        sa.Column("invited_on", sa.Date(), nullable=False),
        sa.Column("since", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            name="fund_comanagers_fund_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fund_comanagers_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("fund_id", "user_id", name="fund_comanagers_pkey"),
    )


def downgrade() -> None:
    op.drop_table("fund_comanagers")
    op.drop_table("fund_comanager_events")
