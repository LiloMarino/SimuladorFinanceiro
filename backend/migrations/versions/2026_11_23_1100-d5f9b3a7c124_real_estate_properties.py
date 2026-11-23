"""real estate properties

Revision ID: d5f9b3a7c124
Revises: c4e8a2f6b913
Create Date: 2026-11-23 11:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d5f9b3a7c124"
down_revision: str | Sequence[str] | None = "c4e8a2f6b913"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "real_estate_properties",
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
        sa.Column("size", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("base_price", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("offer_month", sa.Date(), nullable=True),
        sa.Column("contract_rent", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("contract_start", sa.Date(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("vacant_since", sa.Date(), nullable=True),
        sa.Column("sale_due", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id", "user_id"],
            ["simulation_players.simulation_id", "simulation_players.user_id"],
            name="real_estate_properties_player_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="real_estate_properties_pkey"),
    )
    op.create_index(
        "real_estate_properties_player_idx",
        "real_estate_properties",
        ["simulation_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "real_estate_properties_player_idx", table_name="real_estate_properties"
    )
    op.drop_table("real_estate_properties")
