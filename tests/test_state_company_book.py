"""O livro das estatais: fundação, oferta de privatização, fechamento do mês e efeito das ordens no IPCA."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import (
    AssetClass,
    DividendPolicy,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
)
from backend.features.state_companies import fair_value, levers, payout
from backend.features.state_companies.book import (
    FOUNDING_GOVERNMENT_SHARE,
    FOUNDING_PRICE,
    StateCompanyBook,
    invested_by,
    maker_shares,
)
from backend.features.state_companies.orders import StateOrder
from tests.fakes import simulation_settings

FOUNDED_ON = date(2022, 4, 15)
REAL_INTEREST = Decimal("0.05")
CENTS = Decimal("0.000001")

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
        real_interest=REAL_INTEREST,
        today=FOUNDED_ON,
    )
    assert company is not None
    return company


def test_founding_creates_the_stock_and_the_active_company(database: Engine) -> None:
    book = _book()

    company = _found(book)

    stock = repository.stock.get_by_ticker("PNOV3")
    assert stock is not None
    assert stock.asset_class is AssetClass.STOCK
    assert company.origin is StateCompanyOrigin.FOUNDED
    assert company.status is StateCompanyStatus.ACTIVE
    assert company.government_share == FOUNDING_GOVERNMENT_SHARE
    assert company.founded_on == FOUNDED_ON
    assert company.lever is StateLever.FUEL
    assert book.company("PNOV3") == company


def test_founding_invests_the_size_and_splits_the_shares(database: Engine) -> None:
    book = _book()

    company = _found(book, size=StateCompanySize.SMALL)

    assert company.invested == invested_by(StateCompanySize.SMALL)
    # O capital dividido pelo preço de lançamento dá o total de ações
    assert company.shares == int(company.invested / FOUNDING_PRICE)
    assert maker_shares(company) == company.shares - int(
        company.shares * Decimal("0.51")
    )
    assert company.mean_return == fair_value.mean_annual_return(REAL_INTEREST)


def test_the_repository_gives_the_company_back_to_the_match(database: Engine) -> None:
    book = _book()
    company = _found(book)

    stored = repository.state_company.of_simulation(book._simulation_id)

    assert stored == [company]


def test_founding_on_taken_letters_returns_none(database: Engine) -> None:
    repository.stock.add_stock("PETR4", "Petrobras", AssetClass.STOCK)
    book = _book()

    company = book.found(
        ticker="PETR3",
        name="Outra",
        size=StateCompanySize.SMALL,
        lever=None,
        real_interest=REAL_INTEREST,
        today=FOUNDED_ON,
    )

    assert company is None
    assert book.companies() == []


def test_ticker_is_free_until_the_match_founds_it(database: Engine) -> None:
    book = _book()
    assert book.ticker_free("PNOV3")

    _found(book)

    assert not book.ticker_free("PNOV3")
    assert not book.ticker_free("PNOV4")


def test_ticker_is_not_free_when_the_letters_belong_to_another_asset(
    database: Engine,
) -> None:
    repository.stock.add_stock("PETR4", "Petrobras", AssetClass.STOCK)

    assert not _book().ticker_free("PETR3")


def test_opening_the_privatization_marks_the_company_and_the_day(
    database: Engine,
) -> None:
    book = _book()
    _found(book)

    opened = book.open_privatization("PNOV3", date(2022, 8, 1))

    assert opened.status is StateCompanyStatus.PRIVATIZING
    assert opened.offer_opened_on == date(2022, 8, 1)
    assert book.company("PNOV3") == opened
    [stored] = repository.state_company.of_simulation(book._simulation_id)
    assert stored.status is StateCompanyStatus.PRIVATIZING
    assert stored.offer_opened_on == date(2022, 8, 1)


def test_the_month_closes_with_fair_value_and_profit(database: Engine) -> None:
    book = _book()
    company = _found(book)

    [row] = book.on_month(date(2022, 5, 31))

    assert row.month == date(2022, 5, 1)
    assert company.mean_return is not None and company.seed is not None
    after = fair_value.fair_value(
        company.invested, company.seed, company.mean_return, 1
    )
    assert row.fair_value == after
    # O lucro do mês é o quanto o valor justo andou nele
    assert row.profit == after - company.invested
    # O banco guarda seis casas decimais
    [saved] = repository.state_company.months_of(company.id)
    assert saved.fair_value == row.fair_value.quantize(CENTS)
    assert saved.profit == row.profit.quantize(CENTS)


def test_the_month_of_the_founding_itself_does_not_close(database: Engine) -> None:
    book = _book()
    company = _found(book)

    assert book.on_month(date(2022, 4, 30)) == []
    assert repository.state_company.months_of(company.id) == []


def test_the_treasury_dividend_follows_the_order_in_force(database: Engine) -> None:
    month = date(2022, 5, 1)
    order = StateOrder(StateControl.P10, DividendPolicy.SQUEEZE)
    book = _book({month: {"PNOV3": order}})
    _found(book)

    [row] = book.on_month(date(2022, 5, 31))

    # O Tesouro recebe a fatia do governo no dividendo da política, depois do corte do controle
    expected = payout.dividend(
        max(row.profit, Decimal(0)), order.dividend_policy, order.control
    )
    assert row.treasury_dividend == expected * FOUNDING_GOVERNMENT_SHARE


def test_the_closed_company_month_is_rewritten_not_duplicated(
    database: Engine,
) -> None:
    book = _book()
    company = _found(book)

    book.on_month(date(2022, 6, 30))
    book.on_month(date(2022, 6, 30))

    assert len(repository.state_company.months_of(company.id)) == 1


def test_a_privatized_company_stops_closing_months(database: Engine) -> None:
    book = _book()
    company = _found(book)
    book._companies["PNOV3"] = company.model_copy(
        update={
            "status": StateCompanyStatus.PRIVATIZED,
            "privatized_on": date(2022, 6, 10),
        }
    )

    assert book.on_month(date(2022, 6, 30)) == []


def test_without_history_there_are_no_orders_and_no_inflation_effect(
    database: Engine,
) -> None:
    book = _book()
    _found(book)

    assert book.orders(date(2022, 6, 1)) == {}
    assert book.latest_orders() == {}
    assert book.inflation_points(date(2022, 6, 1)) == 0
    assert book.backlog(date(2022, 6, 1)) == 0


def test_the_orders_of_a_day_are_the_last_month_start_that_arrived(
    database: Engine,
) -> None:
    june = {"PNOV3": StateOrder(StateControl.P10, DividendPolicy.NORMAL)}
    july = {"PNOV3": StateOrder(StateControl.P20, DividendPolicy.NORMAL)}
    book = _book({date(2022, 6, 1): june, date(2022, 7, 1): july})

    assert book.orders(date(2022, 5, 31)) == {}
    assert book.orders(date(2022, 6, 20)) == june
    assert book.orders(date(2022, 7, 1)) == july
    assert book.latest_orders() == july


def test_the_held_price_lowers_the_ipca_and_the_release_returns_the_backlog(
    database: Engine,
) -> None:
    holding = {"PNOV3": StateOrder(StateControl.P10, DividendPolicy.NORMAL)}
    book = _book({date(2022, 6, 1): holding, date(2022, 7, 1): {}})
    _found(book)

    held = levers.held_points(StateLever.FUEL, StateControl.P10)
    assert book.held_points(date(2022, 6, 15)) == held
    assert book.inflation_points(date(2022, 6, 1)) < 0
    assert book.backlog(date(2022, 6, 15)) > 0
    # Sem ordem em julho, o mês solta o que o controle represou
    assert book.inflation_points(date(2022, 7, 1)) > 0


def test_other_points_leave_out_the_company_asked_about(database: Engine) -> None:
    book = _book()
    _found(book, ticker="PNOV3", lever=StateLever.FUEL)
    _found(book, ticker="ENER3", lever=StateLever.ENERGY)
    orders = {
        "PNOV3": StateOrder(StateControl.P10, DividendPolicy.NORMAL),
        "ENER3": StateOrder(StateControl.P10, DividendPolicy.NORMAL),
    }

    assert book.other_points("PNOV3", orders) == levers.held_points(
        StateLever.ENERGY, StateControl.P10
    )


@pytest.mark.parametrize("size", list(StateCompanySize))
def test_every_size_has_a_positive_investment(size: StateCompanySize) -> None:
    assert invested_by(size) > 0
