"""keep achievements of deleted simulations

Revision ID: 5836e0819ac7
Revises: 4273c3c8578a
Create Date: 2026-10-25 19:02:56.287404
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5836e0819ac7"
down_revision: str | Sequence[str] | None = "4273c3c8578a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "achievements", "simulation_id", existing_type=sa.BIGINT(), nullable=True
    )
    op.drop_constraint(
        op.f("achievements_simulation_id_fkey"), "achievements", type_="foreignkey"
    )
    op.create_foreign_key(
        "achievements_simulation_id_fkey",
        "achievements",
        "simulations",
        ["simulation_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # O schema anterior exige a partida: a conquista sem ela sai junto
    op.execute("DELETE FROM achievements WHERE simulation_id IS NULL")
    op.drop_constraint(
        "achievements_simulation_id_fkey", "achievements", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("achievements_simulation_id_fkey"),
        "achievements",
        "simulations",
        ["simulation_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.alter_column(
        "achievements", "simulation_id", existing_type=sa.BIGINT(), nullable=False
    )
