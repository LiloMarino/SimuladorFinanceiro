"""add government expansion

Revision ID: a8c4e17b9d32
Revises: f3a6c2d85b17
Create Date: 2026-10-24 20:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a8c4e17b9d32"
down_revision: str | Sequence[str] | None = "f3a6c2d85b17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

GOVERNMENT_EVENT_TYPE = postgresql.ENUM(
    "PARTY_FOUNDED",
    "COMPUTER_PARTY_ADDED",
    "COMPUTER_PARTY_REMOVED",
    "PARTY_JOINED",
    "PARTY_LEFT",
    "MEMBER_EXPELLED",
    "CONTRIBUTION_SET",
    "TICKET_SET",
    "VICE_ANSWERED",
    "CAMPAIGN_SPENT",
    "DONATION_MADE",
    "ELECTION_ROUND",
    "TERM_STARTED",
    name="government_event_type",
    create_type=False,
)
COMPUTER_DIFFICULTY = postgresql.ENUM(
    "EASY", "NORMAL", "HARD", name="computer_difficulty", create_type=False
)


def upgrade() -> None:
    # ADD VALUE não roda dentro de transação em alguns bancos; o bloco autocommit vale para todos
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE game_type ADD VALUE IF NOT EXISTS 'POLITICAL'")
        op.execute(
            "ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN_CONTRIBUTION'"
        )
        op.execute(
            "ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN_DONATION'"
        )
    COMPUTER_DIFFICULTY.create(op.get_bind(), checkfirst=True)
    GOVERNMENT_EVENT_TYPE.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "simulations",
        sa.Column(
            "government_enabled",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column("simulations", sa.Column("first_election", sa.Date(), nullable=True))
    op.add_column(
        "simulations",
        sa.Column(
            "computer_difficulty",
            COMPUTER_DIFFICULTY,
            server_default=sa.text("'NORMAL'"),
            nullable=False,
        ),
    )
    op.create_table(
        "government_event",
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
        sa.Column("event_type", GOVERNMENT_EVENT_TYPE, nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="government_event_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="government_event_pkey"),
    )
    op.create_index(
        "government_event_simulation_id_idx",
        "government_event",
        ["simulation_id", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("government_event_simulation_id_idx", table_name="government_event")
    op.drop_table("government_event")
    op.drop_column("simulations", "computer_difficulty")
    op.drop_column("simulations", "first_election")
    op.drop_column("simulations", "government_enabled")
    GOVERNMENT_EVENT_TYPE.drop(op.get_bind(), checkfirst=True)
    COMPUTER_DIFFICULTY.drop(op.get_bind(), checkfirst=True)
    # O Postgres não remove valor de ENUM: os valores novos ficam, sem uso
    op.execute(
        "UPDATE simulations SET game_type = 'CLASSIC' WHERE game_type = 'POLITICAL'"
    )
