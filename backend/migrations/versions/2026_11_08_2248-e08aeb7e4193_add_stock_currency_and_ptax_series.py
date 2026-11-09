"""add stock currency and ptax series

Revision ID: e08aeb7e4193
Revises: f3a8c5d1b764
Create Date: 2026-11-08 22:48:40.733024
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e08aeb7e4193"
down_revision: str | Sequence[str] | None = "f3a8c5d1b764"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS 'PTAX'")
    sa.Enum("BRL", "USD", name="currency").create(op.get_bind())
    op.add_column(
        "stock",
        sa.Column(
            "currency",
            sa.Enum("BRL", "USD", name="currency"),
            server_default=sa.text("'BRL'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("stock", "currency")
    sa.Enum(name="currency").drop(op.get_bind())
