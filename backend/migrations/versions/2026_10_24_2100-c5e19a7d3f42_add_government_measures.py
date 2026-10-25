"""add government measures

Revision ID: c5e19a7d3f42
Revises: a8c4e17b9d32
Create Date: 2026-10-24 21:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "c5e19a7d3f42"
down_revision: str | Sequence[str] | None = "a8c4e17b9d32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_EVENT_TYPES = (
    "MEASURE_PROPOSED",
    "MEASURE_WITHDRAWN",
    "MEASURE_VOTED",
    "APPROVAL_MEASURED",
    "IMPEACHED",
)


def upgrade() -> None:
    # ADD VALUE não roda dentro de transação em alguns bancos; o bloco autocommit vale para todos
    with op.get_context().autocommit_block():
        for value in NEW_EVENT_TYPES:
            op.execute(
                f"ALTER TYPE government_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )


def downgrade() -> None:
    # Valor de enum do Postgres não sai sem recriar o tipo; os eventos novos ficam sem uso
    pass
