"""As ligações das estatais com a economia: IPCA, crédito e PIB, sempre nulas sem ordem e sem fundação."""

# A fixture das séries vem do módulo dos testes da economia interligada
# ruff: noqa: F401, F811

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import (
    DividendPolicy,
    InitialAccount,
    StateCompanySize,
    StateControl,
    StateLever,
)
from backend.features.economy.growth import MacroCourse
from backend.features.economy.links import link_month
from backend.features.economy.monetary import SelicBoard
from backend.features.government import budget
from backend.features.government.budget import base_spending_on
from backend.features.government.linked_economy import (
    NO_STATE_FEED,
    LinkedEconomy,
    StateFeed,
)
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.state_companies import gdp, levers
from backend.features.state_companies.book import StateCompanyBook, invested_by
from backend.features.state_companies.orders import StateOrder
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.fakes import simulation_settings
from tests.test_linked_economy import SIMULATION, START, stored_series

D = Decimal
ZERO = D(0)
FOUNDED_ON = date(2022, 4, 15)
JUNE = date(2022, 6, 1)
JULY = date(2022, 7, 1)
AUGUST = date(2022, 8, 1)
HOLD_P10 = StateOrder(StateControl.P10, DividendPolicy.NORMAL)

type History = dict[date, dict[str, StateOrder]]


def _book(history: History | None = None) -> StateCompanyBook:
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    orders = history if history is not None else {}
    return StateCompanyBook(simulation_id, 7, lambda: orders)


def _found(
    book: StateCompanyBook,
    ticker: str = "PNOV3",
    lever: StateLever | None = StateLever.FUEL,
    size: StateCompanySize = StateCompanySize.SMALL,
):
    company = book.found(
        ticker=ticker,
        name="Petro Nova",
        size=size,
        lever=lever,
        real_interest=D("0.05"),
        today=FOUNDED_ON,
    )
    assert company is not None
    return company


def _economy(feed: StateFeed = NO_STATE_FEED) -> LinkedEconomy:
    return LinkedEconomy(
        SIMULATION,
        START,
        MacroCourse(START),
        budget.initial_account(START, InitialAccount.PLAYABLE),
        lambda _day: DEFAULT_TAX_POLICY,
        base_spending_on,
        lambda _day: D(0),
        SpendingEconomy(),
        SelicBoard(),
        feed,
    )


def _month_link(
    state_inflation_points: Decimal = ZERO,
    state_credit_points: Decimal = ZERO,
    state_gdp_push: Decimal = ZERO,
):
    return link_month(
        None,
        date(2022, 6, 30),
        unemployment_gap=D(0),
        premium_gap=D(0),
        growth_gap=D(0),
        primary_gap=D(0),
        primary_gap_year_ago=D(0),
        state_inflation_points=state_inflation_points,
        state_credit_points=state_credit_points,
        state_gdp_push=state_gdp_push,
    )


def test_without_an_order_the_state_link_is_zero(database: Engine) -> None:
    book = _book()
    _found(book)

    link = _month_link(
        state_inflation_points=book.inflation_points(JUNE),
        state_credit_points=book.credit_points(JUNE),
        state_gdp_push=D(0),
    )

    assert link.is_zero
    assert link.inflation_points == 0
    assert link.credit_premium == 0


def test_an_economy_fed_with_zeros_is_the_history(stored_series: None) -> None:
    zeros = replace(
        NO_STATE_FEED,
        spending_on=lambda _day: D(0),
        assets_on=lambda _day: D(0),
        inflation_on=lambda _day: D(0),
        credit_on=lambda _day: D(0),
        gdp_push_on=lambda _day: D(0),
    )
    fed, plain = _economy(zeros), _economy()
    end = date(2022, 12, 31)

    fed.close_until(end)
    plain.close_until(end)

    assert fed.links_until(end) == plain.links_until(end)
    assert all(link.is_zero for link in fed.links_until(end))
    assert fed.budget.latest(end).debt == plain.budget.latest(end).debt


def test_fuel_control_holds_the_ipca_and_the_release_returns_the_whole_backlog(
    database: Engine,
) -> None:
    book = _book({JUNE: {"PNOV3": HOLD_P10}, JULY: {"PNOV3": HOLD_P10}, AUGUST: {}})
    _found(book)

    june, july = book.inflation_points(JUNE), book.inflation_points(JULY)
    released = book.inflation_points(AUGUST)

    assert june < 0
    assert july < 0
    assert released == -(june + july)
    held = _month_link(state_inflation_points=june)
    assert held.inflation_points == float(june)
    assert _month_link(state_inflation_points=released).inflation_points > 0


def test_the_bank_moves_credit_and_leaves_the_ipca(database: Engine) -> None:
    order = StateOrder(StateControl.P20, DividendPolicy.NORMAL)
    book = _book({JUNE: {"BBAS3": order}})
    _found(book, ticker="BBAS3", lever=StateLever.BANK)

    points = book.credit_points(JUNE)
    link = _month_link(
        state_inflation_points=book.inflation_points(JUNE),
        state_credit_points=points,
    )

    assert book.inflation_points(JUNE) == 0
    assert points == levers.credit_points(StateLever.BANK, StateControl.P20)
    assert points > 0
    assert link.inflation_points == 0
    assert link.credit_premium == -points / 100


def test_fuel_control_does_not_touch_credit(database: Engine) -> None:
    book = _book({JUNE: {"PNOV3": HOLD_P10}})
    _found(book)

    assert book.credit_points(JUNE) == 0


def test_the_founding_is_spent_in_twelve_installments_from_the_effect_month(
    database: Engine,
) -> None:
    book = _book()
    company = _found(book, size=StateCompanySize.MEDIUM)
    installment = invested_by(StateCompanySize.MEDIUM) / gdp.FOUNDING_MONTHS

    assert book.founding_spending(date(2022, 3, 1)) == 0
    months = [date(2022 + (3 + i) // 12, (3 + i) % 12 + 1, 1) for i in range(12)]
    assert all(book.founding_spending(month) == installment for month in months)
    assert book.founding_spending(date(2023, 4, 1)) == 0
    total = sum((book.founding_spending(month) for month in months), D(0))
    assert abs(company.invested - total) < 1


def test_the_founding_enters_the_fiscal_impulse(stored_series: None) -> None:
    invested = invested_by(StateCompanySize.LARGE)
    first = date(2020, 5, 1)

    def spending(day: date) -> Decimal:
        elapsed = (day.year - first.year) * 12 + day.month - first.month
        return gdp.founding_installment(invested) if 0 <= elapsed < 12 else D(0)

    founded = _economy(replace(NO_STATE_FEED, spending_on=spending))
    plain = _economy()
    end = date(2022, 12, 31)
    founded.close_until(end)
    plain.close_until(end)

    impulse = {link.month_end: link.impulse for link in founded.links_until(end)}
    assert impulse[date(2020, 12, 31)] > 0
    assert impulse[end] == 0
    assert founded.budget.latest(date(2020, 12, 31)).state_spending > 0
    assert plain.budget.latest(date(2020, 12, 31)).state_spending == 0
    assert founded.budget.latest(end).state_spending == 0


def test_state_dividends_stay_out_of_the_impulse(stored_series: None) -> None:
    paying = _economy(replace(NO_STATE_FEED, dividends_on=lambda _day: D(10) ** 9))
    plain = _economy()
    end = date(2021, 12, 31)
    paying.close_until(end)
    plain.close_until(end)

    assert all(link.impulse == 0 for link in paying.links_until(end))
    assert paying.budget.latest(end).debt < plain.budget.latest(end).debt


def test_the_permanent_push_grows_with_the_founded_size(database: Engine) -> None:
    book = _book()
    assert book.gdp_push(JULY) == 0

    _found(book, size=StateCompanySize.SMALL)
    small = book.gdp_push(JULY)
    _found(book, ticker="OTRO3", lever=StateLever.ENERGY, size=StateCompanySize.LARGE)

    assert small > 0
    assert book.gdp_push(JULY) > small


def test_squeezing_the_dividend_lowers_the_push_and_reinvesting_raises_it(
    database: Engine,
) -> None:
    history: History = {}
    book = _book(history)
    _found(book)

    def push(policy: DividendPolicy) -> Decimal:
        history[JUNE] = {"PNOV3": StateOrder(StateControl.NONE, policy)}
        return book.gdp_push(date(2023, 6, 1))

    assert push(DividendPolicy.SQUEEZE) < push(DividendPolicy.NORMAL)
    assert push(DividendPolicy.REINVEST) > push(DividendPolicy.NORMAL)
