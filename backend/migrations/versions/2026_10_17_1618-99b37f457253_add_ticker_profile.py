"""add ticker profile

Revision ID: 99b37f457253
Revises: a3f1c9d27b58
Create Date: 2026-10-17 16:18:52.392310
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "99b37f457253"
down_revision: str | Sequence[str] | None = "a3f1c9d27b58"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ticker_profile",
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("quote_type", sa.Text(), nullable=True),
        sa.Column("sector", sa.Text(), nullable=True),
        sa.Column("industry", sa.Text(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("ticker", name="ticker_profile_pkey"),
    )


def downgrade() -> None:
    op.drop_table("ticker_profile")
