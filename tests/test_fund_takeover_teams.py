"""Aquisição hostil em equipes: a equipe é a gestora, formada no lobby e fixa na partida."""

# As fixtures do lobby e do livro vêm dos módulos dos testes vizinhos
# ruff: noqa: F401, F811
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.preparation import FundIdentityDTO
from backend.core.enum import (
    FundPreparationComanagerStatus,
    FundPreparationKind,
    GameType,
    PlayerGrouping,
)
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.statistics.report import build_overview_report
from backend.features.strategy.bots import resolve_bot
from tests.test_bots import person, refusal, room, rules
from tests.test_simulation_loader import started

Status = FundPreparationComanagerStatus


def team_rules():
    return rules(
        funds_enabled=True,
        game_type=GameType.FUND_TAKEOVER,
        player_grouping=PlayerGrouping.TEAMS,
    )


@pytest.fixture
def lobby(room, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(RoomFundPreparation, "_entries", {})
    monkeypatch.setattr(RoomFundPreparation, "_comanagers", {})
    monkeypatch.setattr(SettingsManager, "_settings", team_rules())


def found(user, name: str, ticker: str) -> None:
    RoomFundPreparation._entries[user.id] = FundIdentityDTO(name=name, ticker=ticker)


def accept(owner, guest) -> None:
    RoomFundPreparation._comanagers.setdefault(owner.id, {})[guest.id] = (
        Decimal("0.2"),
        Status.ACCEPTED,
    )


def invite(owner, guest) -> None:
    RoomFundPreparation._comanagers.setdefault(owner.id, {})[guest.id] = (
        Decimal("0.2"),
        Status.INVITED,
    )


# =========================
# Lobby: quem está num grupo não funda nem aceita outro
# =========================


def test_a_co_manager_cannot_found_another_fund(lobby):
    ana, bia = person("Ana"), person("Bia")
    found(ana, "Aurora", "AURA11")
    accept(ana, bia)

    detail = refusal(
        lambda: RoomFundPreparation.choose(
            bia,
            FundPreparationKind.FOUND,
            FundIdentityDTO(name="Brisa", ticker="BRIS11"),
        )
    )

    assert "quem está num grupo não funda outra" in detail
    assert bia.id not in RoomFundPreparation._entries


def test_a_founder_cannot_accept_an_invite(lobby):
    ana, bia = person("Ana"), person("Bia")
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")
    invite(ana, bia)

    detail = refusal(
        lambda: RoomFundPreparation.answer_comanager(bia, [ana, bia], "Ana", True)
    )

    assert "quem está num grupo não aceita outro convite" in detail


def test_who_accepted_one_invite_cannot_accept_a_second(lobby):
    ana, bia, caio = person("Ana"), person("Bia"), person("Caio")
    for founder, name, ticker in ((ana, "Aurora", "AURA11"), (bia, "Brisa", "BRIS11")):
        found(founder, name, ticker)
        invite(founder, caio)
    humans = [ana, bia, caio]
    RoomFundPreparation.answer_comanager(caio, humans, "Ana", True)

    detail = refusal(
        lambda: RoomFundPreparation.answer_comanager(caio, humans, "Bia", True)
    )

    assert "já é co-gestor de uma gestora" in detail


def test_declining_is_always_allowed(lobby):
    ana, bia = person("Ana"), person("Bia")
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")
    invite(ana, bia)

    RoomFundPreparation.answer_comanager(bia, [ana, bia], "Ana", False)

    assert RoomFundPreparation._comanagers[ana.id][bia.id][1] is Status.DECLINED


# =========================
# Lobby: o início exige cada humano em exatamente um grupo
# =========================


def test_the_start_is_blocked_while_a_human_has_no_group(lobby):
    ana, bia, _caio = person("Ana"), person("Bia"), person("Caio")
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")

    detail = refusal(lambda: SimulationLoader.create(team_rules()))

    assert (
        "Caio: em equipes todo jogador funda uma gestora ou é co-gestor de uma."
        in detail
    )
    assert not SimulationManager.has_active_simulation()


def test_the_start_is_blocked_with_a_single_gestora(lobby):
    ana, bia = person("Ana"), person("Bia")
    found(ana, "Aurora", "AURA11")
    accept(ana, bia)

    conflicts = RoomFundPreparation.conflicts([ana, bia], takeover=True, teams=True)

    assert conflicts == ["O modo aquisição hostil precisa de ao menos duas gestoras."]


def test_a_human_in_two_groups_blocks_the_start(lobby):
    ana, bia, caio = person("Ana"), person("Bia"), person("Caio")
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")
    accept(ana, caio)
    accept(bia, caio)

    conflicts = RoomFundPreparation.conflicts(
        [ana, bia, caio], takeover=True, teams=True
    )

    assert conflicts == ["Caio: está em mais de um grupo e precisa ficar em um só."]


def test_bots_do_not_block_the_start(lobby):
    ana, bia = person("Ana"), person("Bia")
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")
    bot = UserManager.add_bot("Rentista", resolve_bot("buy_and_hold", {}))

    SimulationLoader.create(team_rules())

    assert repository.simulation_player.teams(
        SimulationManager.get_active_simulation_id()
    ).keys() == {ana.id, bia.id}
    assert bot.id not in repository.simulation_player.teams(
        SimulationManager.get_active_simulation_id()
    )


# =========================
# Partida: a equipe nasce das gestoras e o caixa de todos entra nelas
# =========================


def test_the_team_is_the_gestora_and_every_members_cash_goes_into_it(lobby):
    ana, bia, caio, dani = (person(n) for n in ("Ana", "Bia", "Caio", "Dani"))
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")
    accept(ana, caio)
    accept(bia, dani)

    settings = team_rules()
    SimulationLoader.create(settings)

    simulation_id = SimulationManager.get_active_simulation_id()
    teams = repository.simulation_player.teams(simulation_id)
    assert teams[ana.id] == teams[caio.id]
    assert teams[bia.id] == teams[dani.id]
    assert teams[ana.id] != teams[bia.id]
    sim = SimulationManager.get_active_simulation()
    assert sim._funds is not None
    fund = sim._funds.get("AURA11")
    # Dois membros de R$ 10.000 ao PL inicial de R$ 100 por cota são 200 cotas
    assert fund.account.quotas == 2 * settings.starting_cash / 100
    assert sim._engine.get_cash(fund.account.client_id) == 2 * settings.starting_cash
    for user in (ana, caio):
        assert sim._engine.get_cash(user.client_id) == Decimal(0)


def test_each_team_carries_the_name_of_the_gestora_its_founder_founded(lobby):
    ana, bia, caio = person("Ana"), person("Bia"), person("Caio")
    found(ana, "Aurora", "AURA11")
    found(bia, "Brisa", "BRIS11")
    accept(ana, caio)

    SimulationLoader.create(team_rules())

    simulation_id = SimulationManager.get_active_simulation_id()
    teams = repository.simulation_player.teams(simulation_id)
    assert repository.fund.team_names(simulation_id) == {
        teams[ana.id]: "Aurora",
        teams[bia.id]: "Brisa",
    }
    overview = build_overview_report([simulation_id])
    assert {t.name for t in overview.teams} == {"Aurora", "Brisa"}
