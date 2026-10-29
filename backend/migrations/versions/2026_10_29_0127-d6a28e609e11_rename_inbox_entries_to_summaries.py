"""rename inbox entries to summaries

Revision ID: d6a28e609e11
Revises: a8c2e5d0f6b4
Create Date: 2026-10-29 01:27:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d6a28e609e11"
down_revision: str | Sequence[str] | None = "a8c2e5d0f6b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (nome antigo, nome novo) das constraints; o rename da PK leva o índice dela junto
CONSTRAINTS = (
    ("inbox_entries_pkey", "summaries_pkey"),
    ("inbox_entries_simulation_id_fkey", "summaries_simulation_id_fkey"),
    ("inbox_entries_user_id_fkey", "summaries_user_id_fkey"),
)


def _rename(table: str, constraints: tuple[tuple[str, str], ...]) -> None:
    for old, new in constraints:
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old} TO {new}")


def upgrade() -> None:
    op.rename_table("inbox_entries", "summaries")
    op.execute("ALTER SEQUENCE inbox_entries_id_seq RENAME TO summaries_id_seq")
    _rename("summaries", CONSTRAINTS)
    op.execute(
        "ALTER INDEX inbox_entries_simulation_user_idx "
        "RENAME TO summaries_simulation_user_idx"
    )
    op.execute("ALTER TYPE inbox_entry_kind RENAME TO summary_kind")
    op.drop_column("summaries", "read")


def downgrade() -> None:
    op.add_column(
        "summaries",
        sa.Column(
            "read", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.execute("ALTER TYPE summary_kind RENAME TO inbox_entry_kind")
    op.execute(
        "ALTER INDEX summaries_simulation_user_idx "
        "RENAME TO inbox_entries_simulation_user_idx"
    )
    _rename("summaries", tuple((new, old) for old, new in CONSTRAINTS))
    op.execute("ALTER SEQUENCE summaries_id_seq RENAME TO inbox_entries_id_seq")
    op.rename_table("summaries", "inbox_entries")
