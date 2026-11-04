import logging
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

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

    Cada consulta é planejada com os valores dela: as leituras pela versão da partida
    dependem de quantas linhas aquela versão tem, e o plano genérico que o Postgres
    adota para um statement preparado não enxerga isso.
    """
    engine = create_engine(
        resolve_database_url(),
        pool_pre_ping=True,
        connect_args={"options": "-c plan_cache_mode=force_custom_plan"},
    )
    logger.info("Conectado ao PostgreSQL.")
    return engine


@cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
