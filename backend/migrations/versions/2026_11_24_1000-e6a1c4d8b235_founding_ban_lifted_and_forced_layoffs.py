"""founding ban lifted and forced layoffs

Revision ID: e6a1c4d8b235
Revises: d5f9b3a7c124
Create Date: 2026-11-24 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e6a1c4d8b235"
down_revision: str | Sequence[str] | None = "d5f9b3a7c124"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulation_players",
        sa.Column("founding_ban_lifted_on", sa.Date(), nullable=True),
    )
    op.add_column(
        "simulation_players",
        sa.Column(
            "forced_layoff_days",
            postgresql.ARRAY(sa.Date()),
            server_default=sa.text("'{}'::date[]"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("simulation_players", "forced_layoff_days")
    op.drop_column("simulation_players", "founding_ban_lifted_on")
