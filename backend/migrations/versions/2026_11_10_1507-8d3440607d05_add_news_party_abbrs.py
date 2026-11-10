"""add news party abbrs

Revision ID: 8d3440607d05
Revises: b7e4c2a91d36
Create Date: 2026-11-10 15:07:31.985326
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8d3440607d05"
down_revision: str | Sequence[str] | None = "b7e4c2a91d36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "news",
        sa.Column(
            "party_abbrs",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("news", "party_abbrs")
