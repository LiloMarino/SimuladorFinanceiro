"""Preparação da gestora no lobby: escolha, última escolha, conflitos no Iniciar e expansão desligada."""

from __future__ import annotations

from collections.abc import Callable
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.core import repository
from backend.core.dto.preparation import FundIdentityDTO, PreparationsDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import FundPreparationKind
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.government.room_preparation import RoomPreparation
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from tests.fakes import client, simulation_settings

ANA = UserDTO(id=1, client_id=client("ana"), nickname="Ana")
BIA = UserDTO(id=2, client_id=client("bia"), nickname="Bia")
CAIO = UserDTO(id=3, client_id=client("caio"), nickname="Caio")
HUMANS = [ANA, BIA, CAIO]
FOUND = FundPreparationKind.FOUND
NONE = FundPreparationKind.NONE


def fund(name: str = "Aurora", ticker: str = "AURA11") -> FundIdentityDTO:
    return FundIdentityDTO(name=name, ticker=ticker)


def refusal(action: Callable[[], object], status: int = 409) -> str:
    with pytest.raises(HTTPException) as error:
        action()
    assert error.value.status_code == status
    return str(error.value.detail)


def snapshot() -> PreparationsDTO:
    return RoomFundPreparation.apply(RoomPreparation.snapshot(HUMANS), HUMANS)


@pytest.fixture(autouse=True)
def lobby(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lobby de partida nova com a expansão Gestoras ligada, nenhuma gestora preparada e as letras PETR de um ativo."""
    rules = simulation_settings().model_copy(update={"funds_enabled": True})
    monkeypatch.setattr(SettingsManager, "_settings", rules)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(RoomPreparation, "_entries", {})
    monkeypatch.setattr(RoomPreparation, "_left", {})
    monkeypatch.setattr(RoomFundPreparation, "_entries", {})
    monkeypatch.setattr(
        repository,
        "fund",
        SimpleNamespace(letters_taken_by_asset=lambda ticker: ticker[:4] == "PETR"),
    )


def test_player_founds_and_goes_back_to_no_fund():
    RoomFundPreparation.choose(ANA, FOUND, fund())

    assert [(f.nickname, f.name, f.ticker) for f in snapshot().funds] == [
        ("Ana", "Aurora", "AURA11")
    ]

    RoomFundPreparation.choose(ANA, NONE, fund())

    assert snapshot().funds == []


def test_founding_without_a_saved_fund_is_refused():
    assert "Minha gestora" in refusal(
        lambda: RoomFundPreparation.choose(ANA, FOUND, None)
    )


def test_who_never_chose_is_without_fund():
    assert snapshot().funds == []
    assert RoomFundPreparation.prepared(HUMANS) == []


def test_the_choice_is_locked_with_a_match_running_or_a_saved_one_selected(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", 7)

    assert "salva" in refusal(lambda: RoomFundPreparation.choose(ANA, FOUND, fund()))
    assert snapshot().fund_locked_reason is not None

    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(SimulationManager, "has_active_simulation", lambda: True)

    assert "começou" in refusal(lambda: RoomFundPreparation.choose(ANA, FOUND, fund()))


def test_the_last_room_founder_comes_back_founding_once():
    assert RoomFundPreparation.restore(ANA, fund()) is True
    assert RoomFundPreparation.restore(ANA, fund("Outra", "OUTR11")) is False

    assert [f.ticker for f in snapshot().funds] == ["AURA11"]


def test_clear_and_drop_forget_the_choices():
    RoomFundPreparation.choose(ANA, FOUND, fund())
    RoomFundPreparation.choose(BIA, FOUND, fund("Brisa", "BRIS11"))

    RoomFundPreparation.drop(ANA.id)
    assert [f.nickname for f in snapshot().funds] == ["Bia"]

    RoomFundPreparation.clear()
    assert snapshot().funds == []


def test_only_who_is_in_the_room_founds():
    RoomFundPreparation.choose(ANA, FOUND, fund())
    RoomFundPreparation.choose(CAIO, FOUND, fund("Cais", "CAIS11"))

    present = RoomFundPreparation.prepared([ANA, BIA])

    assert [user.nickname for user, _ in present] == ["Ana"]


def test_the_same_ticker_blocks_both_players():
    RoomFundPreparation.choose(ANA, FOUND, fund("Aurora", "AURA11"))
    RoomFundPreparation.choose(BIA, FOUND, fund("Brisa", "AURA11"))

    [message] = snapshot().conflicts
    assert "Ana e Bia" in message and "AURA11" in message
    detail = refusal(lambda: RoomFundPreparation.ensure_ready(HUMANS, enabled=True))
    assert "Ana e Bia" in detail


def test_the_same_name_blocks_both_players_whatever_the_case():
    RoomFundPreparation.choose(ANA, FOUND, fund("Aurora", "AURA11"))
    RoomFundPreparation.choose(BIA, FOUND, fund("AURORA", "BRIS11"))

    [message] = snapshot().conflicts
    assert "Ana e Bia" in message and "nome" in message


def test_different_funds_do_not_conflict():
    RoomFundPreparation.choose(ANA, FOUND, fund("Aurora", "AURA11"))
    RoomFundPreparation.choose(BIA, FOUND, fund("Brisa", "BRIS11"))
    RoomFundPreparation.choose(CAIO, NONE, None)

    assert snapshot().conflicts == []
    RoomFundPreparation.ensure_ready(HUMANS, enabled=True)


def test_who_stays_without_fund_does_not_conflict_with_the_name_of_another():
    RoomFundPreparation.choose(ANA, FOUND, fund())
    RoomFundPreparation.choose(BIA, FOUND, fund("Brisa", "BRIS11"))
    RoomFundPreparation.choose(BIA, NONE, None)

    assert snapshot().conflicts == []


def test_ticker_with_the_letters_of_an_imported_asset_blocks_the_start():
    RoomFundPreparation.choose(ANA, FOUND, fund("Petro", "PETR11"))

    [message] = snapshot().conflicts
    assert "Ana" in message and "PETR" in message
    assert "ativo" in refusal(
        lambda: RoomFundPreparation.ensure_ready(HUMANS, enabled=True)
    )


def test_the_fund_conflicts_join_the_party_ones_in_the_same_list():
    RoomFundPreparation.choose(ANA, FOUND, fund("Aurora", "AURA11"))
    RoomFundPreparation.choose(BIA, FOUND, fund("Brisa", "AURA11"))
    party_conflict = RoomPreparation.snapshot(HUMANS).model_copy(
        update={"conflicts": ["Ana e Bia escolheram a mesma cor."]}
    )

    merged = RoomFundPreparation.apply(party_conflict, HUMANS)

    assert len(merged.conflicts) == 2
    assert merged.conflicts[0] == "Ana e Bia escolheram a mesma cor."


def test_with_the_expansion_off_the_choice_is_ignored(monkeypatch: pytest.MonkeyPatch):
    RoomFundPreparation.choose(ANA, FOUND, fund("Aurora", "AURA11"))
    RoomFundPreparation.choose(BIA, FOUND, fund("Brisa", "AURA11"))
    rules = simulation_settings().model_copy(update={"funds_enabled": False})
    monkeypatch.setattr(SettingsManager, "_settings", rules)

    merged = snapshot()

    assert merged.funds == []
    assert merged.conflicts == []
    RoomFundPreparation.ensure_ready(HUMANS, enabled=False)
