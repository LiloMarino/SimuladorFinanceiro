"""keep only year review summaries

Revision ID: a3d7f1c9e5b2
Revises: f1c5d7e9a3b4
Create Date: 2026-11-03 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a3d7f1c9e5b2"
down_revision: str | Sequence[str] | None = "f1c5d7e9a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TOAST_PATH = "{notifications,toasts}"


def _rename_toast(old: str, new: str) -> None:
    """Leva a escolha do jogador sobre o aviso para o nome novo, quando ele escolheu."""
    op.execute(
        f"""
        UPDATE users
        SET settings = jsonb_set(
            settings,
            '{TOAST_PATH}',
            ((settings #> '{TOAST_PATH}') - '{old}')
                || jsonb_build_object('{new}', settings #> '{{notifications,toasts,{old}}}')
        )
        WHERE settings #> '{{notifications,toasts}}' ? '{old}'
        """
    )


def upgrade() -> None:
    op.execute("DELETE FROM summaries WHERE kind = 'MONTH_SUMMARY'")
    op.execute("ALTER TYPE summary_kind RENAME TO summary_kind_old")
    op.execute("CREATE TYPE summary_kind AS ENUM ('YEAR_REVIEW')")
    op.execute(
        "ALTER TABLE summaries ALTER COLUMN kind TYPE summary_kind "
        "USING kind::text::summary_kind"
    )
    op.execute("DROP TYPE summary_kind_old")
    _rename_toast("MONTH_SUMMARY", "YEAR_REVIEW")


def downgrade() -> None:
    _rename_toast("YEAR_REVIEW", "MONTH_SUMMARY")
    op.execute("ALTER TYPE summary_kind RENAME TO summary_kind_old")
    op.execute("CREATE TYPE summary_kind AS ENUM ('MONTH_SUMMARY', 'YEAR_REVIEW')")
    op.execute(
        "ALTER TABLE summaries ALTER COLUMN kind TYPE summary_kind "
        "USING kind::text::summary_kind"
    )
    op.execute("DROP TYPE summary_kind_old")
