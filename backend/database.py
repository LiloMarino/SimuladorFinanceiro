import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

# Prioridade: MySQL > SQLite
mysql_url = os.getenv("MYSQL_DATABASE_URL")
sqlite_url = os.getenv(
    "SQLITE_DATABASE_URL", "sqlite:///./data/simulador_financeiro.db"
)

DATABASE_URL = mysql_url or sqlite_url

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    return SessionLocal()
