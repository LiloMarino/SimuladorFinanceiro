"""add asset class and income tax

Revision ID: bfa52da39f2d
Revises: be5288fb9164
Create Date: 2026-10-09 23:23:25.599201
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "bfa52da39f2d"
down_revision: str | Sequence[str] | None = "be5288fb9164"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

asset_class = postgresql.ENUM(
    "STOCK", "FII", "ETF", "BDR", name="asset_class", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    asset_class.create(bind)

    # As ações já importadas recebem o mesmo palpite de `infer_asset_class`
    op.add_column("stock", sa.Column("asset_class", asset_class, nullable=True))
    op.execute(
        r"""
        UPDATE stock SET asset_class = CASE
            WHEN ticker ~* '(31|32|33|34|35|39)(\.SA)?$' THEN 'BDR'
            WHEN ticker ~* '11(\.SA)?$' THEN 'FII'
            ELSE 'STOCK'
        END::asset_class
        """
    )
    op.alter_column("stock", "asset_class", nullable=False)

    op.execute("ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'TAX'")


def downgrade() -> None:
    # O Postgres não remove valor de ENUM: o 'TAX' fica em cashflow_event_type
    op.drop_column("stock", "asset_class")
    asset_class.drop(op.get_bind())
