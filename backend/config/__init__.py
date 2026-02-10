from backend.config.env_settings import load_env_settings
from backend.config.toml_settings import load_toml_settings
from backend.core.logger import setup_logging

env = load_env_settings()
toml = load_toml_settings()

setup_logging(
    level=toml.logging.logging_level,
    logs_path=toml.logging.logs_path,
)
