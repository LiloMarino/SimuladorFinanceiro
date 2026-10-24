"""add simulation result

Revision ID: 7d3e91a2b4c6
Revises: 4bf5950342b9
Create Date: 2026-10-24 18:10:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "7d3e91a2b4c6"
down_revision: str | Sequence[str] | None = "4bf5950342b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("simulations", sa.Column("result_as_of", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("simulations", "result_as_of")
    op.drop_column("simulations", "result")
