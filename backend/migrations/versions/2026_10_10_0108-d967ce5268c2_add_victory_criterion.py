"""add victory criterion

Revision ID: d967ce5268c2
Revises: 1e7c9c4c5fb8
Create Date: 2026-10-10 01:08:12.912148
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d967ce5268c2"
down_revision: str | Sequence[str] | None = "1e7c9c4c5fb8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

victory_criterion = postgresql.ENUM(
    "SCORE", "RETURN", "NETWORTH", "SHARPE", name="victory_criterion", create_type=False
)


def upgrade() -> None:
    victory_criterion.create(op.get_bind())
    op.add_column(
        "simulations",
        sa.Column(
            "victory_criterion",
            victory_criterion,
            nullable=False,
            server_default="SCORE",
        ),
    )


def downgrade() -> None:
    op.drop_column("simulations", "victory_criterion")
    victory_criterion.drop(op.get_bind())
