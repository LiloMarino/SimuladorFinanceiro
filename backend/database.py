import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from backend.shared.models.models import Base
from backend.shared.utils.logger import setup_logger

DB_PATH = Path("data/simulador_financeiro.db")
load_dotenv()

logger = setup_logger(__name__)


def get_engine():
    mysql_url = os.getenv("MYSQL_DATABASE_URL")
    sqlite_url = os.getenv(
        "SQLITE_DATABASE_URL", "sqlite:///./data/simulador_financeiro.db"
    )

    if mysql_url:
        try:
            # Extrai info da URL
            url_obj = make_url(mysql_url)
            db_name = url_obj.database

            # Conecta sem schema
            url_no_db = URL.create(
                drivername=url_obj.drivername,
                username=url_obj.username,
                password=url_obj.password,
                host=url_obj.host,
                port=url_obj.port,
                database=None,
                query=url_obj.query,
            )
            tmp_engine = create_engine(url_no_db, echo=False, pool_pre_ping=True)

            # Cria schema se não existir
            with tmp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

            tmp_engine.dispose()

            # Agora conecta no schema correto
            engine = create_engine(mysql_url, echo=False, pool_pre_ping=True)

            # Cria tabelas
            Base.metadata.create_all(bind=engine)
            return engine

        except OperationalError as e:
            logger.error(f"Erro ao conectar ao MySQL: {str(e)}")
            logger.warning("MySQL indisponível, fallback para SQLite...")

    # Se não deu MySQL, usa SQLite
    engine = create_engine(sqlite_url, echo=False, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    return engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    return SessionLocal()
