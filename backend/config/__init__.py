from typing import Final

from backend.config.env_settings import EnvSettings, load_env_settings
from backend.config.toml_settings import TomlSettings, load_toml_settings

env: Final[EnvSettings] = load_env_settings()
toml: Final[TomlSettings] = load_toml_settings()
