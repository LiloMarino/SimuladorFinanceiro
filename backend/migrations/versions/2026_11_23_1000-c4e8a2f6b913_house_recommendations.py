"""house recommendations

Revision ID: c4e8a2f6b913
Revises: b3d7f1a8c264
Create Date: 2026-11-23 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4e8a2f6b913"
down_revision: str | Sequence[str] | None = "b3d7f1a8c264"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "house_recommendations",
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
        sa.Column("report_month", sa.Date(), nullable=False),
        sa.Column("issued_on", sa.Date(), nullable=False),
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("side", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("target", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("result_price", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("resolved_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="house_recommendations_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="house_recommendations_pkey"),
    )
    op.create_index(
        "house_recommendations_simulation_month_idx",
        "house_recommendations",
        ["simulation_id", "report_month"],
    )


def downgrade() -> None:
    op.drop_index(
        "house_recommendations_simulation_month_idx",
        table_name="house_recommendations",
    )
    op.drop_table("house_recommendations")
