"""drop stock name unique

Revision ID: 9707da5dfa82
Revises: c5a4bf0941a9
Create Date: 2026-10-21 14:45:12.480317
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "9707da5dfa82"
down_revision: str | Sequence[str] | None = "c5a4bf0941a9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("stock_name_key", "stock", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("stock_name_key", "stock", ["name"])
