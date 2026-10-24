"""add price correction

Revision ID: f3a6c2d85b17
Revises: 7d3e91a2b4c6
Create Date: 2026-10-24 19:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f3a6c2d85b17"
down_revision: str | Sequence[str] | None = "7d3e91a2b4c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "stock_price_history",
        sa.Column(
            "price_corrected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.create_table(
        "import_settings",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column(
            "correct_price_errors",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name="import_settings_single_row"),
        sa.PrimaryKeyConstraint("id", name="import_settings_pkey"),
    )


def downgrade() -> None:
    op.drop_table("import_settings")
    op.drop_column("stock_price_history", "price_corrected")
