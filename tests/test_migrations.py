"""As migrations chegam exatamente no schema dos models, o `migrate` guarda só os
backups mais recentes e recomeça o banco que a linha de revisões não cobre."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from decimal import Decimal

import pytest
from alembic import command
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

from backend.core.migration import (
    alembic_config,
    backups_to_drop,
    current_revision,
    drop_databases,
    ensure_database,
    head_revision,
    schema_diff,
)
from backend.core.migration import (
    migrate as migrate_database,
)


def test_schema_matches_models(migrated_template: URL) -> None:
    """O banco modelo da sessão subiu até o head, e o `schema_diff` não acha diferença."""
    # Sem pool: o modelo só aceita ser copiado sem nenhuma conexão aberta nele.
    engine = create_engine(migrated_template, poolclass=NullPool)
    try:
        assert schema_diff(engine) == []
        assert current_revision(engine) == head_revision()
    finally:
        engine.dispose()


def test_only_the_latest_backups_are_kept() -> None:
    backups = [
        "db_bkp_20261003_101500",
        "db_bkp_20261001_090000",
        "db_bkp_20261009_120000",
        "db_bkp_20261005_080000",
    ]

    assert backups_to_drop(backups, keep=3) == ["db_bkp_20261001_090000"]
    assert backups_to_drop(backups[:2], keep=3) == []


@pytest.fixture
def scratch_url(pg_server: URL) -> Iterator[URL]:
    """Banco novo e vazio, apagado com os backups que o teste gerar."""
    url = pg_server.set(database=f"simfin_mig_{uuid.uuid4().hex[:8]}")
    ensure_database(url)
    try:
        yield url
    finally:
        drop_databases(url, [str(url.database), *_backups_of(url)])


def _backups_of(url: URL) -> list[str]:
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    try:
        with admin.connect() as connection:
            return list(
                connection.execute(
                    text(
                        "SELECT datname FROM pg_database WHERE starts_with(datname, :prefix)"
                    ),
                    {"prefix": f"{url.database}_bkp_"},
                ).scalars()
            )
    finally:
        admin.dispose()


def _scalar(url: URL, sql: str) -> object:
    engine = create_engine(url, poolclass=NullPool)
    try:
        with engine.connect() as connection:
            return connection.execute(text(sql)).scalar()
    finally:
        engine.dispose()


def test_empty_database_comes_up_with_the_built_in_presets(scratch_url: URL) -> None:
    migrate_database(scratch_url.render_as_string(hide_password=False))

    names = _scalar(
        scratch_url,
        "SELECT string_agg(name, ',' ORDER BY id) FROM preset WHERE built_in",
    )
    assert names == "Iniciante,Clássico,Realista"
    assert _scalar(scratch_url, "SELECT version_num FROM alembic_version") == (
        head_revision()
    )


def test_database_in_an_unknown_revision_goes_to_backup_and_restarts_empty(
    scratch_url: URL,
) -> None:
    engine = create_engine(scratch_url, poolclass=NullPool)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE old_game (id int)"))
        connection.execute(text("INSERT INTO old_game VALUES (7)"))
        connection.execute(
            text("CREATE TABLE alembic_version (version_num varchar(32) NOT NULL)")
        )
        connection.execute(text("INSERT INTO alembic_version VALUES ('ffffffffffff')"))
    engine.dispose()

    migrate_database(scratch_url.render_as_string(hide_password=False))

    assert _scalar(scratch_url, "SELECT to_regclass('old_game')") is None
    assert _scalar(scratch_url, "SELECT version_num FROM alembic_version") == (
        head_revision()
    )
    (backup,) = _backups_of(scratch_url)
    assert _scalar(scratch_url.set(database=backup), "SELECT id FROM old_game") == 7


def test_database_without_revision_and_unlike_the_models_restarts_empty(
    scratch_url: URL,
) -> None:
    engine = create_engine(scratch_url, poolclass=NullPool)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE old_game (id int)"))
    engine.dispose()

    migrate_database(scratch_url.render_as_string(hide_password=False))

    assert _scalar(scratch_url, "SELECT to_regclass('old_game')") is None
    assert len(_backups_of(scratch_url)) == 1
    assert _scalar(scratch_url, "SELECT count(*) FROM preset") == 3


# A última revisão antes de a carteira nascer
BEFORE_PORTFOLIOS = "a6d3c8f14e27"

# Ana e Bia jogam a partida 1; só a Ana joga a 2; o Caio tem evento na 1 sem estar
# entre os jogadores
PLAYERS = ((1, 1), (1, 2), (2, 1))
OWNERS = (*PLAYERS, (1, 3))
NOW = "2026-01-01T00:00:00+00"
# Tabela, coluna que guarda um valor múltiplo do id do jogador e o fator
VALUES_BY_OWNER = (
    ("event_cashflow", "amount", 1000),
    ("event_equity", "quantity", 1),
    ("event_fixed_income", "amount", 100),
    ("event_credit", "amount", 500),
    ("snapshots", "total_cash", 1000),
)


def _seed_saved_match(connection: Connection) -> None:
    """Uma partida no schema anterior à carteira, com eventos dos 4 tipos e snapshots."""
    for nickname in ("ana", "bia", "caio"):
        connection.execute(
            text(
                "INSERT INTO users (client_id, nickname, created_at) "
                "VALUES (gen_random_uuid(), :nickname, :now)"
            ),
            {"nickname": nickname, "now": NOW},
        )
    for name, rules in (
        ("Partida 1", '{"starting_cash": "10000"}'),
        ("Partida 2", '{"starting_cash": "25000.5"}'),
    ):
        connection.execute(
            text(
                "INSERT INTO simulations (name, random_seed, rules, created_at, "
                "last_simulated_at) VALUES (:name, 7, CAST(:rules AS jsonb), :now, :now)"
            ),
            {"name": name, "rules": rules, "now": NOW},
        )
    for simulation_id, user_id in PLAYERS:
        connection.execute(
            text(
                "INSERT INTO simulation_players (simulation_id, user_id, color) "
                "VALUES (:simulation_id, :user_id, :color)"
            ),
            {
                "simulation_id": simulation_id,
                "user_id": user_id,
                "color": f"color{simulation_id}{user_id}",
            },
        )
    connection.execute(
        text(
            "INSERT INTO stock (ticker, name, asset_class) "
            "VALUES ('AAA3', 'Empresa A', 'STOCK')"
        )
    )
    connection.execute(
        text(
            "INSERT INTO fixed_income_asset (simulation_id, asset_uuid, name, issuer, "
            "investment_type, rate_type, maturity_date, interest_rate) VALUES "
            "(1, gen_random_uuid(), 'CDB', 'Banco', 'CDB', 'CDI', '2030-01-01', 1)"
        )
    )
    for simulation_id, user_id in OWNERS:
        owner = {"simulation_id": simulation_id, "user_id": user_id, "now": NOW}
        connection.execute(
            text(
                "INSERT INTO event_cashflow (simulation_id, user_id, event_type, "
                "amount, event_date, created_at) VALUES (:simulation_id, :user_id, "
                "'DEPOSIT', 1000 * :user_id, '2000-01-03', :now)"
            ),
            owner,
        )
        for day in ("2000-01-03", "2000-01-04"):
            connection.execute(
                text(
                    "INSERT INTO snapshots (simulation_id, user_id, snapshot_date, "
                    "total_equity, total_fixed, total_cash, total_contribution, "
                    "total_debt, total_networth, equity_by_class, created_at) VALUES "
                    "(:simulation_id, :user_id, :day, 0, 0, 1000 * :user_id, 0, 0, 0, "
                    "'{}', :now)"
                ),
                {**owner, "day": day},
            )
        if (simulation_id, user_id) not in PLAYERS or simulation_id == 2:
            continue
        connection.execute(
            text(
                "INSERT INTO event_equity (simulation_id, user_id, stock_id, event_type, "
                "quantity, price, event_date, created_at) VALUES (:simulation_id, "
                ":user_id, 1, 'BUY', :user_id, 5, '2000-01-04', :now)"
            ),
            owner,
        )
        connection.execute(
            text(
                "INSERT INTO event_fixed_income (simulation_id, user_id, asset_id, "
                "event_type, amount, tax_withheld, event_date, created_at) VALUES "
                "(:simulation_id, :user_id, 1, 'BUY', 100 * :user_id, 0, "
                "'2000-01-04', :now)"
            ),
            owner,
        )
        connection.execute(
            text(
                "INSERT INTO event_credit (simulation_id, user_id, loan_id, event_type, "
                "amount, event_date, created_at) VALUES (:simulation_id, :user_id, "
                "gen_random_uuid(), 'CONTRACT', 500 * :user_id, '2000-01-05', :now)"
            ),
            owner,
        )


def _row_counts(connection: Connection) -> dict[str, int]:
    return {
        table: connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()  # noqa: S608
        for table, _, _ in VALUES_BY_OWNER
    }


def test_saved_match_gets_one_portfolio_per_player(scratch_url: URL) -> None:
    """
    A partida salva no schema anterior chega ao head com uma carteira por jogador, e
    cada evento e cada snapshot aponta para a carteira do `(partida, jogador)` dele.
    """
    url = scratch_url.render_as_string(hide_password=False)
    command.upgrade(alembic_config(url), BEFORE_PORTFOLIOS)
    engine = create_engine(scratch_url, poolclass=NullPool)
    with engine.begin() as connection:
        _seed_saved_match(connection)
        counts = _row_counts(connection)
    engine.dispose()

    migrate_database(url)

    engine = create_engine(scratch_url, poolclass=NullPool)
    with engine.connect() as connection:
        portfolios = [
            (simulation_id, user_id)
            for simulation_id, user_id in connection.execute(
                text("SELECT simulation_id, user_id FROM portfolios")
            )
        ]
        assert sorted(portfolios) == sorted(OWNERS)
        # O capital inicial de cada carteira é o `starting_cash` da partida em que ela abriu
        cash = {
            simulation_id: starting_cash
            for simulation_id, starting_cash in connection.execute(
                text("SELECT DISTINCT simulation_id, starting_cash FROM portfolios")
            )
        }
        assert cash == {1: 10000, 2: Decimal("25000.5")}
        assert _row_counts(connection) == counts
        for table, column, factor in VALUES_BY_OWNER:
            # A carteira é da mesma partida e do jogador de quem o valor da linha era
            misplaced = connection.execute(
                text(
                    f"SELECT count(*) FROM {table} AS t JOIN portfolios AS p "  # noqa: S608
                    "ON p.id = t.portfolio_id WHERE p.simulation_id <> t.simulation_id "
                    f"OR t.{column} <> p.user_id * {factor}"
                )
            ).scalar_one()
            assert misplaced == 0
        assert schema_diff(engine) == []
    engine.dispose()

    command.downgrade(alembic_config(url), BEFORE_PORTFOLIOS)

    engine = create_engine(scratch_url, poolclass=NullPool)
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT to_regclass('portfolios')")).scalar()
            is None
        )
        assert _row_counts(connection) == counts
        for table, column, factor in VALUES_BY_OWNER:
            wrong_owner = connection.execute(
                text(
                    f"SELECT count(*) FROM {table} "  # noqa: S608
                    f"WHERE {column} <> user_id * {factor}"
                )
            ).scalar_one()
            assert wrong_owner == 0
    engine.dispose()
