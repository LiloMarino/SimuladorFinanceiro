"""Os avisos da estratégia pelo tempo real, com banco: registro por cursor de id, linhas novas, ordem que fecha depois, modo da conta e pendência do erro."""

from __future__ import annotations

from typing import Any

import pytest

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import StrategyGroup, StrategyLogKind, StrategyOrderStatus
from backend.features.simulation import feed_support
from backend.features.strategy import runner as runner_module
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.context import StrategyContext
from backend.features.strategy.registry import STRATEGIES
from tests.test_simulation_loader import new_user, saved_match, started  # noqa: F401
from tests.test_strategy_engine import Boom, BuyOne, match  # noqa: F401


class BuyFarBelow(BaseStrategy):
    """Deixa uma ordem limitada longe do preço: ela segue aberta no book."""

    key = "buy_far_below"
    name = "Compra longe"
    summary = "Teste"
    description = "Teste"
    group = StrategyGroup.TACTIC

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        ctx.buy("BANK_A", 1, "Deixou uma ordem aberta", limit=0.01)


class Sent:
    """Os avisos que o servidor entregou, por evento e cliente."""

    def __init__(self) -> None:
        self.items: list[tuple[str, Any, Any]] = []

    def of(self, event: str) -> list[tuple[Any, Any]]:
        return [(to, payload) for name, to, payload in self.items if name == event]

    def clear(self) -> None:
        self.items.clear()


@pytest.fixture
def sent(match, monkeypatch: pytest.MonkeyPatch) -> Sent:  # noqa: F811
    """Ana e Bia assinam os avisos; o que seria enviado fica registrado."""
    _sim, ana, bia = match
    monkeypatch.setitem(STRATEGIES, BuyFarBelow.key, BuyFarBelow)
    recorded = Sent()
    events = {
        "strategy_update",
        "strategy_log_update",
        "pending_update",
    }

    def listening(event: str):
        return {ana.client_id, bia.client_id} if event in events else set()

    def notify(event: str, payload: Any, to: Any = None) -> None:
        recorded.items.append((event, to, payload))

    for module in (runner_module, feed_support):
        monkeypatch.setattr(module, "subscribed_clients", listening)
        monkeypatch.setattr(module, "notify", notify)
    return recorded


def test_the_log_pages_by_id_without_repeating_or_skipping_a_row(match):  # noqa: F811
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_one", {})
    for _ in range(4):
        sim.next_tick()

    everything = sim.get_strategy_log(ana, "all", None, 100)
    pages = []
    cursor = None
    while True:
        page = sim.get_strategy_log(ana, "all", cursor, 2)
        if not page.items:
            break
        pages.append(page)
        cursor = page.items[-1].id
    paged = [row.id for page in pages for row in page.items]

    assert paged == [row.id for row in everything.items]
    assert len(set(paged)) == len(paged) == everything.total
    assert all(page.total == everything.total for page in pages)


def test_a_cursor_that_is_not_in_the_filter_has_no_rows_before_it(match):  # noqa: F811
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_one", {})
    sim.next_tick()
    [order] = [
        row
        for row in sim.get_strategy_log(ana, "orders", None, 10).items
        if row.kind is StrategyLogKind.ORDER
    ]

    page = sim.get_strategy_log(ana, "modes", order.id, 10)

    assert page.items == []
    assert page.total == 1


def test_the_new_rows_are_sent_with_id_after_they_are_saved(match, sent):  # noqa: F811
    sim, ana, _bia = match
    sim.set_my_strategy(ana, "buy_one", {})
    sent.clear()

    sim.next_tick()

    [(to, payload)] = sent.of("strategy_log_update")
    assert to == ana.client_id
    saved = {row.id: row for row in sim.get_strategy_log(ana, "all", None, 100).items}
    assert payload["rows"]
    assert all(row["id"] in saved for row in payload["rows"])
    assert payload["total_all"] == len(saved)
    assert payload["total_orders"] == 1
    assert payload["account"] is None


def test_a_limit_order_that_closes_later_sends_the_changed_row(match, sent):  # noqa: F811
    sim, ana, _ = match
    sim.set_my_strategy(ana, "buy_far_below", {})
    sim.next_tick()
    [open_row] = [
        row
        for row in sim.get_strategy_log(ana, "orders", None, 10).items
        if row.status is StrategyOrderStatus.OPEN
    ]
    sent.clear()

    sim.set_my_strategy(ana, None, {})

    changed = [
        row
        for _, payload in sent.of("strategy_log_update")
        for row in payload["rows"]
        if row["id"] == open_row.id
    ]
    assert [row["status"] for row in changed] == ["canceled"]


def test_the_mode_goes_with_the_strategy_update(match, sent):  # noqa: F811
    sim, ana, _bia = match
    sim.set_my_strategy(ana, "buy_one", {})

    updates = sent.of("strategy_update")

    assert [to for to, _ in updates] == [ana.client_id]
    [(_, payload)] = updates
    assert payload["account"] is None
    assert payload["my_strategy"]["active"]["key"] == "buy_one"


def test_the_error_returns_the_player_to_manual_and_updates_the_pending(match, sent):  # noqa: F811
    sim, ana, bia = match
    sim.set_my_strategy(ana, "boom", {})
    sent.clear()

    sim.next_tick()

    [(to, payload)] = [
        (to, payload)
        for to, payload in sent.of("strategy_update")
        if payload["my_strategy"]["error"] is not None
    ]
    assert to == ana.client_id
    assert payload["my_strategy"]["active"] is None
    pending = [
        item for dest, item in sent.of("pending_update") if dest == ana.client_id
    ]
    assert pending
    assert any(
        entry["type"] == "STRATEGY_ERROR" for item in pending for entry in item["items"]
    )
    assert all(dest != bia.client_id for dest, _ in sent.of("strategy_update"))
