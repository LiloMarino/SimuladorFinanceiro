import tomllib
from pathlib import Path

import toml
from pydantic import BaseModel

from backend.core.logger import setup_logger

logger = setup_logger(__package__ if __package__ else __name__)

CONFIG_PATH = Path("config.toml")
DEFAULT_TOML_CONTENT = {
    "simulation": {
        "starting_cash": 10000,
    },
    "realtime": {
        "use_sse": False,
    },
}


class SimulationConfig(BaseModel):
    starting_cash: int


class RealtimeConfig(BaseModel):
    use_sse: bool = False


class TomlSettings(BaseModel):
    simulation: SimulationConfig
    realtime: RealtimeConfig


def load_toml_settings() -> TomlSettings:
    if not CONFIG_PATH.exists():
        with CONFIG_PATH.open("w") as f:
            toml.dump(DEFAULT_TOML_CONTENT, f)
        logger.info("config.toml created with defaults")

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return TomlSettings(**data)
