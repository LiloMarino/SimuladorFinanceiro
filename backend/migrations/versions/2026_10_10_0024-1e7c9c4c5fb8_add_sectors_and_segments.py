"""add sectors and segments

Revision ID: 1e7c9c4c5fb8
Revises: bfa52da39f2d
Create Date: 2026-10-10 00:24:06.055183
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "1e7c9c4c5fb8"
down_revision: str | Sequence[str] | None = "bfa52da39f2d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sectors",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="sectors_pkey"),
        sa.UniqueConstraint("name", name="sectors_name_key"),
    )
    op.create_table(
        "segments",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            nullable=False,
        ),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sector_id"],
            ["sectors.id"],
            name="segments_sector_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="segments_pkey"),
        sa.UniqueConstraint("sector_id", "name", name="segments_sector_id_name_key"),
    )
    op.add_column("stock", sa.Column("segment_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "stock_segment_id_fkey",
        "stock",
        "segments",
        ["segment_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("stock_segment_id_fkey", "stock", type_="foreignkey")
    op.drop_column("stock", "segment_id")
    op.drop_table("segments")
    op.drop_table("sectors")
