"""add stock origin

Revision ID: b7d2e94a1c35
Revises: e08aeb7e4193
Create Date: 2026-11-09 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7d2e94a1c35"
down_revision: str | Sequence[str] | None = "e08aeb7e4193"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sa.Enum("DOMESTIC", "FOREIGN", name="asset_origin").create(op.get_bind())
    op.add_column(
        "stock",
        sa.Column(
            "origin",
            sa.Enum("DOMESTIC", "FOREIGN", name="asset_origin"),
            server_default=sa.text("'DOMESTIC'"),
            nullable=False,
        ),
    )
    # Cotado em dólar ou BDR já é internacional
    op.execute(
        "UPDATE stock SET origin = 'FOREIGN' WHERE currency = 'USD' OR asset_class = 'BDR'"
    )


def downgrade() -> None:
    op.drop_column("stock", "origin")
    sa.Enum(name="asset_origin").drop(op.get_bind())
