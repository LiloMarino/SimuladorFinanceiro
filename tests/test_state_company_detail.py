"""A estatal na tela da ação: valores por ação, os meses com o motivo de cada um e quem tem as ações."""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from backend.core import repository
from backend.core.decorators import transactional_method
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.state_company import (
    StateCompanyDetailDTO,
    StateCompanyMonthDetailDTO,
    StateCompanyMonthDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    DividendPolicy,
    EquityEventType,
    StateCompanyOrigin,
    StateCompanyStatus,
    StateMonthReason,
)
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.models.models import Portfolios
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.simulation.simulation import Simulation
from backend.features.state_companies import payout, reference
from backend.features.state_companies.book import StateCompanyBook, government_shares
from backend.features.state_companies.detail import build_detail
from backend.routes.dependencies import get_current_user
from backend.routes.dependencies.simulation import get_active_simulation
from backend.routes.operation import operation_router
from tests.test_state_company_book import FOUNDED_ON, _book, _found
from tests.test_state_company_price import _imported_book

D = Decimal
TODAY = date(2022, 8, 10)
MAKER_STOCK = D(400)
PLACES = D("0.0001")
PRICE = D("12.50")


def detail(
    book: StateCompanyBook,
    ticker: str = "PNOV3",
    *,
    price: Decimal | None = PRICE,
    portfolio_id: int | None = None,
    today: date = TODAY,
) -> StateCompanyDetailDTO | None:
    return build_detail(
        book,
        ticker,
        simulation_id=book._simulation_id,
        today=today,
        market_price=lambda _ticker: price,
        maker_stock=lambda _ticker: MAKER_STOCK,
        portfolio_id=portfolio_id,
    )


def months_of(book: StateCompanyBook, today: date) -> list[StateCompanyMonthDetailDTO]:
    result = detail(book, today=today)
    assert result is not None
    return result.months


def test_a_ticker_that_is_not_a_state_company_has_no_detail(database: Engine) -> None:
    book = _book()
    _found(book)

    assert detail(book, "PETR4") is None


def test_the_founded_company_reports_its_shape_and_the_beta(database: Engine) -> None:
    book = _book()
    company = _found(book)

    result = detail(book)

    assert result is not None
    assert result.origin is StateCompanyOrigin.FOUNDED
    assert result.status is StateCompanyStatus.ACTIVE
    assert result.founded_on == FOUNDED_ON
    assert result.shares == company.shares
    assert result.government_share == company.government_share
    assert result.price == PRICE
    assert result.beta == D(str(reference.MARKET_BETA))
    assert result.fair_value == book.offer_price(company, TODAY)


def test_the_first_month_is_the_founding_with_the_invested_capital(
    database: Engine,
) -> None:
    book = _book()
    company = _found(book)

    [founding] = months_of(book, FOUNDED_ON)

    assert founding.reason is StateMonthReason.FOUNDING
    assert founding.month == date(2022, 4, 1)
    assert founding.fair_value == (company.invested / company.shares).quantize(PLACES)
    assert founding.profit is None
    assert founding.dividend is None
    assert founding.dividend_policy is None


def test_a_closed_month_shows_profit_and_dividend_per_share(database: Engine) -> None:
    book = _book()
    company = _found(book)
    [row] = book.on_month(date(2022, 5, 31))

    founding, paid = months_of(book, date(2022, 6, 1))

    assert founding.reason is StateMonthReason.FOUNDING
    assert paid.reason is StateMonthReason.PAID
    assert paid.month == date(2022, 5, 1)
    assert paid.profit == (row.profit / company.shares).quantize(PLACES)
    # O dividendo por ação é o do Tesouro dividido pela fatia do governo e pelas ações
    expected = row.treasury_dividend / company.government_share / company.shares
    assert paid.dividend == expected.quantize(PLACES)
    assert paid.payout is not None
    assert paid.dividend_policy is not None


def test_the_total_dividends_add_up_the_months(database: Engine) -> None:
    book = _book()
    _found(book)
    book.on_month(date(2022, 5, 31))
    book.on_month(date(2022, 6, 30))

    result = detail(book, today=date(2022, 7, 1))

    assert result is not None
    assert result.dividends == sum(
        (m.dividend for m in result.months if m.dividend is not None), D(0)
    )
    assert result.dividends > 0


def test_the_detail_lists_each_policy_with_its_payout(database: Engine) -> None:
    book = _book()
    _found(book)

    result = detail(book, today=date(2022, 5, 2))

    assert result is not None
    assert {(p.dividend_policy, p.payout) for p in result.policies} == set(
        payout.PAYOUT.items()
    )


def test_a_loss_month_has_no_dividend(database: Engine) -> None:
    book = _book()
    company = _found(book)
    # Mês de prejuízo gravado: o valor justo ficou abaixo do capital
    repository.state_company.save_month(
        StateCompanyMonthDTO(
            state_company_id=company.id,
            month=date(2022, 5, 1),
            fair_value=company.invested * D("0.9"),
            profit=-company.invested * D("0.1"),
            treasury_dividend=D(0),
        )
    )

    _, loss = months_of(book, date(2022, 6, 1))

    assert loss.reason is StateMonthReason.LOSS
    assert loss.profit is not None
    assert loss.profit < 0
    assert loss.dividend == 0


def test_the_sold_company_closes_with_the_privatization_month(
    database: Engine,
) -> None:
    book = _book()
    company = _found(book)
    book.on_month(date(2022, 5, 31))
    book._companies["PNOV3"] = company.model_copy(
        update={
            "status": StateCompanyStatus.PRIVATIZED,
            "privatized_on": date(2022, 6, 10),
        }
    )

    result = detail(book, today=date(2022, 8, 10))

    assert result is not None
    assert result.government_share == 0
    assert result.fair_value is None
    assert [m.reason for m in result.months] == [
        StateMonthReason.FOUNDING,
        StateMonthReason.PAID,
        StateMonthReason.PRIVATIZED,
    ]
    assert result.holders is not None
    assert result.holders.government == 0


def test_the_imported_company_has_no_months_holders_or_beta(database: Engine) -> None:
    book = _imported_book()
    [company] = book.companies()

    result = detail(book, company.ticker)

    assert result is not None
    assert result.origin is StateCompanyOrigin.IMPORTED
    assert result.months == []
    assert result.holders is None
    assert result.beta is None
    assert result.fair_value is None


def _portfolio(simulation_id: int, *, bot: bool | None) -> int:
    """A carteira de um jogador (bot ou não) ou, com `bot=None`, a de gestora sem dono."""
    user_id = None
    if bot is not None:
        user_id = repository.user.create_user(
            uuid.uuid4(), f"user-{uuid.uuid4().hex[:6]}", is_bot=bot
        ).id
    with transactional_method.get_session_factory()() as session, session.begin():
        portfolio = Portfolios(
            simulation_id=simulation_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
            starting_cash=D(0),
        )
        session.add(portfolio)
        session.flush()
        return portfolio.id


def _trade(
    simulation_id: int,
    portfolio_id: int,
    quantity: int,
    kind: EquityEventType = EquityEventType.BUY,
) -> None:
    repository.event.insert_many(
        [
            EquityEventDTO(
                simulation_id=simulation_id,
                event_date=date(2022, 6, 1),
                portfolio_id=portfolio_id,
                ticker="PNOV3",
                event_type=kind,
                quantity=D(quantity),
                price=D(10),
            )
        ]
    )


def test_the_holders_separate_you_players_bots_and_funds(database: Engine) -> None:
    book = _book()
    company = _found(book)
    sim = book._simulation_id
    you = _portfolio(sim, bot=False)
    other = _portfolio(sim, bot=False)
    robot = _portfolio(sim, bot=True)
    fund = _portfolio(sim, bot=None)
    _trade(sim, you, 30)
    _trade(sim, other, 20)
    _trade(sim, robot, 10)
    _trade(sim, robot, 4, EquityEventType.SELL)
    _trade(sim, fund, 5)

    result = detail(book, portfolio_id=you)

    assert result is not None
    assert result.holders is not None
    holders = result.holders
    assert (holders.you, holders.players, holders.bots, holders.funds) == (
        D(30),
        D(20),
        D(6),
        D(5),
    )
    assert holders.government == government_shares(company)
    assert holders.maker == MAKER_STOCK


def test_a_viewer_without_portfolio_holds_nothing(database: Engine) -> None:
    book = _book()
    _found(book)
    sim = book._simulation_id
    _trade(sim, _portfolio(sim, bot=False), 12)

    result = detail(book, portfolio_id=None)

    assert result is not None
    assert result.holders is not None
    assert result.holders.you == 0
    assert result.holders.players == 12


def _client(simulation: Simulation, user: UserDTO) -> TestClient:
    app = FastAPI()
    app.include_router(operation_router)
    app.dependency_overrides[get_active_simulation] = lambda: simulation
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def _simulation(government: object) -> Simulation:
    simulation = object.__new__(Simulation)
    simulation._engine = SimpleNamespace(_lock=threading.RLock())  # type: ignore[assignment]
    simulation._government = government  # type: ignore[assignment]
    simulation._current_date = TODAY
    return simulation


USER = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana", is_bot=False)
URL = "/api/variable-income/PNOV3/state-company"


def test_the_route_returns_null_when_the_match_has_no_government() -> None:
    response = _client(_simulation(None), USER).get(URL)

    assert response.status_code == 200
    assert response.json() is None


def test_the_route_serves_the_detail_of_the_ticker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asked: list[tuple[date, str, int | None]] = []

    def state_detail(today: date, ticker: str, portfolio_id: int | None):
        asked.append((today, ticker, portfolio_id))
        return StateCompanyDetailDTO(
            ticker=ticker,
            origin=StateCompanyOrigin.FOUNDED,
            status=StateCompanyStatus.ACTIVE,
            founded_on=None,
            size=None,
            government_share=D("0.51"),
            shares=1000,
            price=D("12.50"),
            fair_value=None,
            dividends=D(0),
            dividend_policy=DividendPolicy.NORMAL,
            policies=[],
            beta=None,
            months=[],
            holders=None,
        )

    monkeypatch.setattr(SimulationManager, "get_portfolio_id", lambda _user_id: 9)

    response = _client(
        _simulation(SimpleNamespace(state_detail=state_detail)), USER
    ).get(URL)

    assert response.status_code == 200
    body = response.json()
    assert (body["ticker"], body["origin"], body["price"]) == (
        "PNOV3",
        "FOUNDED",
        "12.50",
    )
    assert asked == [(TODAY, "PNOV3", 9)]


def test_the_route_serves_the_viewer_without_portfolio(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def no_portfolio(_user_id: int) -> int:
        raise NotFoundError("sem carteira")

    monkeypatch.setattr(SimulationManager, "get_portfolio_id", no_portfolio)
    government = SimpleNamespace(state_detail=lambda *_: None)

    response = _client(_simulation(government), USER).get(URL)

    assert response.status_code == 200
    assert response.json() is None
