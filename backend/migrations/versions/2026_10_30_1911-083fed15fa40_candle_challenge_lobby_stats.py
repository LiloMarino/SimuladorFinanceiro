"""candle challenge lobby stats

Revision ID: 083fed15fa40
Revises: e9b4c6d8f0a2
Create Date: 2026-10-30 19:11:53.604248
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "083fed15fa40"
down_revision: str | Sequence[str] | None = "e9b4c6d8f0a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candle_challenge_stats",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hits", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "best_streak", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("best_streak_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="candle_challenge_stats_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name="candle_challenge_stats_pkey"),
    )
    # Quem já acertou desafios nas partidas não perde o progresso: o total passa para a tabela nova
    op.execute(
        "INSERT INTO candle_challenge_stats (user_id, hits) "
        "SELECT user_id, count(*) FROM candle_challenges "
        "WHERE result = 'hit' GROUP BY user_id"
    )
    op.drop_index(op.f("candle_challenges_open_idx"), table_name="candle_challenges")
    op.drop_table("candle_challenges")


def downgrade() -> None:
    op.create_table(
        "candle_challenges",
        sa.Column("simulation_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("ticker", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column("pattern_date", sa.DATE(), autoincrement=False, nullable=False),
        sa.Column("pattern_code", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column("direction", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column("answered_on", sa.DATE(), autoincrement=False, nullable=False),
        sa.Column("result", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("settled_on", sa.DATE(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name=op.f("candle_challenges_simulation_id_fkey"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("candle_challenges_user_id_fkey"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "simulation_id",
            "user_id",
            "ticker",
            "pattern_date",
            name=op.f("candle_challenges_pkey"),
        ),
    )
    op.create_index(
        op.f("candle_challenges_open_idx"),
        "candle_challenges",
        ["simulation_id", "result"],
        unique=False,
    )
    op.drop_table("candle_challenge_stats")
