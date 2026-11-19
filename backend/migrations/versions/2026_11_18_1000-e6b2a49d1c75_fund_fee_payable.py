"""fund fee payable

Revision ID: e6b2a49d1c75
Revises: d5a8c13e7b92
Create Date: 2026-11-18 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e6b2a49d1c75"
down_revision: str | Sequence[str] | None = "d5a8c13e7b92"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _money_column(name: str) -> sa.Column:
    return sa.Column(
        name,
        sa.Numeric(precision=20, scale=6),
        server_default=sa.text("0"),
        nullable=False,
    )


def upgrade() -> None:
    op.add_column("funds", _money_column("management_fee_payable"))
    op.add_column("funds", _money_column("performance_fee_payable"))
    op.add_column("fund_days", _money_column("fee_payable"))


def downgrade() -> None:
    op.drop_column("fund_days", "fee_payable")
    op.drop_column("funds", "performance_fee_payable")
    op.drop_column("funds", "management_fee_payable")
