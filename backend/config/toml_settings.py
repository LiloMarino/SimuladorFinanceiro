import tomllib
from pathlib import Path

import toml
from pydantic import BaseModel, field_validator

from backend.core.logger import setup_logger
from backend.features.tunnel.providers import AVAILABLE_PROVIDERS

logger = setup_logger(__package__ if __package__ else __name__)

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


class TunnelConfig(BaseModel):
    enabled: bool = False
    provider: str = "placeholder"
    port: int = 8000
    auto_start: bool = False

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Valida se o provider especificado está disponível."""

        if v not in AVAILABLE_PROVIDERS:
            available = ", ".join(AVAILABLE_PROVIDERS.keys())
            raise ValueError(
                f"Provider '{v}' não é válido. Providers disponíveis: {available}"
            )
        return v


class TomlSettings(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    simulation: SimulationConfig = SimulationConfig()
    realtime: RealtimeConfig = RealtimeConfig()
    host: HostConfig = HostConfig()
    tunnel: TunnelConfig = TunnelConfig()


def load_toml_settings() -> TomlSettings:
    if not CONFIG_PATH.exists():
        defaults = TomlSettings().model_dump()

        with CONFIG_PATH.open("w") as f:
            toml.dump(defaults, f)

        logger.info("config.toml criado com defaults")

        return TomlSettings()

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return TomlSettings(**data)
