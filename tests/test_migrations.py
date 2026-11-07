"""As migrations chegam exatamente no schema dos models, o `migrate` guarda só os
backups mais recentes e recomeça o banco que a linha de revisões não cobre."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

from backend.core.migration import (
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
