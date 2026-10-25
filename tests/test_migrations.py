"""As migrations chegam exatamente no schema dos models, e o `migrate` só entra
num banco existente quando nada se perde."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from backend.core import migration
from backend.core.enum import GameType
from backend.core.migration import (
    MigrationError,
    TableFingerprint,
    alembic_config,
    assert_no_data_loss,
    backups_to_drop,
    current_revision,
    drop_databases,
    fingerprint,
    head_revision,
    migrate,
    schema_diff,
)
from backend.core.models.models import Base
from backend.core.repository.simulation import decode_settings, encode_rules
from tests.fakes import simulation_settings


def test_schema_matches_models(pg_url: str, engine: Engine) -> None:
    """Depois do upgrade até o head, o `compare_metadata` não acha diferença."""
    migrate(pg_url)

    assert schema_diff(engine) == []
    assert current_revision(engine) == head_revision()


def test_downgrade_then_upgrade_again(pg_url: str, engine: Engine) -> None:
    """Toda migration desce até a base e sobe de volta até o head."""
    migrate(pg_url)
    alembic = alembic_config(pg_url)

    command.downgrade(alembic, "base")
    assert current_revision(engine) is None

    command.upgrade(alembic, "head")
    assert current_revision(engine) == head_revision()


def test_versioned_database_migrates_through_the_dry_run(
    pg_url: str, engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Banco com dado no head antigo passa pelo ensaio e pelo backup até o head novo."""
    migrate(pg_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO stock (ticker, name, asset_class) VALUES ('T', 'T', 'STOCK')"
            )
        )
    _add_newer_revision(tmp_path, monkeypatch)

    try:
        migrate(pg_url)

        assert current_revision(engine) == NEWER_REVISION
        with engine.connect() as connection:
            assert connection.execute(text("SELECT ticker FROM stock")).scalar() == "T"
    finally:
        drop_databases(make_url(pg_url), _backups(pg_url))


BEFORE_SUFFIX_STRIP = "9707da5dfa82"


def _tickers_before_strip(pg_url: str, engine: Engine, tickers: list[str]) -> None:
    """Banco na revisão anterior à que tira o `.SA`, com estes códigos em `stock`."""
    command.upgrade(alembic_config(pg_url), BEFORE_SUFFIX_STRIP)
    with engine.begin() as connection:
        for position, ticker in enumerate(tickers):
            connection.execute(
                text(
                    "INSERT INTO stock (ticker, name, asset_class) "  # noqa: S608
                    f"VALUES ('{ticker}', 'Nome {position}', 'STOCK')"
                )
            )
        connection.execute(
            text("INSERT INTO ticker_profile (ticker) VALUES ('VALE3.SA')")
        )


def test_suffix_is_stripped_from_stored_tickers(pg_url: str, engine: Engine) -> None:
    """Os códigos importados com o `.SA` passam a valer sem ele; os outros ficam."""
    _tickers_before_strip(pg_url, engine, ["PETR4.SA", "ITSA4", "BTC-USD"])

    command.upgrade(alembic_config(pg_url), "head")

    with engine.connect() as connection:
        stocks = connection.execute(text("SELECT ticker FROM stock")).scalars().all()
        profiles = connection.execute(
            text("SELECT ticker FROM ticker_profile")
        ).scalars()
        assert sorted(stocks) == ["BTC-USD", "ITSA4", "PETR4"]
        assert list(profiles) == ["VALE3"]


def test_suffix_strip_stops_when_the_bare_code_exists(
    pg_url: str, engine: Engine
) -> None:
    """Com `PETR4` e `PETR4.SA` na base, a migration para em vez de mesclar."""
    _tickers_before_strip(pg_url, engine, ["PETR4.SA", "PETR4"])

    with pytest.raises(RuntimeError, match=r"PETR4.SA"):
        command.upgrade(alembic_config(pg_url), "head")


NEWER_REVISION = "test_newer"


def _add_newer_revision(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Acrescenta ao head real uma revisão só do teste, que dá ao banco uma versão a subir."""
    (tmp_path / "newer.py").write_text(
        f'''
import sqlalchemy as sa
from alembic import op

revision = "{NEWER_REVISION}"
down_revision = "{head_revision()}"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("stock", sa.Column("test_note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("stock", "test_note")
''',
        encoding="utf-8",
    )

    def config_with_newer_revision(database_url: str = "") -> Config:
        config = alembic_config(database_url)
        versions = Path(config.get_main_option("script_location") or "") / "versions"
        config.set_main_option("path_separator", "os")
        config.set_main_option("version_locations", f"{versions}{os.pathsep}{tmp_path}")
        return config

    monkeypatch.setattr(migration, "alembic_config", config_with_newer_revision)


def _backups(pg_url: str) -> list[str]:
    url = make_url(pg_url)
    admin = create_engine(url.set(database="postgres"), poolclass=NullPool)
    try:
        with admin.connect() as connection:
            return list(
                connection.execute(
                    text(
                        "SELECT datname FROM pg_database WHERE starts_with(datname, :p)"
                    ),
                    {"p": f"{url.database}_bkp_"},
                ).scalars()
            )
    finally:
        admin.dispose()


def test_unversioned_database_matching_models_is_stamped(
    pg_url: str, engine: Engine
) -> None:
    """Banco do `create_all` igual aos models entra na linha de revisões no head."""
    Base.metadata.create_all(engine)

    migrate(pg_url)

    assert current_revision(engine) == head_revision()


def test_unversioned_database_with_old_schema_is_refused(
    pg_url: str, engine: Engine
) -> None:
    """Banco do `create_all` com schema antigo é recusado e fica como estava."""
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE simulations DROP COLUMN random_seed"))

    with pytest.raises(MigrationError, match="anterior às migrations"):
        migrate(pg_url)

    assert current_revision(engine) is None
    columns = {column["name"] for column in inspect(engine).get_columns("simulations")}
    assert "random_seed" not in columns


def test_data_loss_is_refused() -> None:
    before = {
        "stock": TableFingerprint(rows=3, filled_cells=9),
        "users": TableFingerprint(rows=1, filled_cells=5),
    }

    assert_no_data_loss(before, dict(before))
    with pytest.raises(MigrationError, match="stock caiu de 3 para 2 linhas"):
        assert_no_data_loss(
            before, {**before, "stock": TableFingerprint(rows=2, filled_cells=6)}
        )
    with pytest.raises(MigrationError, match="células preenchidas"):
        assert_no_data_loss(
            before, {**before, "users": TableFingerprint(rows=1, filled_cells=4)}
        )
    with pytest.raises(MigrationError, match="a tabela users sumiu com 1 linhas"):
        assert_no_data_loss(before, {"stock": before["stock"]})


def test_dropping_an_empty_table_loses_nothing() -> None:
    """Tabela vazia que some não é perda de dado."""
    before = {
        "stock": TableFingerprint(rows=3, filled_cells=9),
        "unused": TableFingerprint(rows=0, filled_cells=0),
    }

    assert_no_data_loss(before, {"stock": before["stock"]})


def test_only_the_latest_backups_are_kept() -> None:
    backups = [
        "db_bkp_20261003_101500",
        "db_bkp_20261001_090000",
        "db_bkp_20261009_120000",
        "db_bkp_20261005_080000",
    ]

    assert backups_to_drop(backups, keep=3) == ["db_bkp_20261001_090000"]
    assert backups_to_drop(backups[:2], keep=3) == []


def test_fingerprint_counts_the_values_of_a_json_object(
    pg_url: str, engine: Engine
) -> None:
    """Num JSONB, cada valor não nulo do primeiro nível é uma célula."""
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE sample (id int, data jsonb)"))
        connection.execute(
            text(
                "INSERT INTO sample VALUES "
                """(1, '{"a": 1, "b": null, "c": "x"}'), """  # objeto: a e c
                "(2, '[1, 2]'), "  # não é objeto: 1
                "(3, 'null'), "  # nulo do JSON: 0
                "(4, NULL), "  # nulo do SQL: 0
                "(5, '5')"  # escalar: 1
            )
        )

    assert fingerprint(engine)["sample"] == TableFingerprint(
        rows=5, filled_cells=5 + 2 + 1 + 0 + 0 + 1
    )


def test_merging_columns_into_json_keeps_the_total(pg_url: str, engine: Engine) -> None:
    """Juntar colunas num JSON preserva o total; tirar uma chave do JSON o reduz."""
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE sample (a int, b text, c text)"))
        connection.execute(
            text("INSERT INTO sample VALUES (1, 'x', NULL), (2, NULL, NULL)")
        )
    before = fingerprint(engine)

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE sample ADD COLUMN data jsonb"))
        connection.execute(
            text("UPDATE sample SET data = jsonb_build_object('a', a, 'b', b, 'c', c)")
        )
        connection.execute(
            text("ALTER TABLE sample DROP COLUMN a, DROP COLUMN b, DROP COLUMN c")
        )
    assert_no_data_loss(before, fingerprint(engine))

    with engine.begin() as connection:
        connection.execute(text("UPDATE sample SET data = data - 'a'"))
    with pytest.raises(MigrationError, match="células preenchidas"):
        assert_no_data_loss(before, fingerprint(engine))


BEFORE_RULES_IN_JSON = "5836e0819ac7"


def test_saved_match_keeps_its_rules_through_the_json_migration(
    pg_url: str, engine: Engine
) -> None:
    """A partida das colunas migra para o JSON sem perder célula, abre igual no DTO e volta."""
    expected = simulation_settings().model_copy(
        update={
            "name": "Política",
            "end_date": date(2026, 12, 31),
            "game_type": GameType.POLITICAL,
            "government_enabled": True,
            "first_election": date(2022, 10, 2),
            "starting_cash": Decimal("12345.67"),
        }
    )
    alembic = alembic_config(pg_url)
    command.upgrade(alembic, BEFORE_RULES_IN_JSON)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO simulations (name, start_date, end_date, starting_cash, "
                "monthly_contribution, price_impact_enabled, price_impact_k, "
                "price_impact_decay_days, victory_criterion, game_type, goal_net_worth, "
                "monthly_salary, monthly_expense, unexpected_per_year, withdrawal_rate, "
                "inflation_adjusted, random_seed, player_grouping, team_naming, "
                "show_equivalent_rate, show_maturity_projection, show_chart_hints, "
                "government_enabled, first_election, computer_difficulty, "
                "created_at, last_simulated_at) VALUES ("
                "'Política', '2020-01-01', '2026-12-31', 12345.67, 0, false, 0.02, 20, "
                "'SCORE', 'POLITICAL', 100000, 8000, 5000, 3, 0.04, false, 7, "
                "'INDIVIDUAL', 'COLOR', true, true, true, true, '2022-10-02', 'NORMAL', "
                "now(), now())"
            )
        )
    before = fingerprint(engine)

    command.upgrade(alembic, "head")

    assert_no_data_loss(before, fingerprint(engine))
    with engine.connect() as connection:
        name, rules = connection.execute(
            text("SELECT name, rules FROM simulations")
        ).one()
    assert decode_settings(name, rules) == expected
    assert rules.keys() == encode_rules(expected).keys()

    command.downgrade(alembic, BEFORE_RULES_IN_JSON)

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT start_date, starting_cash, game_type::text, first_election, "
                "government_enabled FROM simulations"
            )
        ).one()
    assert tuple(row) == (
        date(2020, 1, 1),
        Decimal("12345.670000"),
        "POLITICAL",
        date(2022, 10, 2),
        True,
    )
