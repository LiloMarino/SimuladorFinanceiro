"""A gestora preparada no lobby nasce vazia no 1º dia da partida nova, e só nela."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.preparation import FundIdentityDTO
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from backend.features.simulation.simulation_loader import SimulationLoader
from tests.test_bots import person, refusal, room, rules  # noqa: F401
from tests.test_simulation_loader import started  # noqa: F401


@pytest.fixture(autouse=True)
def lobby(room, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: F811
    """Sala com a expansão Gestoras ligada nas regras do lobby e nenhuma gestora preparada."""
    monkeypatch.setattr(RoomFundPreparation, "_entries", {})
    monkeypatch.setattr(SettingsManager, "_settings", rules(funds_enabled=True))


def prepare(user, name: str, ticker: str) -> None:
    RoomFundPreparation._entries[user.id] = FundIdentityDTO(name=name, ticker=ticker)


def test_who_chose_to_found_starts_with_an_empty_closed_fund():
    ana, _bia = person("Ana"), person("Bia")
    prepare(ana, "Aurora", "AURA11")

    SimulationLoader.create(rules(funds_enabled=True))

    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    [fund] = sim._funds.funds()
    assert (fund.terms.name, fund.ticker) == ("Aurora", "AURA11")
    assert fund.terms.founder_user_id == fund.terms.manager_user_id == ana.id
    assert fund.account.quotas == 0
    assert sim._engine.get_cash(fund.account.client_id) == Decimal(0)
    assert not fund.listed
    assert fund.account.offer_remaining is None
    assert (fund.terms.management_fee, fund.terms.performance_fee) == (0, 0)
    assert RoomFundPreparation.prepared([ana]) == []


def test_each_founder_gets_their_own_fund_and_the_rest_get_none():
    ana, bia, _caio = person("Ana"), person("Bia"), person("Caio")
    prepare(ana, "Aurora", "AURA11")
    prepare(bia, "Brisa", "BRIS11")

    SimulationLoader.create(rules(funds_enabled=True))

    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    assert {f.ticker: f.terms.manager_user_id for f in sim._funds.funds()} == {
        "AURA11": ana.id,
        "BRIS11": bia.id,
    }


def test_nobody_founds_when_nobody_chose():
    person("Ana")

    SimulationLoader.create(rules(funds_enabled=True))

    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    assert sim._funds.funds() == []


def test_with_the_expansion_off_the_choice_is_ignored():
    ana = person("Ana")
    prepare(ana, "Aurora", "AURA11")

    SimulationLoader.create(rules(funds_enabled=False))

    sim = SimulationManager.get_active_simulation()
    assert sim._funds is None
    assert (
        repository.fund.of_simulation(SimulationManager.get_active_simulation_id())
        == []
    )


def test_two_players_with_the_same_ticker_block_the_start():
    ana, bia = person("Ana"), person("Bia")
    prepare(ana, "Aurora", "AURA11")
    prepare(bia, "Brisa", "AURA11")

    detail = refusal(lambda: SimulationLoader.create(rules(funds_enabled=True)))

    assert "Ana e Bia" in detail
    assert not SimulationManager.has_active_simulation()


def test_a_ticker_with_the_letters_of_an_imported_asset_blocks_the_start():
    ana = person("Ana")
    prepare(ana, "Banco", "BANK11")

    detail = refusal(lambda: SimulationLoader.create(rules(funds_enabled=True)))

    assert "BANK" in detail
    assert not SimulationManager.has_active_simulation()


def test_a_saved_match_does_not_found_again():
    ana, bia = person("Ana"), person("Bia")
    prepare(ana, "Aurora", "AURA11")
    SimulationLoader.create(rules(funds_enabled=True))
    simulation_id = SimulationManager.get_active_simulation_id()
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    SimulationManager.clear_simulation()
    for user in (ana, bia):
        UserManager.player_auth(user.client_id)
    prepare(bia, "Brisa", "BRIS11")

    SimulationLoader.load(summary)

    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    assert [f.ticker for f in sim._funds.funds()] == ["AURA11"]
    assert RoomFundPreparation.prepared([ana, bia]) == []
