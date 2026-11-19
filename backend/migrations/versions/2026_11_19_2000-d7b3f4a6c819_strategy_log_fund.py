"""strategy log fund

Revision ID: d7b3f4a6c819
Revises: c5e8a2f91b73
Create Date: 2026-11-19 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7b3f4a6c819"
down_revision: str | Sequence[str] | None = "c5e8a2f91b73"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("strategy_log", sa.Column("fund_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "strategy_log_fund_id_fkey",
        "strategy_log",
        "funds",
        ["fund_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("strategy_log_fund_id_fkey", "strategy_log", type_="foreignkey")
    op.drop_column("strategy_log", "fund_id")
