"""reset political results

Revision ID: a6d3c8f14e27
Revises: 8d3440607d05
Create Date: 2026-11-10 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a6d3c8f14e27"
down_revision: str | Sequence[str] | None = "8d3440607d05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # O resultado guardado das partidas políticas é recalculado pelo capital político
    op.execute(
        "UPDATE simulations SET result = NULL, result_as_of = NULL "
        "WHERE rules->>'game_type' = 'POLITICAL'"
    )


def downgrade() -> None:
    pass
