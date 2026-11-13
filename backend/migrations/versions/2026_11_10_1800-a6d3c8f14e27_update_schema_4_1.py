"""update schema 4.1

Revision ID: a6d3c8f14e27
Revises: f3a8c5d1b764
Create Date: 2026-11-10 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a6d3c8f14e27"
down_revision: str | Sequence[str] | None = "f3a8c5d1b764"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A ordem dos valores segue a dos enums do Python
INDICATOR_SERIES = (
    "PTAX",
    "FOCUS_SELIC",
    "FOCUS_IPCA",
    "FOCUS_GDP",
    "FOCUS_FX",
    "FED_FUNDS",
)


def upgrade() -> None:
    # Todas as tabelas que usam o enum compartilham o tipo indicator_series
    for series in INDICATOR_SERIES:
        op.execute(f"ALTER TYPE indicator_series ADD VALUE IF NOT EXISTS '{series}'")

    # Moeda e origem do ativo: a origem dos que já existem sai da moeda e da classe
    sa.Enum("BRL", "USD", name="currency").create(op.get_bind())
    op.add_column(
        "stock",
        sa.Column(
            "currency",
            sa.Enum("BRL", "USD", name="currency"),
            server_default=sa.text("'BRL'"),
            nullable=False,
        ),
    )
    sa.Enum("DOMESTIC", "FOREIGN", name="asset_origin").create(op.get_bind())
    op.add_column(
        "stock",
        sa.Column(
            "origin",
            sa.Enum("DOMESTIC", "FOREIGN", name="asset_origin"),
            server_default=sa.text("'DOMESTIC'"),
            nullable=False,
        ),
    )
    op.execute(
        "UPDATE stock SET origin = 'FOREIGN' WHERE currency = 'USD' OR asset_class = 'BDR'"
    )

    # Conta em dólar, que rende o juro americano
    op.execute("ALTER TYPE investment_type ADD VALUE IF NOT EXISTS 'DOLLAR_ACCOUNT'")
    op.execute("ALTER TYPE rate_type ADD VALUE IF NOT EXISTS 'FED_FUNDS'")
    op.add_column(
        "event_fixed_income", sa.Column("fx_rate", sa.Numeric(20, 8), nullable=True)
    )

    op.add_column(
        "simulation_players", sa.Column("profession", sa.Text(), nullable=True)
    )
    op.add_column(
        "news",
        sa.Column(
            "party_abbrs",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
    )

    # O resultado guardado das partidas políticas é recalculado pelo capital político
    op.execute(
        "UPDATE simulations SET result = NULL, result_as_of = NULL "
        "WHERE rules->>'game_type' = 'POLITICAL'"
    )


def downgrade() -> None:
    # O PostgreSQL não remove valor de enum: os valores novos ficam nos tipos
    op.drop_column("news", "party_abbrs")
    op.drop_column("simulation_players", "profession")
    op.drop_column("event_fixed_income", "fx_rate")
    op.drop_column("stock", "origin")
    sa.Enum(name="asset_origin").drop(op.get_bind())
    op.drop_column("stock", "currency")
    sa.Enum(name="currency").drop(op.get_bind())
