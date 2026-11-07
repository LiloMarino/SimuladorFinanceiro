"""add corporate events

Revision ID: d8b3f5a1c970
Revises: c4a7e1d9b256
Create Date: 2026-11-07 18:41:29.306847
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d8b3f5a1c970"
down_revision: str | Sequence[str] | None = "c4a7e1d9b256"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE roda fora de transação: o bloco autocommit vale para todos os bancos
    with op.get_context().autocommit_block():
        for value in ("SPLIT", "FRACTION_SELL"):
            op.execute(
                f"ALTER TYPE equity_event_type ADD VALUE IF NOT EXISTS '{value}'"
            )
    op.create_table(
        "stock_corporate_event",
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("ex_date", sa.Date(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("SPLIT", "DIVIDEND", name="corporate_event_kind"),
            nullable=False,
        ),
        sa.Column("value", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column(
            "origin",
            # O tipo data_origin já existe: o preço e os indicadores o usam
            postgresql.ENUM("REAL", "GENERATED", name="data_origin", create_type=False),
            server_default=sa.text("'REAL'"),
            nullable=False,
        ),
        sa.Column(
            "version", sa.BigInteger(), server_default=sa.text("0"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            name="stock_corporate_event_stock_id_fkey",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "stock_id", "ex_date", "kind", "version", name="stock_corporate_event_pkey"
        ),
    )
    op.add_column("event_cashflow", sa.Column("stock_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "event_cashflow_stock_id_fkey",
        "event_cashflow",
        "stock",
        ["stock_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "event_cashflow_stock_id_fkey", "event_cashflow", type_="foreignkey"
    )
    op.drop_column("event_cashflow", "stock_id")
    op.drop_table("stock_corporate_event")
    sa.Enum(name="corporate_event_kind").drop(op.get_bind())
    # Valor de enum do Postgres só sai recriando o tipo; os valores de equity_event_type ficam sem uso
