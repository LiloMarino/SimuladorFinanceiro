"""fund assembly agenda

Revision ID: a9d4e17c3b62
Revises: f7c3b58e2d41
Create Date: 2026-11-19 15:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a9d4e17c3b62"
down_revision: str | Sequence[str] | None = "f7c3b58e2d41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # As assembleias que já existem são todas de troca de gestor
    op.add_column(
        "fund_assemblies",
        sa.Column(
            "agenda",
            sa.Text(),
            server_default=sa.text("'REPLACE_MANAGER'"),
            nullable=False,
        ),
    )
    op.add_column(
        "fund_assemblies",
        sa.Column("previous_management_fee", sa.Numeric(8, 6), nullable=True),
    )
    op.add_column(
        "fund_assemblies",
        sa.Column("previous_performance_fee", sa.Numeric(8, 6), nullable=True),
    )
    op.add_column(
        "fund_assemblies",
        sa.Column("proposed_management_fee", sa.Numeric(8, 6), nullable=True),
    )
    op.add_column(
        "fund_assemblies",
        sa.Column("proposed_performance_fee", sa.Numeric(8, 6), nullable=True),
    )
    op.alter_column(
        "fund_assemblies",
        "candidate_user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("DELETE FROM fund_assemblies WHERE candidate_user_id IS NULL")
    op.alter_column(
        "fund_assemblies",
        "candidate_user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("fund_assemblies", "proposed_performance_fee")
    op.drop_column("fund_assemblies", "proposed_management_fee")
    op.drop_column("fund_assemblies", "previous_performance_fee")
    op.drop_column("fund_assemblies", "previous_management_fee")
    op.drop_column("fund_assemblies", "agenda")
