"""As migrations chegam exatamente no schema dos models, e o `migrate` só entra
num banco existente quando nada se perde."""

from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from backend.core.migration import (
    MigrationError,
    TableFingerprint,
    alembic_config,
    assert_no_data_loss,
    backups_to_drop,
    current_revision,
    drop_databases,
    head_revision,
    migrate,
    schema_diff,
)
from backend.core.models.models import Base


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
    pg_url: str, engine: Engine
) -> None:
    """Banco com dado uma revisão atrás passa pelo ensaio e pelo backup até o head."""
    migrate(pg_url)
    command.downgrade(alembic_config(pg_url), "-1")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO stock (ticker, name, asset_class) VALUES ('T', 'T', 'STOCK')"
            )
        )

    try:
        migrate(pg_url)

        assert current_revision(engine) == head_revision()
        with engine.connect() as connection:
            assert connection.execute(text("SELECT ticker FROM stock")).scalar() == "T"
    finally:
        drop_databases(make_url(pg_url), _backups(pg_url))


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
        connection.execute(text("ALTER TABLE simulations DROP COLUMN price_impact_k"))

    with pytest.raises(MigrationError, match="anterior às migrations"):
        migrate(pg_url)

    assert current_revision(engine) is None
    columns = {column["name"] for column in inspect(engine).get_columns("simulations")}
    assert "price_impact_k" not in columns


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
