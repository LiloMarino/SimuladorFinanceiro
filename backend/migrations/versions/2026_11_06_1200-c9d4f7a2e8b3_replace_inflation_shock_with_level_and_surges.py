"""replace inflation shock with level and surges

Revision ID: c9d4f7a2e8b3
Revises: e4b8d2f6a9c1
Create Date: 2026-11-06 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c9d4f7a2e8b3"
down_revision: str | Sequence[str] | None = "e4b8d2f6a9c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # O valor gravado do choque passa a ser o nível da inflação
    op.alter_column(
        "generated_future", "inflation_shock", new_column_name="inflation_level"
    )
    op.add_column(
        "generated_future",
        sa.Column(
            "surge_frequency",
            sa.Numeric(precision=4, scale=2),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "generated_future",
        sa.Column(
            "surge_intensity",
            sa.Numeric(precision=5, scale=2),
            server_default="6",
            nullable=False,
        ),
    )
    op.drop_column("generated_future", "start_regime")
    sa.Enum(name="market_regime").drop(op.get_bind())


def downgrade() -> None:
    regime = sa.Enum("CALM", "NORMAL", "AGITATED", name="market_regime")
    regime.create(op.get_bind())
    op.add_column("generated_future", sa.Column("start_regime", regime, nullable=True))
    op.drop_column("generated_future", "surge_intensity")
    op.drop_column("generated_future", "surge_frequency")
    op.alter_column(
        "generated_future", "inflation_level", new_column_name="inflation_shock"
    )
