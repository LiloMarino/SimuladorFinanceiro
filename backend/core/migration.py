"""Leva o banco ao head das migrations antes de o app subir.

Banco com dado migra depois de um backup dele como estava.
"""

import logging
from datetime import datetime

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, Engine, Enum, create_engine, inspect, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.pool import NullPool

from backend.core.logger import TERMINAL
from backend.core.models.models import Base
from backend.core.utils import resource_path

logger = logging.getLogger(__name__)

BACKUPS_KEPT = 3
VERSION_TABLE = "alembic_version"
RELEASES_URL = "https://github.com/LiloMarino/SimuladorFinanceiro/releases"


class MigrationError(Exception):
    """Migration recusada: o banco fica como estava."""


def alembic_config(database_url: str = "") -> Config:
    config = Config()
    config.set_main_option("script_location", str(resource_path("backend/migrations")))
    # O ConfigParser interpola `%`; dobrar é o escape
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def head_revision() -> str | None:
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def current_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def known_revisions() -> set[str]:
    return {
        script.revision
        for script in ScriptDirectory.from_config(alembic_config()).walk_revisions()
    }


def schema_diff(engine: Engine) -> list:
    """Diferenças entre o schema do banco e o que os models declaram."""
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        return compare_metadata(context, Base.metadata) + _enum_diff(connection)


def _enum_diff(connection: Connection) -> list:
    """Os tipos enum cujos valores no banco diferem dos declarados nos models.

    O `compare_metadata` compara só o nome do tipo; os valores ficam por conta daqui.
    """
    rows = connection.execute(
        text(
            "SELECT t.typname, e.enumlabel FROM pg_type t "
            "JOIN pg_enum e ON e.enumtypid = t.oid"
        )
    )
    stored: dict[str, set[str]] = {}
    for name, label in rows:
        stored.setdefault(name, set()).add(label)
    declared = {
        column.type.name: set(column.type.enums)
        for table in Base.metadata.tables.values()
        for column in table.columns
        if isinstance(column.type, Enum) and column.type.name
    }
    return [
        ("enum_values", name, sorted(stored.get(name, set()) ^ values))
        for name, values in sorted(declared.items())
        if stored.get(name, set()) != values
    ]


def backups_to_drop(backups: list[str], keep: int = BACKUPS_KEPT) -> list[str]:
    """Os backups além dos `keep` mais recentes.

    O sufixo `AAAAMMDD_HHMMSS` faz a ordem alfabética ser a cronológica.
    """
    return sorted(backups)[:-keep] if len(backups) > keep else []


def _admin_engine(url: URL) -> Engine:
    return create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )


def database_name(url: URL) -> str:
    if not url.database:
        raise MigrationError("O POSTGRES_DATABASE_URL não diz o nome do banco.")
    return url.database


def ensure_database(url: URL) -> None:
    name = database_name(url)
    admin = _admin_engine(url)
    try:
        with admin.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": name},
            ).scalar()
            if not exists:
                logger.info(
                    "Criando o banco de dados PostgreSQL: %s", name, extra=TERMINAL
                )
                quote = admin.dialect.identifier_preparer.quote
                connection.execute(text(f"CREATE DATABASE {quote(name)}"))
    finally:
        admin.dispose()


def copy_database(url: URL, target: str) -> None:
    source = database_name(url)
    admin = _admin_engine(url)
    quote = admin.dialect.identifier_preparer.quote
    try:
        with admin.connect() as connection:
            connection.execute(text(f"DROP DATABASE IF EXISTS {quote(target)}"))
            connection.execute(
                text(f"CREATE DATABASE {quote(target)} TEMPLATE {quote(source)}")
            )
    except DBAPIError as error:
        raise MigrationError(
            f"Não foi possível copiar o banco {source} para {target}. "
            "A cópia exige o banco sem outras conexões: feche pgAdmin, DBeaver "
            f"ou outra instância do simulador e tente de novo. ({error.orig})"
        ) from error
    finally:
        admin.dispose()


def drop_databases(url: URL, names: list[str]) -> None:
    admin = _admin_engine(url)
    quote = admin.dialect.identifier_preparer.quote
    try:
        with admin.connect() as connection:
            for name in names:
                connection.execute(text(f"DROP DATABASE IF EXISTS {quote(name)}"))
    finally:
        admin.dispose()


def _list_backups(url: URL) -> list[str]:
    admin = _admin_engine(url)
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


def _backup(url: URL) -> None:
    name = f"{url.database}_bkp_{datetime.now():%Y%m%d_%H%M%S}"  # noqa: DTZ005
    copy_database(url, name)
    logger.info("Backup do banco antes da migration: %s", name)
    drop_databases(url, backups_to_drop(_list_backups(url)))


def migrate(database_url: str) -> None:
    """Leva o banco ao head, criando-o se não existir."""
    if not database_url:
        raise MigrationError(
            "POSTGRES_DATABASE_URL não configurada. "
            "Configure a variável de ambiente no arquivo .env"
        )
    url = make_url(database_url)
    ensure_database(url)
    head = head_revision()

    engine = create_engine(url, poolclass=NullPool)
    try:
        revision = current_revision(engine)
        tables = set(inspect(engine).get_table_names()) - {VERSION_TABLE}
        diff = schema_diff(engine) if revision is None and tables else []
    finally:
        engine.dispose()

    config = alembic_config(database_url)
    if revision == head:
        return
    # A linha de revisões começa na 2.3.0: banco gravado numa revisão fora dela
    # só atualiza passando antes pela 2.3.0
    if revision is not None and revision not in known_revisions():
        raise MigrationError(
            f"O banco {url.database} é de uma versão anterior à 2.3.0. Abra-o uma "
            "vez com a 2.3.0, que atualiza as partidas salvas, e depois volte para "
            f"esta versão. A 2.3.0 está em {RELEASES_URL}."
        )
    if revision is None and not tables:
        command.upgrade(config, "head")
        logger.info("Banco criado na revisão %s", head, extra=TERMINAL)
        return
    if revision is None:
        # Banco do `create_all`, anterior às migrations: só o que bate com os
        # models entra na linha de revisões
        if diff:
            raise MigrationError(
                f"O banco {url.database} é anterior às migrations e o schema dele "
                "não bate com o desta versão. Renomeie ou apague esse banco, ou "
                "aponte o POSTGRES_DATABASE_URL para um banco novo."
            )
        command.stamp(config, "head")
        logger.info("Banco existente marcado na revisão %s", head)
        return

    _backup(url)
    command.upgrade(config, "head")
    logger.info("Banco migrado de %s até %s", revision, head, extra=TERMINAL)
