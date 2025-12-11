from backend.config.env_settings import load_env_settings
from backend.config.toml_settings import load_toml_settings


class Settings:
    def __init__(self):
        self.env = load_env_settings()
        self.toml = load_toml_settings()


# Instância única p/ usar no app inteiro
settings = Settings()
