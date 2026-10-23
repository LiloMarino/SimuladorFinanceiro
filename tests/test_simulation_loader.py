"""Retomada de uma partida salva: jogadores, carteira e data voltam do banco."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import CashflowEventType, EquityEventType
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.features.simulation import simulation_loader
from backend.features.simulation.simulation_loader import SimulationLoader
from tests.fakes import simulation_settings

START = date(2004, 3, 1)
BOUGHT_ON = date(2004, 3, 3)
CASH = Decimal(10000)
PRICE = Decimal("25.00")
QUANTITY = 10


def new_user(nickname: str) -> UserDTO:
    return repository.user.create_user(uuid.uuid4(), nickname)


def saved_match(players: list[UserDTO], buyer: UserDTO) -> int:
    """Partida jogada até `BOUGHT_ON`, em que `buyer` comprou ações do BANK_A."""
    simulation_id = repository.simulation.create_simulation(
        simulation_settings().model_copy(
            update={
                "start_date": START,
                "end_date": date(2004, 12, 31),
                "starting_cash": CASH,
            }
        )
    )
    repository.simulation_player.save(
        simulation_id, {p.id: PLAYER_COLORS[i] for i, p in enumerate(players)}
    )
    repository.user.seed_simulation_users(
        simulation_id, [p.id for p in players], START, CASH
    )
    # A compra é gravada como o broker grava: a ação e o dinheiro que saiu do caixa
    repository.event.insert_many(
        [
            EquityEventDTO(
                simulation_id=simulation_id,
                user_id=buyer.id,
                event_date=BOUGHT_ON,
                ticker="BANK_A",
                event_type=EquityEventType.BUY,
                quantity=QUANTITY,
                price=PRICE,
            ),
            CashflowEventDTO(
                simulation_id=simulation_id,
                user_id=buyer.id,
                event_date=BOUGHT_ON,
                event_type=CashflowEventType.WITHDRAW,
                amount=PRICE * QUANTITY,
            ),
        ]
    )
    return simulation_id


@pytest.fixture
def started(market: Engine, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """
    Sala vazia e sem partida, realtime mudo e o loop sem thread; devolve os
    `start` do loop e as notificações do loader, na ordem.
    """
    monkeypatch.setattr(UserManager, "_active_players", {})
    monkeypatch.setattr(UserManager, "_colors", {})
    monkeypatch.setattr(UserManager, "_saved_colors", {})
    monkeypatch.setattr(UserManager, "_teams", {})
    monkeypatch.setattr(UserManager, "_saved_teams", {})
    monkeypatch.setattr(UserManager, "_bots", {})
    monkeypatch.setattr(UserManager, "_parked_bots", {})
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(SettingsManager, "_settings", None)
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(notify=lambda *_args, **_kwargs: None),
    )

    calls: list[str] = []
    monkeypatch.setattr(
        simulation_loader,
        "simulation_controller",
        SimpleNamespace(start=lambda: calls.append("start")),
    )
    monkeypatch.setattr(
        simulation_loader, "notify", lambda event, _payload: calls.append(event)
    )
    return calls


def test_loading_a_saved_match_restores_players_portfolio_and_date(started):
    ana, bia = new_user("Ana"), new_user("Bia")
    simulation_id = saved_match([ana, bia], buyer=ana)
    # Caio nunca jogou a partida e está na sala: entra nela ao retomar
    caio = new_user("Caio")
    UserManager.player_auth(caio.client_id)
    # O host seleciona a partida no lobby: o novato fica com uma cor que ela não usa
    UserManager.apply_saved_colors(repository.simulation_player.colors(simulation_id))
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None

    settings = SimulationLoader.load(summary)

    sim = SimulationManager.get_active_simulation()
    assert settings.id == simulation_id
    assert SimulationManager.get_active_simulation_id() == simulation_id
    assert sim.get_current_date() == next_business_day(BOUGHT_ON)
    assert {
        p.nickname for p in repository.simulation_player.participants(simulation_id)
    } == {"Ana", "Bia", "Caio"}

    portfolio = sim.get_portfolio(ana.client_id)
    [position] = portfolio.variable_income
    assert (position.ticker, position.size) == ("BANK_A", QUANTITY)
    assert position.total_cost == PRICE * QUANTITY
    assert portfolio.cash == CASH - PRICE * QUANTITY
    assert sim.get_portfolio(bia.client_id).cash == CASH
    assert sim.get_portfolio(caio.client_id).cash == CASH

    assert started == ["start", "simulation_started"]


def test_loading_a_saved_match_restores_the_assistance_rules(started):
    simulation_id = repository.simulation.create_simulation(
        simulation_settings().model_copy(
            update={
                "start_date": START,
                "end_date": date(2004, 12, 31),
                "show_equivalent_rate": False,
            }
        )
    )
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None

    settings = SimulationLoader.load(summary)

    assert not settings.show_equivalent_rate
    assert settings.show_maturity_projection
    assert not SimulationManager.get_active_simulation().settings.show_equivalent_rate
