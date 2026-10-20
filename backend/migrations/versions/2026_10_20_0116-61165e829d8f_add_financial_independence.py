"""add financial independence

Revision ID: 61165e829d8f
Revises: 4684a1cc504c
Create Date: 2026-10-20 01:16:46.248615
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "61165e829d8f"
down_revision: str | Sequence[str] | None = "4684a1cc504c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_NEW_CASHFLOW_TYPES = ("SALARY", "EXPENSE", "UNEXPECTED_EXPENSE", "OVERDRAFT_INTEREST")

# Partidas salvas são Clássicas ou corridas: a vida real nasce zerada, e a semente
# dos imprevistos é o id da partida
_SAVED_VALUES = {
    "monthly_salary": ("0", sa.Numeric(precision=20, scale=6)),
    "monthly_expense": ("0", sa.Numeric(precision=20, scale=6)),
    "unexpected_per_year": ("0", sa.SmallInteger()),
    "withdrawal_rate": ("0.04", sa.Numeric(precision=10, scale=6)),
    "inflation_adjusted": ("false", sa.Boolean()),
    "random_seed": ("id", sa.BigInteger()),
}


def upgrade() -> None:
    for value in _NEW_CASHFLOW_TYPES:
        op.execute(f"ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS '{value}'")
    op.add_column(
        "event_cashflow", sa.Column("life_event_key", sa.Text(), nullable=True)
    )
    for column, (value, type_) in _SAVED_VALUES.items():
        op.add_column("simulations", sa.Column(column, type_, nullable=True))
        op.execute(f"UPDATE simulations SET {column} = {value}")
        op.alter_column("simulations", column, nullable=False)


def downgrade() -> None:
    # O Postgres não remove valor de ENUM: os tipos novos ficam, sem eventos
    op.execute(
        "DELETE FROM event_cashflow WHERE event_type::text IN ("
        + ", ".join(f"'{value}'" for value in _NEW_CASHFLOW_TYPES)
        + ")"
    )
    for column in reversed(_SAVED_VALUES):
        op.drop_column("simulations", column)
    op.drop_column("event_cashflow", "life_event_key")
