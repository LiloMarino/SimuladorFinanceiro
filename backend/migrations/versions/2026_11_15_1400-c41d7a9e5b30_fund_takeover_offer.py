"""fund takeover offer

Revision ID: c41d7a9e5b30
Revises: 2e27ab7ada58
Create Date: 2026-11-14 22:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c41d7a9e5b30"
down_revision: str | Sequence[str] | None = "2e27ab7ada58"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("funds", sa.Column("takeover_offer_on", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("funds", "takeover_offer_on")
