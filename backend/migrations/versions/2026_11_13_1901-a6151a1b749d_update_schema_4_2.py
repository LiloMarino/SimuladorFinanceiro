"""update schema 4.2

Revision ID: a6151a1b749d
Revises: a6d3c8f14e27
Create Date: 2026-11-13 19:01:07.890926
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a6151a1b749d"
down_revision: str | Sequence[str] | None = "a6d3c8f14e27"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Tabelas que passam do jogador para a carteira: as de evento têm o índice
# (partida, dono, dia) e `snapshots` leva o dono na chave primária
EVENT_TABLES = ("event_cashflow", "event_equity", "event_fixed_income", "event_credit")
OWNED_TABLES = (*EVENT_TABLES, "snapshots")


def _index_columns(owner: str) -> list[str]:
    return ["simulation_id", owner, "event_date"]


def upgrade() -> None:
    op.create_table(
        "portfolios",
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
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("starting_cash", sa.Numeric(precision=20, scale=6), nullable=False),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            name="portfolios_simulation_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="portfolios_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="portfolios_pkey"),
        sa.UniqueConstraint(
            "simulation_id", "user_id", name="portfolios_simulation_id_user_id_key"
        ),
    )

    # Uma carteira por jogador de cada partida salva: quem tem evento ou snapshot
    # sem estar em `simulation_players` também ganha a dele, sem linha órfã. Nas
    # partidas antigas todo jogador recebeu o `starting_cash` da sala, e é ele que
    # a carteira guarda como capital inicial
    pairs = " UNION ".join(
        f"SELECT simulation_id, user_id FROM {table}"
        for table in ("simulation_players", *OWNED_TABLES)
    )
    op.execute(
        "INSERT INTO portfolios (simulation_id, user_id, created_at, starting_cash) "
        "SELECT owners.simulation_id, owners.user_id, now(), "
        "COALESCE((s.rules ->> 'starting_cash')::numeric, 0) "
        f"FROM ({pairs}) AS owners "
        "JOIN simulations AS s ON s.id = owners.simulation_id "
        "ORDER BY owners.simulation_id, owners.user_id"
    )

    for table in OWNED_TABLES:
        op.add_column(table, sa.Column("portfolio_id", sa.BigInteger(), nullable=True))
        op.execute(
            f"UPDATE {table} AS t SET portfolio_id = p.id FROM portfolios AS p "
            "WHERE p.simulation_id = t.simulation_id AND p.user_id = t.user_id"
        )
        op.alter_column(table, "portfolio_id", nullable=False)

        if table == "snapshots":
            op.drop_constraint("snapshots_pkey", table, type_="primary")
        else:
            op.drop_index(f"{table}_simulation_user_idx", table_name=table)
        op.drop_constraint(f"{table}_user_id_fkey", table, type_="foreignkey")
        op.drop_column(table, "user_id")

        op.create_foreign_key(
            f"{table}_portfolio_id_fkey",
            table,
            "portfolios",
            ["portfolio_id"],
            ["id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
        if table == "snapshots":
            op.create_primary_key(
                "snapshots_pkey",
                table,
                ["simulation_id", "portfolio_id", "snapshot_date"],
            )
        else:
            op.create_index(
                f"{table}_simulation_portfolio_idx",
                table,
                _index_columns("portfolio_id"),
            )


def downgrade() -> None:
    for table in OWNED_TABLES:
        op.add_column(table, sa.Column("user_id", sa.Integer(), nullable=True))
        op.execute(
            f"UPDATE {table} AS t SET user_id = p.user_id FROM portfolios AS p "
            "WHERE p.id = t.portfolio_id"
        )
        op.alter_column(table, "user_id", nullable=False)

        if table == "snapshots":
            op.drop_constraint("snapshots_pkey", table, type_="primary")
        else:
            op.drop_index(f"{table}_simulation_portfolio_idx", table_name=table)
        op.drop_constraint(f"{table}_portfolio_id_fkey", table, type_="foreignkey")
        op.drop_column(table, "portfolio_id")

        op.create_foreign_key(
            f"{table}_user_id_fkey",
            table,
            "users",
            ["user_id"],
            ["id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
        if table == "snapshots":
            op.create_primary_key(
                "snapshots_pkey", table, ["simulation_id", "user_id", "snapshot_date"]
            )
        else:
            op.create_index(
                f"{table}_simulation_user_idx", table, _index_columns("user_id")
            )

    op.drop_table("portfolios")
