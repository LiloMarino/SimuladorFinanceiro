"""add fixed income tax withheld

Revision ID: e9c4a6b2d813
Revises: d8b3f5a1c970
Create Date: 2026-11-07 20:10:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e9c4a6b2d813"
down_revision: str | Sequence[str] | None = "d8b3f5a1c970"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "event_fixed_income",
        sa.Column(
            "tax_withheld",
            sa.Numeric(precision=20, scale=6),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("event_fixed_income", "tax_withheld")
