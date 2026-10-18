"""O modo debug vem desligado e só o liga quem pede no boot."""

import pytest

from backend.config.toml_settings import TomlSettings


def test_debug_is_off_by_default() -> None:
    assert TomlSettings().debug.enabled is False


def test_config_without_debug_section_loads() -> None:
    # config.toml de antes do modo debug não tem a seção [debug]
    settings = TomlSettings.model_validate({"logging": {"logging_level": "WARNING"}})

    assert settings.debug.enabled is False


def test_debug_section_turns_it_on() -> None:
    assert (
        TomlSettings.model_validate({"debug": {"enabled": True}}).debug.enabled is True
    )


@pytest.mark.parametrize("configured", ["INFO", "WARNING", "ERROR"])
def test_debug_forces_debug_level(configured: str) -> None:
    settings = TomlSettings.model_validate(
        {"logging": {"logging_level": configured}, "debug": {"enabled": True}}
    )

    assert settings.effective_logging_level() == "DEBUG"


@pytest.mark.parametrize("configured", ["INFO", "WARNING", "ERROR"])
def test_without_debug_the_configured_level_wins(configured: str) -> None:
    settings = TomlSettings.model_validate({"logging": {"logging_level": configured}})

    assert settings.effective_logging_level() == configured
