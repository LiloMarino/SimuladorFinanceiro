import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__package__ if __package__ else __name__)
ENV_PATH = Path(".env")


class EnvSettings(BaseSettings):
    postgres_url: str = Field(
        default="",
        alias="POSTGRES_DATABASE_URL",
        description="PostgreSQL URL ex: postgresql+psycopg://postgres:<PASSWORD>@localhost:5432/simulador_financeiro",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


def _generate_env_default_content(model: EnvSettings) -> str:
    """
    Gera automaticamente o conteúdo do .env baseado nos alias e defaults.
    """
    lines = [
        "# ===========================",
        "# 🔧 AUTO-GENERATED ENV FILE",
        "# ===========================",
        "",
    ]

    for field_name, field in EnvSettings.model_fields.items():
        alias = field.alias
        default = getattr(model, field_name)

        comment = f"# {field.description}" if field.description else ""
        default_value = default if default is not None else ""

        lines.append(f"{comment}")
        lines.append(f"{alias}={default_value}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _load_env_settings() -> EnvSettings:  # pyright: ignore[reportUnusedFunction]
    example = EnvSettings()

    if not ENV_PATH.exists():
        content = _generate_env_default_content(example)
        ENV_PATH.write_text(content, encoding="utf-8")
        logger.info(".env criado automaticamente com defaults")

    return EnvSettings()
