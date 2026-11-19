"""fund manager since

Revision ID: f7c3b58e2d41
Revises: 55d31789e090
Create Date: 2026-11-19 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f7c3b58e2d41"
down_revision: str | Sequence[str] | None = "55d31789e090"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("funds", sa.Column("manager_since", sa.Date(), nullable=True))
    # As gestoras que já existem: o dia da última troca de gestor pela assembleia e, sem troca,
    # o dia da oferta pública; a que nunca listou fica sem data
    op.execute(
        """
        UPDATE funds
        SET manager_since = COALESCE(
            (
                SELECT MAX(closed_on)
                FROM fund_assemblies
                WHERE fund_assemblies.fund_id = funds.id AND status = 'REPLACED'
            ),
            listed_on
        )
        """
    )


def downgrade() -> None:
    op.drop_column("funds", "manager_since")
