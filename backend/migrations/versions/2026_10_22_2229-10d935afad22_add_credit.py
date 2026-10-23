"""add credit

Revision ID: 10d935afad22
Revises: e5d2a9b7c314
Create Date: 2026-10-22 22:29:26.765773
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "10d935afad22"
down_revision: str | Sequence[str] | None = "e5d2a9b7c314"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_NEW_CASHFLOW_TYPES = ("LOAN_PROCEEDS", "LOAN_PAYMENT")


def upgrade() -> None:
    for value in _NEW_CASHFLOW_TYPES:
        op.execute(f"ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS '{value}'")
    op.create_table(
        "event_credit",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=9223372036854775807,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("loan_id", sa.Uuid(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "CONTRACT",
                "INSTALLMENT_PAID",
                "INSTALLMENT_LATE",
                "OVERDUE_PAID",
                "PREPAYMENT",
                "PAYOFF",
                name="credit_event_type",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column("installment_number", sa.Integer(), nullable=True),
        sa.Column("annual_rate", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("term_months", sa.Integer(), nullable=True),
        sa.Column(
            "grade",
            sa.Enum(
                "AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D", name="credit_grade"
            ),
            nullable=True,
        ),
        sa.Column(
            "prepayment_mode",
            sa.Enum(
                "SHORTEN_TERM", "REDUCE_INSTALLMENT", name="credit_prepayment_mode"
            ),
            nullable=True,
        ),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="event_credit_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="event_credit_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="event_credit_pkey"),
    )
    op.add_column(
        "snapshots",
        sa.Column(
            "total_debt",
            sa.Numeric(precision=20, scale=6),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("snapshots", "total_debt")
    op.drop_table("event_credit")
    for name in ("credit_event_type", "credit_grade", "credit_prepayment_mode"):
        sa.Enum(name=name).drop(op.get_bind())
