"""add economic indicators

Revision ID: be5288fb9164
Revises: 243ae671fdc0
Create Date: 2026-10-09 22:22:47.848612
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "be5288fb9164"
down_revision: str | Sequence[str] | None = "243ae671fdc0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Os dois tipos são compartilhados entre colunas: nascem uma vez, antes das tabelas
indicator_series = postgresql.ENUM(
    "CDI", "SELIC", "IPCA", "IBOV", name="indicator_series", create_type=False
)
data_origin = postgresql.ENUM(
    "REAL", "GENERATED", name="data_origin", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    indicator_series.create(bind)
    data_origin.create(bind)

    op.create_table(
        "economic_indicator_history",
        sa.Column(
            "series",
            indicator_series,
            nullable=False,
        ),
        sa.Column("ref_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("origin", data_origin, nullable=False),
        sa.PrimaryKeyConstraint(
            "series", "ref_date", name="economic_indicator_history_pkey"
        ),
    )
    op.create_table(
        "fetch_log",
        sa.Column(
            "series",
            indicator_series,
            nullable=False,
        ),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("succeeded_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("series", name="fetch_log_pkey"),
    )
    op.drop_table("selic_history")
    op.drop_table("ipca_history")
    op.add_column(
        "stock_price_history",
        sa.Column(
            "origin",
            data_origin,
            server_default=sa.text("'REAL'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("stock_price_history", "origin")
    op.create_table(
        "ipca_history",
        sa.Column("ref_month", sa.DATE(), autoincrement=False, nullable=False),
        sa.Column(
            "rate_value",
            sa.NUMERIC(precision=10, scale=6),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("ref_month", name=op.f("ipca_history_pkey")),
    )
    op.create_table(
        "selic_history",
        sa.Column("rate_date", sa.DATE(), autoincrement=False, nullable=False),
        sa.Column(
            "rate_value",
            sa.NUMERIC(precision=10, scale=6),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("rate_date", name=op.f("selic_history_pkey")),
    )
    op.drop_table("fetch_log")
    op.drop_table("economic_indicator_history")

    bind = op.get_bind()
    data_origin.drop(bind)
    indicator_series.drop(bind)
