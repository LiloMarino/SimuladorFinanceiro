"""add series version and generated future

Revision ID: c5a4bf0941a9
Revises: 61165e829d8f
Create Date: 2026-10-21 00:29:33.229117
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5a4bf0941a9"
down_revision: str | Sequence[str] | None = "61165e829d8f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A versão entra na chave das séries; o autogenerate não troca chave primária
_SERIES_KEYS = {
    "economic_indicator_history": ("series", "ref_date"),
    "stock_price_history": ("stock_id", "price_date"),
}


def _replace_primary_key(table: str, columns: Sequence[str]) -> None:
    op.drop_constraint(f"{table}_pkey", table, type_="primary")
    op.create_primary_key(f"{table}_pkey", table, list(columns))


def upgrade() -> None:
    op.create_table(
        "generated_future",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("seed", sa.BigInteger(), nullable=False),
        sa.Column("temperature", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column(
            "start_regime",
            sa.Enum("CALM", "NORMAL", "AGITATED", name="market_regime"),
            nullable=True,
        ),
        sa.Column("inflation_shock", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("until", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("real_advanced_until", sa.Date(), nullable=True),
        sa.CheckConstraint("id = 1", name="generated_future_single_row"),
        sa.PrimaryKeyConstraint("id", name="generated_future_pkey"),
    )
    op.add_column(
        "economic_indicator_history",
        sa.Column(
            "version", sa.BigInteger(), server_default=sa.text("0"), nullable=False
        ),
    )
    op.add_column(
        "stock_price_history",
        sa.Column(
            "version", sa.BigInteger(), server_default=sa.text("0"), nullable=False
        ),
    )
    for table, key in _SERIES_KEYS.items():
        _replace_primary_key(table, (*key, "version"))


def downgrade() -> None:
    # As cópias das partidas não cabem na chave antiga
    for table, key in _SERIES_KEYS.items():
        op.execute(f"DELETE FROM {table} WHERE version <> 0")
        _replace_primary_key(table, key)
    op.drop_column("stock_price_history", "version")
    op.drop_column("economic_indicator_history", "version")
    op.drop_table("generated_future")
    sa.Enum(name="market_regime").drop(op.get_bind())
