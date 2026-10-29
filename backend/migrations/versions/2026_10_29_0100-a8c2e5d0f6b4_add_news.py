"""add news

Revision ID: a8c2e5d0f6b4
Revises: f7b1d4c9e5a3
Create Date: 2026-10-29 01:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a8c2e5d0f6b4"
down_revision: str | Sequence[str] | None = "f7b1d4c9e5a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEWS_TYPES = (
    "ELECTION_CALENDAR",
    "ELECTION_RESULT",
    "TERM_STARTED",
    "MEASURE_PROPOSED",
    "MEASURE_VOTED",
    "PARTY_LIFE",
    "CAMPAIGN",
)

# As preferências de aviso de antes, por chave do JSON, e o tipo de aviso que as herda
TOAST_FROM_OLD = (
    ("orders", "executed", "ORDER_EXECUTED"),
    ("orders", "partial", "ORDER_PARTIAL"),
    ("players", "join_exit", "PLAYER_PRESENCE"),
)


def upgrade() -> None:
    op.create_table(
        "news",
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
        sa.Column("news_date", sa.Date(), nullable=False),
        sa.Column("news_type", sa.Enum(*NEWS_TYPES, name="news_type"), nullable=False),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("dek", sa.Text(), nullable=True),
        sa.Column(
            "tickers",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="news_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="news_pkey"),
    )
    op.create_index(
        "news_simulation_date_idx", "news", ["simulation_id", "news_date"], unique=False
    )

    # Quem desligou um aviso continua com ele desligado no registro novo
    toasts = ", ".join(
        f"'{toast}', settings->'{section}'->'{item}'"
        for section, item, toast in TOAST_FROM_OLD
    )
    op.execute(
        f"""
        UPDATE users
        SET settings = settings || jsonb_build_object(
            'notifications',
            jsonb_build_object('toasts', jsonb_strip_nulls(jsonb_build_object({toasts})))
        )
        WHERE settings ? 'orders' OR settings ? 'players'
        """
    )


def downgrade() -> None:
    op.execute("UPDATE users SET settings = settings - 'notifications'")
    op.drop_index("news_simulation_date_idx", table_name="news")
    op.drop_table("news")
    sa.Enum(name="news_type").drop(op.get_bind())
