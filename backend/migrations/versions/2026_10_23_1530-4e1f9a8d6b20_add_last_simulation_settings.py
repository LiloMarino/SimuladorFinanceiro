"""add last simulation settings

Revision ID: 4e1f9a8d6b20
Revises: 678977c56480
Create Date: 2026-10-23 15:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "4e1f9a8d6b20"
down_revision: str | Sequence[str] | None = "678977c56480"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "last_simulation_settings",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("id = 1", name="last_simulation_settings_single_row"),
        sa.PrimaryKeyConstraint("id", name="last_simulation_settings_pkey"),
    )


def downgrade() -> None:
    op.drop_table("last_simulation_settings")
