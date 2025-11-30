import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from backend.core.logger import setup_logger
from backend.core.models.models import Base

load_dotenv()
logger = setup_logger(__name__)


# -----------------------------------
# Criar DB no PostgreSQL se não existir
# -----------------------------------
def create_database_postgres(url_obj):
    db_name = url_obj.database

    admin_url = URL.create(
        drivername=url_obj.drivername,
        username=url_obj.username,
        password=url_obj.password,
        host=url_obj.host,
        port=url_obj.port,
        database="postgres",  # banco padrão de administração
    )

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db"), {"db": db_name}
        ).scalar()

        if not exists:
            logger.info(f"Criando database PostgreSQL: {db_name}")
            conn.execute(text(f"CREATE DATABASE {db_name}"))

    admin_engine.dispose()


# -----------------------------------
# Factory do Engine
# -----------------------------------
def get_engine():
    pg_url = os.getenv("POSTGRES_DATABASE_URL")
    sqlite_url = os.getenv(
        "SQLITE_DATABASE_URL", "sqlite:///./data/simulador_financeiro.db"
    )

    # ================================
    # PostgreSQL (prioritário)
    # ================================
    if pg_url:
        try:
            url_obj = make_url(pg_url)

            create_database_postgres(url_obj)

            engine = create_engine(pg_url, pool_pre_ping=True)
            Base.metadata.create_all(engine)

            logger.info("Conectado ao PostgreSQL.")
            return engine

        except Exception as e:
            logger.error(f"Erro ao conectar no PostgreSQL: {e}")

    # ================================
    # SQLite (fallback automático)
    # ================================
    engine = create_engine(sqlite_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    logger.warning("Conectado ao SQLite (fallback).")
    return engine


engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
