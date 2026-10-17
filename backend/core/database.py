import logging
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend import config
from backend.core.embedded_postgres import resolve_database_url

logger = logging.getLogger(__name__)


# -----------------------------------
# Factory do Engine
# -----------------------------------
@cache
def get_engine() -> Engine:
    """
    A engine conecta no primeiro uso: importar o backend não toca no banco. No app,
    o primeiro uso é o lifespan do main.py, então as threads de request e do loop
    da simulação já a encontram criada.
    """
    engine = create_engine(
        resolve_database_url(),
        pool_pre_ping=True,
        echo=config.toml.database.echo_sql,
    )
    logger.info("Conectado ao PostgreSQL.")
    return engine


@cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
