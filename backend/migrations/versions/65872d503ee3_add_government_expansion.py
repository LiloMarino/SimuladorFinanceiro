"""add government expansion

Revision ID: 65872d503ee3
Revises: e5d2a9b7c314
Create Date: 2026-10-22 21:15:57.957952
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "65872d503ee3"
down_revision: str | Sequence[str] | None = "e5d2a9b7c314"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE cashflow_event_type ADD VALUE IF NOT EXISTS 'CAMPAIGN'")
    op.add_column(
        "event_fixed_income",
        sa.Column(
            "withheld_tax",
            sa.Numeric(20, 6),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.create_table(
        "government_event",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("simulation_id", sa.BigInteger(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("request_key", sa.Text(), nullable=True),
        sa.Column("actor", sa.Integer(), nullable=True),
        sa.Column("outcome", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="government_event_simulation_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "simulation_id", "revision", name="government_event_revision_key"
        ),
        sa.UniqueConstraint(
            "simulation_id", "request_key", name="government_event_request_key"
        ),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "government_rules",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.execute("DELETE FROM event_cashflow WHERE event_type::text = 'CAMPAIGN'")
    op.drop_column("event_fixed_income", "withheld_tax")
    op.drop_column("simulations", "government_rules")
    op.drop_table("government_event")
