"""add player profession

Revision ID: b7e4c2a91d36
Revises: 8d3b5f20a6c1
Create Date: 2026-11-09 17:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7e4c2a91d36"
down_revision: str | Sequence[str] | None = "8d3b5f20a6c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulation_players", sa.Column("profession", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("simulation_players", "profession")
