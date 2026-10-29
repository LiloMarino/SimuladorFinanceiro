"""As migrations chegam exatamente no schema dos models, e o `migrate` guarda um
backup do banco existente antes de subir."""

from __future__ import annotations

import json
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
from backend.core.enum import VictoryCriterion
from backend.core.migration import (
    MigrationError,
    alembic_config,
    backups_to_drop,
    current_revision,
    drop_databases,
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


def test_versioned_database_is_backed_up_and_migrated(
    pg_url: str, engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Banco com dado no head antigo ganha um backup e sobe até o head novo."""
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
        assert len(_backups(pg_url)) == 1
    finally:
        drop_databases(make_url(pg_url), _backups(pg_url))


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


def test_only_the_latest_backups_are_kept() -> None:
    backups = [
        "db_bkp_20261003_101500",
        "db_bkp_20261001_090000",
        "db_bkp_20261009_120000",
        "db_bkp_20261005_080000",
    ]

    assert backups_to_drop(backups, keep=3) == ["db_bkp_20261001_090000"]
    assert backups_to_drop(backups[:2], keep=3) == []


SAVED_BY_2_3 = "f3a6c2d85b17"


def test_match_saved_by_2_3_opens_the_same_in_3_0(pg_url: str, engine: Engine) -> None:
    """A partida das colunas da 2.3 migra para o JSON e abre igual no DTO."""
    expected = simulation_settings().model_copy(
        update={
            "name": "Clássica",
            "end_date": date(2024, 12, 31),
            "starting_cash": Decimal("12345.67"),
            "victory_criterion": VictoryCriterion.NETWORTH,
            "price_impact_enabled": True,
        }
    )
    alembic = alembic_config(pg_url)
    command.upgrade(alembic, SAVED_BY_2_3)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO simulations (name, start_date, end_date, starting_cash, "
                "monthly_contribution, price_impact_enabled, price_impact_k, "
                "price_impact_decay_days, victory_criterion, game_type, goal_net_worth, "
                "monthly_salary, monthly_expense, unexpected_per_year, withdrawal_rate, "
                "inflation_adjusted, random_seed, player_grouping, team_naming, "
                "show_equivalent_rate, show_maturity_projection, "
                "created_at, last_simulated_at) VALUES ("
                "'Clássica', '2020-01-01', '2024-12-31', 12345.67, 0, true, 0.02, 20, "
                "'NETWORTH', 'CLASSIC', 100000, 8000, 5000, 3, 0.04, false, 7, "
                "'INDIVIDUAL', 'COLOR', true, true, now(), now())"
            )
        )

    command.upgrade(alembic, "head")

    assert current_revision(engine) == head_revision()
    with engine.connect() as connection:
        name, rules = connection.execute(
            text("SELECT name, rules FROM simulations")
        ).one()
    assert decode_settings(name, rules) == expected
    assert rules.keys() == encode_rules(expected).keys()


def test_rules_return_to_columns_on_downgrade(pg_url: str, engine: Engine) -> None:
    """Descer da 3.0 devolve as regras da partida às colunas, com os mesmos valores."""
    migrate(pg_url)
    settings = simulation_settings().model_copy(
        update={"starting_cash": Decimal("12345.67")}
    )
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO simulations (name, rules, random_seed, created_at, "
                "last_simulated_at) VALUES ('Partida', CAST(:rules AS jsonb), 7, now(), now())"
            ),
            {"rules": json.dumps(encode_rules(settings))},
        )

    command.downgrade(alembic_config(pg_url), SAVED_BY_2_3)

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT start_date, starting_cash, game_type::text, victory_criterion::text "
                "FROM simulations"
            )
        ).one()
    assert tuple(row) == (
        date(2020, 1, 1),
        Decimal("12345.670000"),
        "CLASSIC",
        "SCORE",
    )


def test_revision_from_before_2_3_is_refused_untouched(
    pg_url: str, engine: Engine
) -> None:
    """Banco numa revisão que a 3.0 não conhece é recusado com o caminho de volta pela 2.3."""
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE alembic_version (version_num text)"))
        connection.execute(text("INSERT INTO alembic_version VALUES ('9707da5dfa82')"))
        connection.execute(text("CREATE TABLE stock (ticker text)"))
        connection.execute(text("INSERT INTO stock VALUES ('PETR4.SA')"))

    with pytest.raises(
        MigrationError, match=r"anterior à 2\.3\.0\. Abra-o uma vez com a 2\.3\.0"
    ):
        migrate(pg_url)

    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
            == "9707da5dfa82"
        )
        assert (
            connection.execute(text("SELECT ticker FROM stock")).scalar() == "PETR4.SA"
        )
    assert _backups(pg_url) == []


BEFORE_NEWS = "f7b1d4c9e5a3"


def test_turned_off_notices_stay_off_in_the_notification_registry(
    pg_url: str, engine: Engine
) -> None:
    """As preferências de aviso de antes viram os avisos do registro."""
    alembic = alembic_config(pg_url)
    command.upgrade(alembic, BEFORE_NEWS)
    old = {
        "orders": {"executed": False, "partial": True},
        "players": {"join_exit": False},
    }
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (client_id, nickname, created_at, settings) "
                "VALUES (gen_random_uuid(), 'Ana', now(), CAST(:settings AS jsonb))"
            ),
            {"settings": json.dumps(old)},
        )
    command.upgrade(alembic, "head")

    with engine.connect() as connection:
        settings = connection.execute(text("SELECT settings FROM users")).scalar_one()
    assert settings["notifications"] == {
        "toasts": {
            "ORDER_EXECUTED": False,
            "ORDER_PARTIAL": True,
            "PLAYER_PRESENCE": False,
        }
    }


BEFORE_SUMMARIES = "a8c2e5d0f6b4"


def test_summaries_keep_their_rows_after_the_rename(
    pg_url: str, engine: Engine
) -> None:
    """Os resumos gravados na tabela da caixa de entrada seguem na tabela de resumos."""
    alembic = alembic_config(pg_url)
    command.upgrade(alembic, BEFORE_SUMMARIES)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (client_id, nickname, created_at) "
                "VALUES (gen_random_uuid(), 'Ana', now())"
            )
        )
        connection.execute(
            text(
                "INSERT INTO simulations (name, rules, random_seed, created_at, "
                "last_simulated_at) VALUES ('Partida', CAST('{}' AS jsonb), 7, now(), now())"
            )
        )
        connection.execute(
            text(
                "INSERT INTO inbox_entries (simulation_id, user_id, game_date, kind, "
                "content, created_at) SELECT s.id, u.id, '2020-02-01', 'MONTH_SUMMARY', "
                'CAST(\'{"kind": "MONTH_SUMMARY"}\' AS jsonb), now() '
                "FROM simulations s, users u"
            )
        )

    command.upgrade(alembic, "head")

    with engine.begin() as connection:
        row = connection.execute(
            text("SELECT game_date, kind::text, content FROM summaries")
        ).one()
        assert tuple(row) == (
            date(2020, 2, 1),
            "MONTH_SUMMARY",
            {"kind": "MONTH_SUMMARY"},
        )
        connection.execute(
            text(
                "INSERT INTO summaries (simulation_id, user_id, game_date, kind, "
                "content, created_at) SELECT simulation_id, user_id, '2020-03-01', "
                "'YEAR_REVIEW', content, now() FROM summaries"
            )
        )
        assert connection.execute(text("SELECT count(*) FROM summaries")).scalar() == 2
    assert schema_diff(engine) == []
    columns = {column["name"] for column in inspect(engine).get_columns("summaries")}
    assert "read" not in columns
