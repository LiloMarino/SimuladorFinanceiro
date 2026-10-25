"""add candle challenge

Revision ID: 4273c3c8578a
Revises: c5e19a7d3f42
Create Date: 2026-10-25 16:19:23.992125
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4273c3c8578a"
down_revision: str | Sequence[str] | None = "c5e19a7d3f42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candle_challenges",
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("pattern_date", sa.Date(), nullable=False),
        sa.Column("pattern_code", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("answered_on", sa.Date(), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("settled_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="candle_challenges_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="candle_challenges_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id",
            "user_id",
            "ticker",
            "pattern_date",
            name="candle_challenges_pkey",
        ),
    )
    op.create_index(
        "candle_challenges_open_idx",
        "candle_challenges",
        ["simulation_id", "result"],
        unique=False,
    )
    op.add_column(
        "simulations",
        sa.Column(
            "show_chart_hints",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    # O Realista já desliga as outras ajudas: a das dicas de análise técnica vai junto
    op.execute(
        "UPDATE preset SET config = config || jsonb_build_object('show_chart_hints', false) "
        "WHERE built_in AND name = 'Realista'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE preset SET config = config - 'show_chart_hints' "
        "WHERE built_in AND name = 'Realista'"
    )
    op.drop_column("simulations", "show_chart_hints")
    op.drop_index("candle_challenges_open_idx", table_name="candle_challenges")
    op.drop_table("candle_challenges")
