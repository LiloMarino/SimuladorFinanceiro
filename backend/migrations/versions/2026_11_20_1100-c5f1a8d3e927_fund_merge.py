"""fund merge

Revision ID: c5f1a8d3e927
Revises: b8e4d2a7f613
Create Date: 2026-11-20 11:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5f1a8d3e927"
down_revision: str | Sequence[str] | None = "b8e4d2a7f613"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "funds", sa.Column("merged_into_fund_id", sa.BigInteger(), nullable=True)
    )
    op.add_column("funds", sa.Column("merged_on", sa.Date(), nullable=True))
    op.create_foreign_key(
        "funds_merged_into_fund_id_fkey",
        "funds",
        "funds",
        ["merged_into_fund_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    op.add_column(
        "fund_assemblies", sa.Column("partner_fund_id", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "fund_assemblies",
        sa.Column(
            "absorbed", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.add_column(
        "fund_assemblies",
        sa.Column("merge_shortfall", sa.Numeric(precision=20, scale=6), nullable=True),
    )
    op.create_foreign_key(
        "fund_assemblies_partner_fund_id_fkey",
        "fund_assemblies",
        "funds",
        ["partner_fund_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fund_assemblies_partner_fund_id_fkey", "fund_assemblies", type_="foreignkey"
    )
    op.drop_column("fund_assemblies", "merge_shortfall")
    op.drop_column("fund_assemblies", "absorbed")
    op.drop_column("fund_assemblies", "partner_fund_id")
    op.drop_constraint("funds_merged_into_fund_id_fkey", "funds", type_="foreignkey")
    op.drop_column("funds", "merged_on")
    op.drop_column("funds", "merged_into_fund_id")
