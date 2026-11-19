"""fund manager leave

Revision ID: c5e8a2f91b73
Revises: a9d4e17c3b62
Create Date: 2026-11-19 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5e8a2f91b73"
down_revision: str | Sequence[str] | None = "a9d4e17c3b62"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "funds", sa.Column("leave_manager_user_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "funds", sa.Column("leave_heir_share", sa.Numeric(8, 6), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("funds", "leave_heir_share")
    op.drop_column("funds", "leave_manager_user_id")
