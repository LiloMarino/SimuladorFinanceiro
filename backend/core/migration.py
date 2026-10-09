"""Leva o banco ao head das migrations antes de o app subir.

Banco com dado só migra depois de um ensaio numa cópia, em que nenhuma tabela
pode perder linha nem célula preenchida, e de um backup do banco como estava.
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.pool import NullPool

from backend.core.models.models import Base
from backend.core.utils import resource_path

logger = logging.getLogger(__name__)

BACKUPS_KEPT = 3
VERSION_TABLE = "alembic_version"


class MigrationError(Exception):
    """Migration recusada: o banco fica como estava."""


@dataclass(frozen=True, slots=True)
class TableFingerprint:
    rows: int
    filled_cells: int


type Fingerprint = dict[str, TableFingerprint]


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


def schema_diff(engine: Engine) -> list:
    """Diferenças entre o schema do banco e o que os models declaram."""
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        return compare_metadata(context, Base.metadata)


def fingerprint(engine: Engine) -> Fingerprint:
    """Linhas e células preenchidas por tabela.

    Rename de coluna preserva o total de células; coluna removida ou recriada
    vazia o reduz.
    """
    inspector = inspect(engine)
    quote = engine.dialect.identifier_preparer.quote
    result: Fingerprint = {}
    with engine.connect() as connection:
        for table in inspector.get_table_names():
            if table == VERSION_TABLE:
                continue
            columns = [column["name"] for column in inspector.get_columns(table)]
            filled = " + ".join(f"COUNT({quote(column)})" for column in columns)
            rows, filled_cells = connection.execute(
                text(f"SELECT COUNT(*), {filled} FROM {quote(table)}")
            ).one()
            result[table] = TableFingerprint(rows=rows, filled_cells=filled_cells)
    return result


def assert_no_data_loss(before: Fingerprint, after: Fingerprint) -> None:
    problems: list[str] = []
    for table, old in before.items():
        new = after.get(table)
        if new is None:
            problems.append(f"a tabela {table} sumiu")
        elif new.rows < old.rows:
            problems.append(f"{table} caiu de {old.rows} para {new.rows} linhas")
        elif new.filled_cells < old.filled_cells:
            problems.append(
                f"{table} caiu de {old.filled_cells} para {new.filled_cells} "
                "células preenchidas (coluna removida ou recriada vazia)"
            )
    if problems:
        raise MigrationError("A migration perderia dado: " + "; ".join(problems))


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
                logger.info(f"Criando database PostgreSQL: {name}")
                quote = admin.dialect.identifier_preparer.quote
                connection.execute(text(f"CREATE DATABASE {quote(name)}"))
    finally:
        admin.dispose()


def _copy_database(url: URL, target: str) -> None:
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


def _dry_run(url: URL) -> None:
    """Aplica as migrations numa cópia e só retorna se nenhum dado se perdeu."""
    copy_name = f"{url.database}_dryrun"
    _copy_database(url, copy_name)
    copy_url = url.set(database=copy_name)
    try:
        engine = create_engine(copy_url, poolclass=NullPool)
        try:
            before = fingerprint(engine)
            command.upgrade(
                alembic_config(copy_url.render_as_string(hide_password=False)), "head"
            )
            assert_no_data_loss(before, fingerprint(engine))
        finally:
            engine.dispose()
    finally:
        drop_databases(url, [copy_name])


def _backup(url: URL) -> None:
    name = f"{url.database}_bkp_{datetime.now():%Y%m%d_%H%M%S}"
    _copy_database(url, name)
    logger.info(f"Backup do banco antes da migration: {name}")
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
    if revision is None and not tables:
        command.upgrade(config, "head")
        logger.info(f"Banco criado no head {head}")
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
        logger.info(f"Banco existente marcado no head {head}")
        return

    _dry_run(url)
    _backup(url)
    command.upgrade(config, "head")
    logger.info(f"Banco migrado de {revision} até {head}")
