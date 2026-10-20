import logging
import tomllib

import toml
from pydantic import BaseModel, field_validator

from backend.config.paths import app_files_dir
from backend.features.tunnel.network_utils.network_types import NetworkType
from backend.features.tunnel.providers import AVAILABLE_PROVIDERS

logger = logging.getLogger(__name__)

CONFIG_PATH = app_files_dir() / "config.toml"


class SimulationConfig(BaseModel):
    start_date: str = "2000-01-01"
    end_date: str = "2026-01-01"
    starting_cash: float = 10000.00
    monthly_contribution: float = 0.0
    price_impact_enabled: bool = False
    price_impact_k: float = 0.02
    price_impact_decay_days: int = 20
    victory_criterion: str = "SCORE"
    # Meta padrão da corrida à meta, em múltiplos do saldo inicial
    goal_multiple: int = 10


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
    logs_path: str = "logs"


class DebugConfig(BaseModel):
    enabled: bool = False
    sql: bool = False


class TomlSettings(BaseModel):
    simulation: SimulationConfig = SimulationConfig()
    host: HostConfig = HostConfig()
    server: ServerConfig = ServerConfig()
    logging: LoggingConfig = LoggingConfig()
    debug: DebugConfig = DebugConfig()


def _load_toml_settings() -> TomlSettings:  # pyright: ignore[reportUnusedFunction]
    if not CONFIG_PATH.exists():
        defaults = TomlSettings().model_dump()

        with CONFIG_PATH.open("w") as f:
            toml.dump(defaults, f)

        logger.info("config.toml criado com defaults")

        return TomlSettings()

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return TomlSettings(**data)
