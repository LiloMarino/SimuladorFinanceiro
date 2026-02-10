from typing import Final

from backend.config.env_settings import EnvSettings, _load_env_settings
from backend.config.toml_settings import TomlSettings, _load_toml_settings

env: Final[EnvSettings] = _load_env_settings()
toml: Final[TomlSettings] = _load_toml_settings()
