"""A estratégia de cada jogador operando dentro da partida: modo, trava, erro, recusa e retomada."""

from __future__ import annotations

from datetime import date

import pytest

from backend.core import repository
from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import (
    OrderAction,
    StrategyAction,
    StrategyGroup,
    StrategyLogKind,
    StrategyOrderStatus,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.simulation.simulation import Simulation
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.context import StrategyContext
from backend.features.strategy.registry import STRATEGIES
from backend.features.variable_income.entities.order import LimitOrder, MarketOrder
from tests.test_simulation_loader import new_user, saved_match, started  # noqa: F401


class Boom(BaseStrategy):
    key = "boom"
    name = "Quebra sempre"
    summary = "Teste"
    description = "Teste"
    group = StrategyGroup.TACTIC

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        raise RuntimeError("falha de propósito")


class BuyEverything(BaseStrategy):
    """Pede mais ações do que o caixa paga: o mercado recusa a ordem."""

    key = "buy_everything"
    name = "Compra tudo"
    summary = "Teste"
    description = "Teste"
    group = StrategyGroup.TACTIC

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        ctx.buy("BANK_A", 1_000_000, "Quis comprar um milhão de ações")


class BuyOne(BaseStrategy):
    key = "buy_one"
    name = "Compra uma"
    summary = "Teste"
    description = "Teste"
    group = StrategyGroup.TACTIC

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        ctx.buy("BANK_A", 1, "Comprou uma ação")


@pytest.fixture
def match(started, monkeypatch: pytest.MonkeyPatch):  # noqa: F811
    """Partida retomada com Ana e Bia, Ana com ações; devolve a simulação e as duas."""
    for strategy in (Boom, BuyEverything, BuyOne):
        monkeypatch.setitem(STRATEGIES, strategy.key, strategy)
    ana, bia = new_user("Ana"), new_user("Bia")
    UserManager.player_auth(ana.client_id)
    UserManager.player_auth(bia.client_id)
    simulation_id = saved_match([ana, bia], buyer=ana)
    summary = repository.simulation.get_simulation(simulation_id)
    assert summary is not None
    SimulationLoader.load(summary)
    return SimulationManager.get_active_simulation(), ana, bia


def log_of(sim: Simulation, user, kind: str = "all"):
    return sim.get_strategy_log(user, kind, 0, 100).items  # type: ignore[arg-type]


def test_a_player_starts_in_manual_mode(match):
    sim, ana, _ = match
    mine = sim.get_my_strategy(ana)
    assert mine.active is None
    assert mine.error is None
    assert mine.panel is None


def test_the_strategy_runs_only_for_the_player_who_turned_it_on(match):
    sim, ana, bia = match
    sim.set_my_strategy(ana, "buy_one", {})
    before_ana = sim.get_portfolio(ana.client_id).variable_income[0].size

    sim.next_tick()

    assert sim.get_portfolio(ana.client_id).variable_income[0].size == before_ana + 1
    assert sim.get_portfolio(bia.client_id).variable_income == []
    [order] = [r for r in log_of(sim, ana) if r.kind is StrategyLogKind.ORDER]
    assert (order.action, order.ticker, order.quantity) == (
        StrategyAction.BUY,
        "BANK_A",
        1,
    )
    assert order.status is StrategyOrderStatus.EXECUTED
    assert order.price is not None
    assert log_of(sim, bia) == []


def test_turning_on_leaves_a_mode_row_with_the_chosen_strategy(match):
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_one", {})

    mine = sim.get_my_strategy(ana)

    assert mine.active is not None
    assert mine.active.key == "buy_one"
    [row] = log_of(sim, ana, "modes")
    assert row.kind is StrategyLogKind.ENABLED
    assert row.strategy_name == "Compra uma"


def test_the_manual_ticket_is_locked_while_the_automatic_is_on(match):
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_one", {})

    with pytest.raises(ConflictError, match="automático"):
        sim.create_order(
            MarketOrder(
                client_id=ana.client_id,
                ticker="BANK_A",
                size=1,
                action=OrderAction.BUY,
            )
        )
    with pytest.raises(ConflictError):
        sim.cancel_order(order_id="qualquer", client_id=ana.client_id)


def test_going_back_to_manual_unlocks_the_ticket_and_cancels_open_orders(match):
    sim, ana, _ = match
    limit = LimitOrder(
        client_id=ana.client_id,
        ticker="BANK_A",
        size=1,
        action=OrderAction.BUY,
        price=0.01,
    )
    sim.create_order(limit)
    assert sim.get_my_strategy(ana).open_orders == 1

    sim.set_my_strategy(ana, "buy_one", {})
    assert sim.get_my_strategy(ana).open_orders == 0

    sim.set_my_strategy(ana, None, {})
    assert sim.get_my_strategy(ana).active is None
    sim.create_order(
        MarketOrder(
            client_id=ana.client_id, ticker="BANK_A", size=1, action=OrderAction.BUY
        )
    )
    kinds = [r.kind for r in log_of(sim, ana, "modes")]
    assert kinds == [StrategyLogKind.DISABLED, StrategyLogKind.ENABLED]


def test_an_error_in_the_strategy_returns_the_player_to_manual_with_the_cause(match):
    sim, ana, bia = match
    sim.set_my_strategy(ana, "boom", {})
    sim.set_my_strategy(bia, "buy_one", {})

    sim.next_tick()

    mine = sim.get_my_strategy(ana)
    assert mine.active is None
    assert mine.error is not None
    assert mine.error.strategy_key == "boom"
    assert "falha de propósito" in (mine.error.traceback or "")
    assert not mine.error.seen
    # O erro de um jogador não para a estratégia do outro
    assert sim.get_my_strategy(bia).active is not None
    sim.create_order(
        MarketOrder(
            client_id=ana.client_id, ticker="BANK_A", size=1, action=OrderAction.BUY
        )
    )


def test_marking_the_error_as_seen_keeps_it_out_of_the_log(match):
    sim, ana, _ = match
    sim.set_my_strategy(ana, "boom", {})
    sim.next_tick()

    sim.mark_strategy_error_seen(ana)

    assert sim.get_my_strategy(ana).error.seen  # type: ignore[union-attr]
    assert StrategyLogKind.ERROR_SEEN not in [r.kind for r in log_of(sim, ana)]


def test_a_refused_order_is_logged_and_the_strategy_keeps_running(match):
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_everything", {})

    sim.next_tick()
    sim.next_tick()

    assert sim.get_my_strategy(ana).active is not None
    orders = [r for r in log_of(sim, ana) if r.kind is StrategyLogKind.ORDER]
    assert [o.status for o in orders] == [StrategyOrderStatus.REFUSED] * 2
    assert all(o.detail for o in orders)
    panel = sim.get_my_strategy(ana).panel
    assert panel is not None
    assert (panel.orders_total, panel.refused, panel.executed) == (2, 2, 0)


def test_changing_the_parameters_keeps_the_start_date(match):
    sim, ana, _ = match
    params: dict[str, StrategyParamValue] = {
        "short_window": 50,
        "long_window": 200,
        "cash_pct": 20,
        "tickers": ["BANK_A"],
    }
    sim.set_my_strategy(ana, "moving_average_cross", params)
    since = sim.get_my_strategy(ana).active.since  # type: ignore[union-attr]
    sim.next_tick()

    sim.set_my_strategy(ana, "moving_average_cross", {**params, "cash_pct": 30})

    active = sim.get_my_strategy(ana).active
    assert active is not None
    assert active.since == since
    assert active.params["cash_pct"] == 30
    kinds = [r.kind for r in log_of(sim, ana, "modes")]
    assert kinds == [StrategyLogKind.PARAMS, StrategyLogKind.ENABLED]


def test_an_unknown_strategy_or_invalid_parameters_are_refused(match):
    sim, ana, _ = match
    with pytest.raises(Exception, match="desconhecida"):
        sim.set_my_strategy(ana, "nao_existe", {})
    with pytest.raises(Exception, match="Média curta"):
        sim.set_my_strategy(
            ana,
            "moving_average_cross",
            {"short_window": 1, "long_window": 200, "cash_pct": 20},
        )
    assert sim.get_my_strategy(ana).active is None


def test_the_signal_reports_errors_per_field_without_saving_anything(match):
    sim, ana, _ = match
    signal = sim.get_strategy_signal(
        "moving_average_cross",
        {
            "short_window": 60,
            "long_window": 50,
            "cash_pct": 20,
            "tickers": ["BANK_A"],
        },
        "BANK_A",
    )
    assert "long_window" in signal.errors
    assert signal.lines == []
    assert sim.get_my_strategy(ana).active is None


def test_the_strategy_comes_back_when_the_match_is_resumed(match):
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_one", {})
    sim.next_tick()
    last_day: date = sim.get_current_date()
    simulation_id = sim.settings.id
    # Parar a partida grava o que está na fila
    EventManager.flush()

    # A retomada parte do último dia com registro de snapshot
    repository.strategy.rewind(simulation_id, last_day)
    resumed = Simulation(sim.settings, resume_from=last_day, random_seed=1)

    mine = resumed.get_my_strategy(ana)
    assert mine.active is not None
    assert mine.active.key == "buy_one"
    assert mine.resumed
