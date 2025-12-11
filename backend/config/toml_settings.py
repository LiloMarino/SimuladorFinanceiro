import tomllib
from pathlib import Path

import toml
from pydantic import BaseModel

from backend.core.logger import setup_logger

logger = setup_logger(__package__ if __package__ else __name__)

CONFIG_PATH = Path("config.toml")


class SimulationConfig(BaseModel):
    starting_cash: int = 10000


class RealtimeConfig(BaseModel):
    use_sse: bool = False


class TomlSettings(BaseModel):
    simulation: SimulationConfig = SimulationConfig()
    realtime: RealtimeConfig = RealtimeConfig()


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
