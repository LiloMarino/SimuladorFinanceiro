"""A conta do Fundo Soberano na sala: quem opera, o que compra, o painel e a prévia do aporte."""

# As fixtures do livro vêm dos módulos dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

import threading
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.dto.position import PositionDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, OrderAction
from backend.core.exceptions.http_exceptions import ConflictError, ForbiddenError
from backend.features.government import governance
from backend.features.government.government_book import GovernmentBook
from backend.features.simulation.simulation import Simulation
from backend.features.variable_income.entities.order import Order
from backend.routes.dependencies import ActingClient, get_current_user
from backend.routes.dependencies.auth import get_client_id
from backend.routes.dependencies.simulation import get_active_simulation
from backend.routes.sovereign_fund import sovereign_fund_router
from tests.fakes import bare_simulation
from tests.test_government_book import (
    ALICE,
    BOB,
    TERM_START,
    book,
    engine,
    govern,
    headlines,
    market,
    notices,
    office,
    stored,
)
from tests.test_sovereign_fund_book import fund_with_cash
from tests.test_state_company_measures import match, no_frozen_portfolio

BASE = "/api/government/sovereign-fund"
D = Decimal
BILLION = D(10) ** 9
ISSUED = D(1000)


def _simulation(
    book: GovernmentBook,
    engine,
    *,
    asset_class: AssetClass = AssetClass.STOCK,
    positions: dict[str, Any] | None = None,
    resting: list[Any] | None = None,
) -> Simulation:
    simulation = bare_simulation()
    simulation._engine = SimpleNamespace(  # type: ignore[assignment]
        _lock=threading.RLock(),
        asset_class=lambda _ticker: asset_class,
        get_cash=engine.get_cash,
        broker=SimpleNamespace(get_positions=lambda _client: positions or {}),
        matching_engine=SimpleNamespace(
            order_book=SimpleNamespace(orders_of=lambda _client: resting or [])
        ),
    )
    simulation.settings = cast("SimulationDTO", SimpleNamespace())
    simulation._funds = None
    simulation._government = book
    simulation._current_date = TERM_START
    return simulation


def _app(simulation: Simulation, user: UserDTO) -> TestClient:
    app = FastAPI()
    app.include_router(sovereign_fund_router)

    @app.get("/acting")
    def acting(account: ActingClient) -> str:
        return str(account)

    app.dependency_overrides[get_active_simulation] = lambda: simulation
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_client_id] = lambda: user.client_id
    return TestClient(app)


def _order(
    client_id, size: int, ticker: str = "PETR4", action=OrderAction.BUY
) -> Order:
    return cast(
        "Order",
        SimpleNamespace(
            client_id=client_id, ticker=ticker, size=D(size), action=action
        ),
    )


def _issued(monkeypatch, book: GovernmentBook, issued: Decimal | None = ISSUED):
    monkeypatch.setattr(book, "issued_of", lambda _ticker: ("Empresa", issued, False))


# A conta do fundo


def test_the_president_operates_the_fund_account(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    fund = book.sovereign_fund().client_id

    acting = _app(_simulation(book, engine), ALICE).get(
        "/acting", headers={"X-Account": "0"}
    )

    assert acting.status_code == 200
    assert acting.json() == str(fund)


def test_nobody_else_operates_the_fund_account(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    response = _app(_simulation(book, engine), BOB).get(
        "/acting", headers={"X-Account": "0"}
    )

    assert response.status_code == 403


def test_the_fund_follows_the_office_when_the_president_changes(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    fund = book.sovereign_fund().client_id
    simulation = _simulation(book, engine)

    monkeypatch.setattr(book, "president", lambda: BOB)

    assert simulation.acting_client(BOB.client_id, 0) == fund
    with pytest.raises(ForbiddenError):
        simulation.acting_client(ALICE.client_id, 0)


def test_the_account_list_shows_the_fund_only_to_the_president(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    fund_with_cash(book, engine, 25)
    simulation = _simulation(book, engine)

    president = simulation.get_fund_accounts(ALICE)
    room = simulation.get_fund_accounts(BOB)

    assert [account.fund_id for account in president] == [None, 0]
    fund = president[1]
    assert (fund.name, fund.role, fund.cash) == (
        "Fundo Soberano",
        "president",
        25 * BILLION,
    )
    assert [account.fund_id for account in room] == [None]


# O que o fundo compra


def test_a_purchase_within_the_cash_and_the_ceiling_passes(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book)
    fund = book.sovereign_fund().client_id

    _simulation(book, engine)._ensure_sovereign_order(_order(fund, 200))


def test_a_purchase_over_twenty_percent_is_refused(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book)
    fund = book.sovereign_fund().client_id

    with pytest.raises(ConflictError, match="não passa de 20%"):
        _simulation(book, engine)._ensure_sovereign_order(_order(fund, 201))


def test_the_ceiling_counts_what_the_fund_already_holds_and_its_open_orders(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book)
    fund = book.sovereign_fund().client_id
    held = {"PETR4": SimpleNamespace(size=D(150))}
    resting = [SimpleNamespace(ticker="PETR4", action=OrderAction.BUY, remaining=D(30))]
    simulation = _simulation(book, engine, positions=held, resting=resting)

    simulation._ensure_sovereign_order(_order(fund, 20))
    with pytest.raises(ConflictError, match="cabem mais 20"):
        simulation._ensure_sovereign_order(_order(fund, 21))


def test_the_ceiling_holds_for_the_quotas_of_a_manager_too(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    monkeypatch.setattr(book, "issued_of", lambda _ticker: ("Aura", ISSUED, True))
    fund = book.sovereign_fund().client_id
    simulation = _simulation(book, engine, asset_class=AssetClass.FUND)

    simulation._ensure_sovereign_order(_order(fund, 200, "AURA11"))
    with pytest.raises(ConflictError, match="não passa de 20%"):
        simulation._ensure_sovereign_order(_order(fund, 201, "AURA11"))


def test_a_stock_without_the_number_of_shares_is_not_bought(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book, None)
    fund = book.sovereign_fund().client_id

    with pytest.raises(ConflictError, match="Sem o número de ações em circulação"):
        _simulation(book, engine)._ensure_sovereign_order(_order(fund, 1))


@pytest.mark.parametrize(
    "asset_class", [AssetClass.FII, AssetClass.ETF, AssetClass.CRYPTO]
)
def test_the_fund_buys_only_stocks_and_manager_quotas(
    book: GovernmentBook, engine, market, match, monkeypatch, asset_class
):
    govern(book, engine)
    _issued(monkeypatch, book)
    fund = book.sovereign_fund().client_id

    with pytest.raises(ConflictError, match="só ações e cotas de gestora"):
        _simulation(book, engine, asset_class=asset_class)._ensure_sovereign_order(
            _order(fund, 1)
        )


def test_a_sale_and_other_accounts_skip_the_fund_rules(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book, None)
    fund = book.sovereign_fund().client_id
    simulation = _simulation(book, engine)

    simulation._ensure_sovereign_order(_order(fund, 999, action=OrderAction.SELL))
    simulation._ensure_sovereign_order(_order(ALICE.client_id, 999))


def test_the_fund_has_no_fixed_income(book: GovernmentBook, engine, market, match):
    govern(book, engine)
    fund = book.sovereign_fund().client_id
    simulation = _simulation(book, engine)

    with pytest.raises(ConflictError, match="só ações e cotas de gestora"):
        simulation._ensure_not_sovereign(fund)
    simulation._ensure_not_sovereign(ALICE.client_id)


# O painel e a prévia


def _position(ticker: str, size: int, price: int) -> PositionDTO:
    value = D(size * price)
    return PositionDTO(
        ticker=ticker,
        size=D(size),
        reserved=D(0),
        total_cost=value,
        avg_price=D(price),
        current_price=D(price),
        current_value=value,
        return_value=D(0),
        return_pct=D(0),
    )


def test_the_room_reads_the_panel_and_only_the_president_commands(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    fund_with_cash(book, engine, 25)
    monkeypatch.setattr(engine, "equity_positions", lambda _client: [])
    simulation = _simulation(book, engine)

    president = _app(simulation, ALICE).get(BASE).json()
    room = _app(simulation, BOB).get(BASE).json()

    assert president["is_president"] is True
    assert room["is_president"] is False
    assert D(president["cash"]) == 25 * BILLION
    assert D(president["ceiling"]) == D("0.20")
    assert president["positions"] == []


def test_the_panel_shows_the_stake_and_the_room_of_each_position(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book)
    monkeypatch.setattr(
        engine, "equity_positions", lambda _client: [_position("PETR4", 150, 10)]
    )

    panel = _app(_simulation(book, engine), ALICE).get(BASE).json()

    [row] = panel["positions"]
    assert D(row["stake"]) == D("0.15")
    assert D(row["room"]) == 50
    assert D(panel["invested"]) == 1500


def test_a_stock_without_the_number_of_shares_has_no_stake_in_the_panel(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book, None)
    monkeypatch.setattr(
        engine, "equity_positions", lambda _client: [_position("PETR4", 10, 10)]
    )

    [row] = _app(_simulation(book, engine), ALICE).get(BASE).json()["positions"]

    assert row["stake"] is None
    assert row["room"] is None


def test_the_contribution_preview_shows_the_cash_before_and_after(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    fund_with_cash(book, engine, 10)

    response = _app(_simulation(book, engine), ALICE).post(
        f"{BASE}/contribution-preview", json={"value": str(25 * BILLION)}
    )

    assert response.status_code == 200
    preview = response.json()
    assert D(preview["cash_before"]) == 10 * BILLION
    assert D(preview["cash_after"]) == 35 * BILLION
    assert preview["measure"]["inflation"] is None
    budget = preview["measure"]["budget"]
    assert D(budget["debt_after"]) > D(budget["debt_before"])


def test_only_the_president_previews_a_contribution(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    response = _app(_simulation(book, engine), BOB).post(
        f"{BASE}/contribution-preview", json={"value": str(25 * BILLION)}
    )

    assert response.status_code in (403, 409)


# A prévia da compra na boleta do fundo


def test_the_order_preview_shows_the_stake_before_and_after_the_purchase(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book)
    fund = book.sovereign_fund().client_id
    held = {"PETR4": SimpleNamespace(size=D(100))}
    simulation = _simulation(book, engine, positions=held)

    preview = simulation._sovereign_preview(fund, "PETR4", D(50))

    assert preview is not None
    assert (preview.stake_before, preview.stake_after) == (D("0.1"), D("0.15"))
    assert preview.room == 100
    assert preview.refusal is None
    assert preview.allied is False


def test_the_order_preview_says_why_the_fund_does_not_buy(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book, None)
    fund = book.sovereign_fund().client_id

    preview = _simulation(book, engine)._sovereign_preview(fund, "PETR4", D(1))

    assert preview is not None
    assert preview.stake_after is None
    assert preview.refusal is not None
    assert "Sem o número de ações" in preview.refusal


def test_the_order_preview_marks_an_allied_manager(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    fund = book.sovereign_fund().client_id
    monkeypatch.setattr(book, "issued_of", lambda _ticker: ("Aura", ISSUED, True))
    monkeypatch.setattr(book, "is_allied_manager", lambda _ticker, _day: True)

    preview = _simulation(book, engine, asset_class=AssetClass.FUND)._sovereign_preview(
        fund, "AURA11", D(10)
    )

    assert preview is not None
    assert preview.is_fund and preview.allied


def test_other_accounts_get_no_fund_preview(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    _issued(monkeypatch, book)

    assert (
        _simulation(book, engine)._sovereign_preview(ALICE.client_id, "PETR4", D(1))
        is None
    )
