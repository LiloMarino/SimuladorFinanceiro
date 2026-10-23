from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dependencies import get_client_id, verify_host
from backend.core.enum import GameType, PlayerGrouping, PresetRuleGroup
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.routes import simulation as simulation_routes
from backend.routes.presets import presets_router
from tests.fakes import client, simulation_settings

pytestmark = pytest.mark.usefixtures("database")


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Rotas de preset com o host liberado e a sala sem partida salva."""
    monkeypatch.setattr(SettingsManager, "_settings", None)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SettingsManager, "_applied_preset_id", None)
    monkeypatch.setattr(repository.simulation, "generate_default_name", lambda: "Nova")
    monkeypatch.setattr(UserManager, "reset_teams", lambda: None)
    monkeypatch.setattr(simulation_routes, "notify", lambda *_a, **_k: None)

    app = FastAPI()
    app.include_router(presets_router)
    app.dependency_overrides[get_client_id] = lambda: client("host")
    app.dependency_overrides[verify_host] = lambda: None
    return TestClient(app)


def rules(**changes: object) -> dict[str, object]:
    """O corpo que o lobby envia ao salvar: as regras de teste com o que mudar."""
    body = simulation_settings().model_dump(mode="json")
    body.update(changes)
    return body


def by_name(api: TestClient, name: str) -> dict:
    return next(p for p in api.get("/api/presets").json() if p["name"] == name)


def test_migration_seeds_the_three_built_in_presets(api: TestClient) -> None:
    presets = api.get("/api/presets").json()

    assert [(p["name"], p["built_in"]) for p in presets] == [
        ("Iniciante", True),
        ("Clássico", True),
        ("Realista", True),
    ]


def test_save_rename_and_delete_a_host_preset(api: TestClient) -> None:
    saved = api.post(
        "/api/presets", json={"name": "  Sexta com a turma ", "rules": rules()}
    )
    assert saved.status_code == 201
    preset = saved.json()
    assert preset["name"] == "Sexta com a turma"
    assert preset["built_in"] is False
    assert "name" not in preset["config"]

    renamed = api.patch(f"/api/presets/{preset['id']}", json={"name": "Sexta v2"})
    assert renamed.json()["name"] == "Sexta v2"

    assert api.delete(f"/api/presets/{preset['id']}").status_code == 204
    assert all(p["id"] != preset["id"] for p in api.get("/api/presets").json())


def test_names_are_unique_ignoring_case_and_up_to_sixty_letters(
    api: TestClient,
) -> None:
    repeated = api.post("/api/presets", json={"name": "clássico", "rules": rules()})
    assert repeated.status_code == 409

    too_long = api.post("/api/presets", json={"name": "a" * 61, "rules": rules()})
    assert too_long.status_code == 422

    first = api.post("/api/presets", json={"name": "Meu", "rules": rules()}).json()
    other = api.post("/api/presets", json={"name": "Outro", "rules": rules()}).json()
    clash = api.patch(f"/api/presets/{other['id']}", json={"name": "MEU"})
    assert clash.status_code == 409
    same = api.patch(f"/api/presets/{first['id']}", json={"name": "MEU"})
    assert same.status_code == 200


def test_built_in_presets_do_not_change(api: TestClient) -> None:
    ready = by_name(api, "Clássico")

    rename = api.patch(f"/api/presets/{ready['id']}", json={"name": "X"})
    assert rename.status_code == 409
    assert api.delete(f"/api/presets/{ready['id']}").status_code == 409
    update = api.put(f"/api/presets/{ready['id']}/rules", json={"rules": rules()})
    assert update.status_code == 409


def test_load_applies_the_rules_and_keeps_the_match_name(api: TestClient) -> None:
    SettingsManager.update(simulation_settings().model_copy(update={"name": "Minha"}))
    ready = by_name(api, "Iniciante")

    response = api.post(f"/api/presets/{ready['id']}/load")

    assert response.status_code == 200
    body = response.json()
    assert body["settings"]["name"] == "Minha"
    assert body["settings"]["start_date"] == "2018-01-01"
    assert Decimal(body["settings"]["starting_cash"]) == 10000
    assert body["settings"]["victory_criterion"] == "NETWORTH"
    assert body["applied"] == {
        "id": ready["id"],
        "name": "Iniciante",
        "built_in": True,
        "changed": [],
    }
    assert body["defaulted"] == []
    assert SettingsManager.get().start_date == date(2018, 1, 1)
    assert repository.last_simulation_settings.get() is not None


def test_realista_is_the_expert_financial_independence_game(api: TestClient) -> None:
    ready = by_name(api, "Realista")

    settings = api.post(f"/api/presets/{ready['id']}/load").json()["settings"]

    assert settings["game_type"] == GameType.FINANCIAL_INDEPENDENCE.value
    assert settings["price_impact_enabled"] is True
    assert settings["price_impact_k"] == 0.02
    assert settings["price_impact_decay_days"] == 20
    assert settings["show_equivalent_rate"] is False
    assert settings["show_maturity_projection"] is False


def test_load_ignores_unknown_fields_and_completes_missing_ones(
    api: TestClient,
) -> None:
    preset = api.post("/api/presets", json={"name": "Antigo", "rules": rules()}).json()
    old_config = {
        "start_date": "2015-03-02",
        "end_date": "2016-03-02",
        "campo_de_uma_versao_futura": 1,
    }
    repository.preset.update_config(preset["id"], old_config)

    response = api.post(f"/api/presets/{preset['id']}/load").json()

    assert response["settings"]["start_date"] == "2015-03-02"
    assert response["settings"]["show_equivalent_rate"] is True
    assert PresetRuleGroup.ASSISTANCES.value in response["defaulted"]
    assert PresetRuleGroup.PERIOD.value not in response["defaulted"]


def test_load_resets_the_teams_when_the_mode_changes(
    api: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    resets: list[bool] = []
    monkeypatch.setattr(UserManager, "reset_teams", lambda: resets.append(True))
    SettingsManager.update(simulation_settings(PlayerGrouping.TEAMS))
    ready = by_name(api, "Clássico")

    api.post(f"/api/presets/{ready['id']}/load")
    assert resets == [True]

    api.post(f"/api/presets/{ready['id']}/load")
    assert resets == [True]


def test_load_is_refused_while_a_saved_match_is_selected(
    api: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 7)
    ready = by_name(api, "Clássico")

    assert api.post(f"/api/presets/{ready['id']}/load").status_code == 409


def test_applied_preset_reports_which_groups_changed(api: TestClient) -> None:
    ready = by_name(api, "Clássico")
    api.post(f"/api/presets/{ready['id']}/load")

    SettingsManager.update(
        SettingsManager.get().model_copy(update={"starting_cash": Decimal(50000)})
    )
    applied = SettingsManager.applied_preset()

    assert applied is not None
    assert applied.changed == [PresetRuleGroup.STARTING_CASH]

    SettingsManager.update(
        SettingsManager.get().model_copy(update={"starting_cash": Decimal(100000)})
    )
    applied = SettingsManager.applied_preset()
    assert applied is not None
    assert applied.changed == []


def test_saving_makes_the_new_preset_the_applied_one_and_restore_clears_it(
    api: TestClient,
) -> None:
    saved = api.post("/api/presets", json={"name": "Meu", "rules": rules()}).json()
    applied = SettingsManager.applied_preset()
    assert applied is not None
    assert applied.id == saved["id"]

    SettingsManager.restore_defaults()
    assert SettingsManager.applied_preset() is None


def test_deleting_the_applied_preset_leaves_the_rules_without_a_preset(
    api: TestClient,
) -> None:
    saved = api.post("/api/presets", json={"name": "Meu", "rules": rules()}).json()

    api.delete(f"/api/presets/{saved['id']}")

    assert SettingsManager.applied_preset() is None


def test_update_rules_overwrites_a_host_preset(api: TestClient) -> None:
    saved = api.post("/api/presets", json={"name": "Meu", "rules": rules()}).json()

    updated = api.put(
        f"/api/presets/{saved['id']}/rules",
        json={"rules": rules(starting_cash="777")},
    ).json()

    assert Decimal(str(updated["config"]["starting_cash"])) == 777
    assert updated["name"] == "Meu"
