import logging
import tomllib
from pathlib import Path

import toml
from pydantic import BaseModel, field_validator

from backend.features.tunnel.network_utils.network_types import NetworkType
from backend.features.tunnel.providers import AVAILABLE_PROVIDERS

logger = logging.getLogger(__package__ if __package__ else __name__)

CONFIG_PATH = Path("config.toml")


class DatabaseConfig(BaseModel):
    echo_sql: bool = False


class SimulationConfig(BaseModel):
    start_date: str = "2000-01-01"
    end_date: str = "2026-01-01"
    starting_cash: float = 10000.00
    monthly_contribution: float = 0.0


class RealtimeConfig(BaseModel):
    use_sse: bool = False


class HostConfig(BaseModel):
    nickname: str = "host"


class ServerConfig(BaseModel):
    port: int = 8000
    provider: str = "lan"
    preferred_vpn: NetworkType | None = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v not in AVAILABLE_PROVIDERS:
            available = ", ".join(AVAILABLE_PROVIDERS.keys())
            raise ValueError(
                f"Provider '{v}' não é válido. Providers disponíveis: {available}"
            )
        return v


class LoggingConfig(BaseModel):
    logging_level: str = "INFO"
    logs_path: str = "logs"

    @field_validator("logging_level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        level = v.upper()
        if not hasattr(logging, level):
            raise ValueError(
                f"logging_level inválido: {v}. "
                "Use DEBUG, INFO, WARNING, ERROR ou CRITICAL."
            )
        return level


class TomlSettings(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    simulation: SimulationConfig = SimulationConfig()
    realtime: RealtimeConfig = RealtimeConfig()
    host: HostConfig = HostConfig()
    server: ServerConfig = ServerConfig()
    logging: LoggingConfig = LoggingConfig()


def _load_toml_settings() -> TomlSettings:
    if not CONFIG_PATH.exists():
        defaults = TomlSettings().model_dump()

        with CONFIG_PATH.open("w") as f:
            toml.dump(defaults, f)

        logger.info("config.toml criado com defaults")

        return TomlSettings()

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return TomlSettings(**data)
