from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import config
from backend.core import repository
from backend.core.dependencies import get_client_id, verify_host
from backend.core.enum import GameType
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.settings_manager import SettingsManager
from backend.routes import simulation as simulation_routes
from backend.routes.simulation import restore_simulation_settings, simulation_router
from tests.fakes import client, simulation_settings


@pytest.fixture
def pending_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(SettingsManager, "_settings", None)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(repository.simulation, "generate_default_name", lambda: "Nova")


@pytest.mark.usefixtures("database")
def test_repository_keeps_one_last_settings_row() -> None:
    repository.last_simulation_settings.clear()
    assert repository.last_simulation_settings.get() is None

    repository.last_simulation_settings.save({"start_date": "2012-01-01"})
    repository.last_simulation_settings.save({"start_date": "2013-01-01"})

    assert repository.last_simulation_settings.get() == {"start_date": "2013-01-01"}

    repository.last_simulation_settings.clear()
    assert repository.last_simulation_settings.get() is None


@pytest.mark.usefixtures("database")
def test_manager_remembers_rules_but_generates_a_new_name(
    pending_settings: None,
) -> None:
    rules = simulation_settings().model_copy(
        update={
            "name": "Não deve sobreviver",
            "start_date": date(2012, 1, 2),
            "game_type": GameType.GOAL_RACE,
            "goal_net_worth": Decimal(250000),
        }
    )

    SettingsManager.update(rules)
    stored = repository.last_simulation_settings.get()
    assert stored is not None
    assert "name" not in stored

    SettingsManager._settings = None
    restored = SettingsManager.get()

    assert restored.name == "Nova"
    assert restored.start_date == date(2012, 1, 2)
    assert restored.game_type is GameType.GOAL_RACE
    assert restored.goal_net_worth == Decimal(250000)


@pytest.mark.usefixtures("database")
def test_manager_falls_back_for_missing_or_invalid_persisted_fields(
    pending_settings: None,
) -> None:
    saved = simulation_settings().model_dump(mode="json", exclude={"name"})
    saved.pop("show_equivalent_rate")
    repository.last_simulation_settings.save(saved)

    restored = SettingsManager.get()
    assert restored.show_equivalent_rate is True

    repository.last_simulation_settings.save({"start_date": "não é uma data"})
    SettingsManager._settings = None
    assert SettingsManager.get().start_date == date.fromisoformat(
        config.toml.simulation.start_date
    )

    repository.last_simulation_settings.save({"starting_cash": "-1"})
    SettingsManager._settings = None
    assert SettingsManager.get().starting_cash == Decimal(
        str(config.toml.simulation.starting_cash)
    )


@pytest.mark.usefixtures("database")
def test_restore_settings_deletes_the_saved_rules_and_notifies_the_room(
    pending_settings: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    SettingsManager.update(
        simulation_settings().model_copy(update={"start_date": date(2012, 1, 2)})
    )
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        simulation_routes,
        "notify",
        lambda event, payload: events.append((event, payload)),
    )

    restored = restore_simulation_settings(None)

    assert restored.name == "Nova"
    assert restored.start_date == date.fromisoformat(config.toml.simulation.start_date)
    assert repository.last_simulation_settings.get() is None
    assert events == [
        ("simulation_settings_update", restored.to_json()),
        ("preset_applied_update", {"applied": None}),
    ]


def test_restore_settings_is_refused_while_a_saved_match_is_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 7)

    with pytest.raises(ConflictError):
        restore_simulation_settings(None)


def test_restore_settings_route_requires_a_host() -> None:
    app = FastAPI()
    app.include_router(simulation_router)
    response = TestClient(app).delete("/api/simulation/settings")

    assert response.status_code == 401


@pytest.mark.usefixtures("database")
def test_restore_settings_route_returns_defaults_for_the_host(
    pending_settings: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = FastAPI()
    app.include_router(simulation_router)
    app.dependency_overrides[get_client_id] = lambda: client("host")
    app.dependency_overrides[verify_host] = lambda: None
    SettingsManager.update(
        simulation_settings().model_copy(update={"start_date": date(2012, 1, 2)})
    )
    monkeypatch.setattr(simulation_routes, "notify", lambda *_args, **_kwargs: None)

    response = TestClient(app).delete("/api/simulation/settings")

    assert response.status_code == 200
    assert response.json()["start_date"] == config.toml.simulation.start_date
