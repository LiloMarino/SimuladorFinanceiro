"""add preset

Revision ID: c5a81e3f7d29
Revises: 9b2d7c41e5a3
Create Date: 2026-10-23 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c5a81e3f7d29"
down_revision: str | Sequence[str] | None = "9b2d7c41e5a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Os prontos do app: o que cada um não traz vem do padrão ao carregar
BUILT_IN_PRESETS: list[tuple[str, dict[str, object]]] = [
    (
        "Iniciante",
        {
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "starting_cash": "10000",
            "monthly_contribution": "500",
            "game_type": "CLASSIC",
            "victory_criterion": "NETWORTH",
        },
    ),
    (
        "Clássico",
        {
            "start_date": "2010-01-01",
            "end_date": "2024-12-31",
            "starting_cash": "100000",
            "monthly_contribution": "1000",
            "game_type": "CLASSIC",
            "victory_criterion": "SCORE",
        },
    ),
    (
        "Realista",
        {
            "start_date": "2000-01-01",
            "end_date": "2024-12-31",
            "game_type": "FINANCIAL_INDEPENDENCE",
            "price_impact_enabled": True,
            "price_impact_k": 0.02,
            "price_impact_decay_days": 20,
            "show_equivalent_rate": False,
            "show_maturity_projection": False,
        },
    ),
]


def upgrade() -> None:
    preset = op.create_table(
        "preset",
        sa.Column("id", sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "built_in", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="preset_pkey"),
    )
    op.create_index(
        "preset_name_lower_key", "preset", [sa.text("lower(name)")], unique=True
    )
    op.bulk_insert(
        preset,
        [
            {"name": name, "built_in": True, "config": config}
            for name, config in BUILT_IN_PRESETS
        ],
    )


def downgrade() -> None:
    op.drop_index("preset_name_lower_key", table_name="preset")
    op.drop_table("preset")
