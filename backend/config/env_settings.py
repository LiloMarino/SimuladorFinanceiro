from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.logger import setup_logger

logger = setup_logger(__package__ if __package__ else __name__)

ENV_PATH = Path(".env")
DEFAULT_ENV_CONTENT = """
# ============================
# 🔧 ENVIRONMENT CONFIGURATION
# ============================

# PostgreSQL example:
POSTGRES_DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@localhost:5432/simulador_financeiro
"""


class EnvSettings(BaseSettings):
    postgres_url: str = Field(default="", alias="POSTGRES_DATABASE_URL")
    sqlite_url: str = Field(
        default="sqlite:///./data/simulador_financeiro.db", alias="SQLITE_DATABASE_URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# Função de carregamento completo
def load_env_settings() -> EnvSettings:
    if not ENV_PATH.exists():
        ENV_PATH.write_text(DEFAULT_ENV_CONTENT, encoding="utf-8")
        logger.info(".env created with defaults")

    return EnvSettings()
