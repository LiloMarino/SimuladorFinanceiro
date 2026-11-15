"""commissioned party

Revision ID: a6d4e81c2f07
Revises: b3f19c6e2a85
Create Date: 2026-11-15 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a6d4e81c2f07"
down_revision: str | Sequence[str] | None = "b3f19c6e2a85"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("simulation_players", sa.Column("party", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("simulation_players", "party")
