"""O modo debug vem desligado e só o liga quem pede no boot."""

from backend.config.toml_settings import TomlSettings


def test_debug_is_off_by_default() -> None:
    assert TomlSettings().debug.enabled is False


def test_config_without_debug_section_loads() -> None:
    # config.toml de antes do modo debug não tem a seção [debug]
    settings = TomlSettings.model_validate({"logging": {"logs_path": "logs"}})

    assert settings.debug.enabled is False


def test_debug_section_turns_it_on() -> None:
    assert (
        TomlSettings.model_validate({"debug": {"enabled": True}}).debug.enabled is True
    )


def test_sql_logging_is_off_by_default() -> None:
    assert TomlSettings().debug.sql is False


def test_sql_option_turns_it_on() -> None:
    settings = TomlSettings.model_validate({"debug": {"enabled": True, "sql": True}})

    assert settings.debug.sql is True


def test_removed_keys_in_an_old_config_are_ignored() -> None:
    settings = TomlSettings.model_validate(
        {
            "database": {"echo_sql": True},
            "logging": {"logging_level": "WARNING", "logs_path": "meus_logs"},
            "server": {"show_firewall_hint": False},
        }
    )

    assert settings.logging.logs_path == "meus_logs"
