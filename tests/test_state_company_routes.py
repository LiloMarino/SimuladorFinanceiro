"""Rotas das estatais: o painel que todos leem, as prévias, a ordem do presidente, a reserva na oferta e a marcação da base."""

# As fixtures do livro vêm dos módulos dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    AssetClass,
    StateCompanySize,
    StateControl,
    StateLever,
)
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.government import governance
from backend.features.government.government_book import GovernmentBook
from backend.features.simulation.simulation import Simulation
from backend.routes.dependencies import get_current_user
from backend.routes.dependencies.auth import get_client_id
from backend.routes.dependencies.simulation import (
    get_active_simulation,
    require_no_active_simulation,
)
from backend.routes.importer import import_router
from backend.routes.state_companies import state_companies_router
from tests.fakes import client
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
from tests.test_government_state_orders import (
    ENERGY,
    FUEL,
    PLAIN,
    new_state_book,
    order,
    state_book,
)
from tests.test_state_company_measures import match, privatize

BASE = "/api/government/state-companies"
D = Decimal
FOUND_BODY = {
    "name": "Petro Nova",
    "ticker": "PNOV3",
    "size": "SMALL",
    "lever": "FUEL",
}


@pytest.fixture(autouse=True)
def room(monkeypatch: pytest.MonkeyPatch, engine) -> None:
    """A sala sem banco de ativos: a bolsa cota a importada a 20, e todo jogador tem a carteira 1."""
    engine.matching_engine = SimpleNamespace(
        market_data=SimpleNamespace(
            get_last=lambda _ticker: SimpleNamespace(close=20.0)
        )
    )
    monkeypatch.setattr(governance, "_portfolio", lambda *_: None)
    monkeypatch.setattr(SimulationManager, "get_portfolio_id", lambda _user_id: 1)
    monkeypatch.setattr(
        GovernmentBook, "_stock_name", lambda _self, ticker: f"Empresa {ticker}"
    )


def _simulation(book: GovernmentBook, day: date = TERM_START) -> Simulation:
    simulation = object.__new__(Simulation)
    simulation._engine = SimpleNamespace(  # type: ignore[assignment]
        _lock=threading.RLock()
    )
    simulation.settings = cast("SimulationDTO", SimpleNamespace())
    simulation._funds = None
    simulation._government = book
    simulation._current_date = day
    return simulation


def _app(simulation: Simulation, user: UserDTO) -> TestClient:
    app = FastAPI()
    app.include_router(state_companies_router)
    app.dependency_overrides[get_active_simulation] = lambda: simulation
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_client_id] = lambda: user.client_id
    return TestClient(app)


def _as(book: GovernmentBook, user: UserDTO, day: date = TERM_START) -> TestClient:
    return _app(_simulation(book, day), user)


def _row(panel: dict, ticker: str) -> dict:
    return next(row for row in panel["companies"] if row["ticker"] == ticker)


# O painel


def test_the_president_reads_the_panel_and_can_command(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)

    response = _as(state_book, ALICE).get(BASE)

    assert response.status_code == 200
    panel = response.json()
    assert panel["is_president"] is True
    assert {row["ticker"] for row in panel["companies"]} == {
        FUEL,
        ENERGY,
        "BBAS3",
        PLAIN,
    }
    fuel = _row(panel, FUEL)
    assert fuel["name"] == f"Empresa {FUEL}"
    assert fuel["can_command"] is True
    assert fuel["order"]["control"] == "P10"
    # A ordem dada vale só no mês seguinte
    assert fuel["in_force"]["control"] == "NONE"
    assert Decimal(fuel["price"]) == 20
    # A importada também mostra o que o Tesouro recebeu nos 12 meses
    assert Decimal(fuel["treasury_dividend_12m"]) >= 0
    assert Decimal(panel["summary"]["cap_points"]) == D("1.5")
    # A importada não tem fundação; o preço da oferta é o de mercado
    assert fuel["invested"] is None
    assert Decimal(fuel["fair_price"]) == 20


def test_the_panel_delivers_the_rules_the_screen_reads(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)

    rules = _as(state_book, ALICE).get(BASE).json()["rules"]

    assert Decimal(rules["founding_share"]) == D("0.51")
    assert rules["offer_sessions"] == 5
    small = next(size for size in rules["sizes"] if size["size"] == "SMALL")
    assert Decimal(small["capital"]) == 30 * 10**9
    assert Decimal(small["government_debt"]) == D("15.3") * 10**9
    fuel = next(lever for lever in rules["levers"] if lever["lever"] == "FUEL")
    assert Decimal(fuel["ipca_weight"]) == D("0.05")
    assert Decimal(fuel["credit_weight"]) == 0
    bank = next(lever for lever in rules["levers"] if lever["lever"] == "BANK")
    assert Decimal(bank["credit_weight"]) == D("0.05")


def test_the_room_reads_the_panel_but_does_not_command(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)

    response = _as(state_book, BOB).get(BASE)

    assert response.status_code == 200
    panel = response.json()
    assert panel["is_president"] is False
    assert not any(row["can_command"] for row in panel["companies"])


def test_a_queued_privatization_takes_the_command_of_that_company(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    privatize(state_book, FUEL)

    panel = _as(state_book, ALICE).get(BASE).json()

    fuel = _row(panel, FUEL)
    assert fuel["can_command"] is False
    assert fuel["privatization_measure_id"] == 1
    assert _row(panel, ENERGY)["can_command"] is True


def test_the_panel_is_refused_when_the_expansion_is_off():
    simulation = _simulation(None)  # type: ignore[arg-type]

    response = _app(simulation, ALICE).get(BASE)

    assert response.status_code == 409


# A prévia da ordem


def test_the_order_preview_blocks_the_step_over_the_ceiling(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P20)

    response = _as(state_book, BOB).get(f"{BASE}/{ENERGY}/order-preview")

    assert response.status_code == 200
    preview = response.json()
    assert preview["can_command"] is False
    assert Decimal(preview["other_points"]) == 1
    steps = {step["control"]: step for step in preview["steps"]}
    assert steps["P20"]["blocked_reason"] is not None
    assert steps["P10"]["blocked_reason"] is None
    assert steps["NONE"]["blocked_reason"] is None
    assert Decimal(steps["P10"]["price_factor"]) < 1
    assert {p["dividend_policy"] for p in preview["policies"]} == {
        "REINVEST",
        "NORMAL",
        "SQUEEZE",
    }


def test_the_order_preview_of_a_company_without_price_to_hold_blocks_every_step(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)

    preview = _as(state_book, ALICE).get(f"{BASE}/{PLAIN}/order-preview").json()

    steps = {step["control"]: step for step in preview["steps"]}
    assert steps["NONE"]["blocked_reason"] is None
    assert all(
        steps[control]["blocked_reason"] for control in ("P5", "P10", "P15", "P20")
    )


def test_the_order_preview_of_an_unknown_company_is_not_found(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)

    response = _as(state_book, ALICE).get(f"{BASE}/ZZZZ3/order-preview")

    assert response.status_code == 404


# A ordem


def test_the_president_gives_the_order(state_book: GovernmentBook, engine, market):
    govern(state_book, engine)

    response = _as(state_book, ALICE).put(
        f"{BASE}/{FUEL}/order",
        json={"control": "P10", "dividend_policy": "SQUEEZE"},
    )

    assert response.status_code == 204
    given = state_book.state.state_orders[FUEL]
    assert (given.control.value, given.dividend_policy.value) == ("P10", "SQUEEZE")


def test_only_the_president_gives_the_order(state_book: GovernmentBook, engine, market):
    govern(state_book, engine)

    response = _as(state_book, BOB).put(
        f"{BASE}/{FUEL}/order", json={"control": "P5", "dividend_policy": "NORMAL"}
    )

    assert response.status_code == 403
    assert state_book.state.state_orders == {}


def test_a_company_in_privatization_takes_no_order(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    privatize(state_book, FUEL)

    response = _as(state_book, ALICE).put(
        f"{BASE}/{FUEL}/order", json={"control": "P5", "dividend_policy": "NORMAL"}
    )

    assert response.status_code == 403


def test_a_step_over_the_ceiling_is_unprocessable(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P20)

    response = _as(state_book, ALICE).put(
        f"{BASE}/{ENERGY}/order", json={"control": "P20", "dividend_policy": "NORMAL"}
    )

    assert response.status_code == 422


def test_an_unknown_step_is_unprocessable(state_book: GovernmentBook, engine, market):
    govern(state_book, engine)

    response = _as(state_book, ALICE).put(
        f"{BASE}/{FUEL}/order", json={"control": "P99", "dividend_policy": "NORMAL"}
    )

    assert response.status_code == 422


# A prévia da fundação


def test_the_president_previews_the_foundation(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    response = _as(book, ALICE).post(f"{BASE}/found-preview", json=FOUND_BODY)

    assert response.status_code == 200
    preview = response.json()
    assert preview["measure"]["title"] == "Fundar a Petro Nova (PNOV3)"
    assert Decimal(preview["invested"]) > 0
    assert Decimal(preview["monthly_spending"]) > 0
    assert preview["spending_months"] > 0
    assert Decimal(preview["gdp_push"]) > 0
    assert Decimal(preview["expected_treasury_dividend_year"]) >= 0


def test_only_the_president_previews_the_foundation(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    response = _as(book, BOB).post(f"{BASE}/found-preview", json=FOUND_BODY)

    assert response.status_code == 403


def test_a_taken_ticker_is_refused_in_the_foundation_preview(
    state_book: GovernmentBook, engine, market, match
):
    govern(state_book, engine)

    response = _as(state_book, ALICE).post(
        f"{BASE}/found-preview", json={**FOUND_BODY, "ticker": FUEL}
    )

    assert response.status_code == 409


# A reserva na oferta de privatização


class Offering:
    """A fundada com a oferta aberta no dia da posse e a carteira de quem reserva."""

    def __init__(self, book: GovernmentBook, simulation_id: int) -> None:
        self.book = book
        found = book.state_companies().found(
            ticker="PNOV3",
            name="Petro Nova",
            size=StateCompanySize.SMALL,
            lever=StateLever.FUEL,
            real_interest=D("0.05"),
            today=TERM_START,
        )
        assert found is not None
        book.state_companies().open_privatization("PNOV3", TERM_START)
        self.ends_on = book.state_companies().offer_ends_on("PNOV3")
        assert self.ends_on is not None
        user = repository.user.create_user(client("reserva"), "Reserva")
        self.portfolio = repository.portfolio.create(simulation_id, [user.id])[user.id]
        self.company_id = found.id

    def reservations(self) -> dict[int, Decimal]:
        return repository.state_company.reservations_of(self.company_id)


@pytest.fixture
def offering(
    engine,
    stored,
    notices,
    captured_events,
    office,
    headlines,
    market,
    match,
    monkeypatch,
) -> Offering:
    book = new_state_book(engine, office, headlines, [])
    govern(book, engine)
    offering = Offering(book, match)
    monkeypatch.setattr(
        SimulationManager, "get_portfolio_id", lambda _user_id: offering.portfolio
    )
    return offering


def test_a_reservation_inside_the_window_is_saved(offering: Offering):
    response = _as(offering.book, BOB).post(
        f"{BASE}/offer/reservation", json={"ticker": "PNOV3", "quantity": 150}
    )

    assert response.status_code == 204
    assert offering.reservations() == {offering.portfolio: D(150)}


def test_a_new_reservation_replaces_the_previous_one(offering: Offering):
    app = _as(offering.book, BOB)

    app.post(f"{BASE}/offer/reservation", json={"ticker": "PNOV3", "quantity": 150})
    app.post(f"{BASE}/offer/reservation", json={"ticker": "PNOV3", "quantity": 40})

    assert offering.reservations() == {offering.portfolio: D(40)}


def test_a_reservation_outside_the_window_is_a_conflict(offering: Offering):
    assert offering.ends_on is not None
    late = offering.ends_on + timedelta(days=1)

    response = _as(offering.book, BOB, late).post(
        f"{BASE}/offer/reservation", json={"ticker": "PNOV3", "quantity": 10}
    )

    assert response.status_code == 409
    assert offering.reservations() == {}


@pytest.mark.parametrize("quantity", [0, -3])
def test_a_reservation_takes_a_positive_quantity(offering: Offering, quantity: int):
    response = _as(offering.book, BOB).post(
        f"{BASE}/offer/reservation", json={"ticker": "PNOV3", "quantity": quantity}
    )

    assert response.status_code == 422


def test_the_panel_shows_the_offer_and_the_reservation_of_who_looks(
    offering: Offering,
):
    app = _as(offering.book, BOB)
    app.post(f"{BASE}/offer/reservation", json={"ticker": "PNOV3", "quantity": 150})

    panel = app.get(BASE).json()

    [offer] = panel["offers"]
    assert offer["ticker"] == "PNOV3"
    assert Decimal(offer["reserved"]) == 150
    assert Decimal(offer["your_reservation"]) == 150
    assert offer["shares"] > 0
    # A fundada mostra o que o governo pagou pela fatia e o preço que a oferta usa
    pnov = _row(panel, "PNOV3")
    assert Decimal(pnov["invested"]) == D("15.3") * 10**9
    assert Decimal(pnov["fair_price"]) == Decimal(offer["price"])


# A marcação de estatal na base


@pytest.fixture
def importing(database: Engine) -> TestClient:
    app = FastAPI()
    app.include_router(import_router)
    app.dependency_overrides[require_no_active_simulation] = lambda: None
    return TestClient(app)


def test_an_unmarked_stock_reads_as_nothing(importing: TestClient):
    repository.stock.add_stock("PETR4", "Petrobras", AssetClass.STOCK)

    response = importing.get("/api/import-assets/stocks/PETR4/state")

    assert response.status_code == 200
    assert response.json() is None


def test_a_marked_stock_reads_back_its_mark(importing: TestClient):
    repository.stock.add_stock("PETR4", "Petrobras", AssetClass.STOCK)
    importing.put(
        "/api/import-assets/stocks/PETR4/state",
        json={"government_share": "0.36", "shares": 1000, "lever": "FUEL"},
    )

    response = importing.get("/api/import-assets/stocks/PETR4/state")

    assert response.status_code == 200
    mark = response.json()
    assert mark["ticker"] == "PETR4"
    assert Decimal(mark["government_share"]) == D("0.36")
    assert (mark["shares"], mark["lever"]) == (1000, "FUEL")
