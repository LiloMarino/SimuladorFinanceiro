"""As manchetes das estatais: cada fato sai uma vez, no dia certo, com o ticker e o partido do presidente."""

# As fixtures do livro vêm dos módulos dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from backend.core.enum import (
    DividendPolicy,
    NewsType,
    StateCompanySize,
    StateControl,
    StateLever,
)
from backend.features.government.government_book import GovernmentBook
from backend.features.notifications.news import Headline
from tests.test_government_book import (
    FIRST_VOTE,
    TERM_START,
    USERS,
    book,
    close_months,
    congress_says,
    engine,
    govern,
    headlines,
    hold_vote_day,
    market,
    notices,
    office,
    stored,
)
from tests.test_government_state_orders import (
    ENERGY,
    FUEL,
    company,
    computer_takes_office,
    new_state_book,
    order,
    state_book,
)
from tests.test_state_company_measures import (
    approve_first,
    found_company,
    match,
    privatize,
)

# A sigla do partido que o presidente do `govern` funda
PARTY = "AAA"
HeadlineLog = list[tuple[date, Headline]]


def of_type(log: HeadlineLog, news_type: NewsType) -> list[tuple[date, Headline]]:
    return [(day, h) for day, h in log if h.news_type is news_type]


@pytest.fixture
def last_price(engine) -> None:
    """A bolsa cota a ação importada, que é o preço da oferta de privatização."""
    engine.matching_engine = SimpleNamespace(
        market_data=SimpleNamespace(
            get_last=lambda _ticker: SimpleNamespace(close=20.0)
        )
    )


# Fundação


def test_the_foundation_headline_comes_once_on_the_effective_day(
    book: GovernmentBook, engine, market, match, monkeypatch, headlines: HeadlineLog
):
    govern(book, engine)
    found_company(book)
    effective = approve_first(book, monkeypatch)
    book.on_tick(USERS, effective - timedelta(days=1), False)
    assert of_type(headlines, NewsType.STATE_COMPANY_FOUNDED) == []

    book.on_tick(USERS, effective, False)
    book.on_tick(USERS, effective + timedelta(days=1), False)

    [(day, news)] = of_type(headlines, NewsType.STATE_COMPANY_FOUNDED)
    assert day == effective
    assert news.tickers == ("PNOV3",)
    assert news.party_abbrs == (PARTY,)
    assert "Petro Nova" in news.text


def test_the_in_force_headline_of_a_state_measure_is_the_specific_one(
    book: GovernmentBook, engine, market, match, monkeypatch, headlines: HeadlineLog
):
    govern(book, engine)
    found_company(book)
    effective = approve_first(book, monkeypatch)
    voted = of_type(headlines, NewsType.MEASURE_VOTED)

    book.on_tick(USERS, effective, False)

    assert of_type(headlines, NewsType.MEASURE_VOTED) == voted


# Privatização


def test_the_privatization_opens_and_closes_with_one_headline_each(
    engine,
    stored,
    notices,
    captured_events,
    office,
    headlines: HeadlineLog,
    market,
    match,
    last_price,
    monkeypatch,
):
    book = new_state_book(engine, office, headlines, [company(FUEL, StateLever.FUEL)])
    govern(book, engine)
    privatize(book, FUEL)
    effective = approve_first(book, monkeypatch)

    book.on_tick(USERS, effective, False)
    book.on_tick(USERS, effective + timedelta(days=1), False)

    [(opened_day, opened)] = of_type(headlines, NewsType.STATE_PRIVATIZATION_OPENED)
    assert opened_day == effective
    assert opened.tickers == (FUEL,)
    assert opened.party_abbrs == (PARTY,)
    assert of_type(headlines, NewsType.STATE_PRIVATIZATION_CLOSED) == []

    ends_on = book.state_companies().offer_ends_on(FUEL)
    assert ends_on is not None
    book.close_state_market(ends_on)
    book.close_state_market(ends_on)

    [(closed_day, closed)] = of_type(headlines, NewsType.STATE_PRIVATIZATION_CLOSED)
    assert closed_day == ends_on
    assert closed.tickers == (FUEL,)
    assert closed.party_abbrs == (PARTY,)


# Ordens: controle em vigor, soltura e política


def test_the_control_headline_comes_when_the_order_enters_into_force(
    state_book: GovernmentBook, engine, market, headlines: HeadlineLog
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    assert of_type(headlines, NewsType.STATE_CONTROL_IN_FORCE) == []

    close_months(state_book, 1)
    close_months(state_book, 1, date(2022, 2, 28))

    [(_day, news)] = of_type(headlines, NewsType.STATE_CONTROL_IN_FORCE)
    assert news.tickers == (FUEL,)
    assert news.party_abbrs == (PARTY,)
    assert "10%" in news.text
    assert of_type(headlines, NewsType.STATE_CONTROL_RELEASED) == []


def test_releasing_the_control_brings_the_held_inflation_back_in_one_headline(
    state_book: GovernmentBook, engine, market, headlines: HeadlineLog
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    close_months(state_book, 1)
    order(state_book, FUEL, StateControl.NONE)
    close_months(state_book, 1, date(2022, 2, 28))

    [(_day, news)] = of_type(headlines, NewsType.STATE_CONTROL_RELEASED)
    assert news.tickers == (FUEL,)
    assert news.party_abbrs == (PARTY,)
    assert "inflação represada volta" in news.text


def test_the_release_with_another_company_still_holding_does_not_bring_it_back(
    state_book: GovernmentBook, engine, market, headlines: HeadlineLog
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    order(state_book, ENERGY, StateControl.P5)
    close_months(state_book, 1)
    order(state_book, FUEL, StateControl.NONE)
    close_months(state_book, 1, date(2022, 2, 28))

    [(_day, news)] = of_type(headlines, NewsType.STATE_CONTROL_RELEASED)
    assert news.tickers == (FUEL,)
    assert "ainda não volta" in (news.dek or "")


def test_the_computer_takeover_releases_the_control_with_the_release_headline(
    state_book: GovernmentBook, engine, market, headlines: HeadlineLog
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    close_months(state_book, 1)
    assert of_type(headlines, NewsType.STATE_CONTROL_RELEASED) == []

    day = date(2022, 3, 1)
    computer_takes_office(state_book, day)
    state_book.on_tick(USERS, day, False)
    close_months(state_book, 1, date(2022, 2, 28))

    [(_day, news)] = of_type(headlines, NewsType.STATE_CONTROL_RELEASED)
    assert news.tickers == (FUEL,)


def test_the_dividend_policy_headline_comes_when_the_policy_enters_into_force(
    state_book: GovernmentBook, engine, market, headlines: HeadlineLog
):
    govern(state_book, engine)
    order(state_book, ENERGY, StateControl.NONE, DividendPolicy.SQUEEZE)
    assert of_type(headlines, NewsType.STATE_DIVIDEND_POLICY_CHANGED) == []

    close_months(state_book, 1)
    close_months(state_book, 1, date(2022, 2, 28))

    [(_day, news)] = of_type(headlines, NewsType.STATE_DIVIDEND_POLICY_CHANGED)
    assert news.tickers == (ENERGY,)
    assert news.party_abbrs == (PARTY,)
    assert "espremer" in news.text
    assert of_type(headlines, NewsType.STATE_CONTROL_IN_FORCE) == []


def test_an_order_equal_to_the_one_in_force_makes_no_headline(
    state_book: GovernmentBook, engine, market, headlines: HeadlineLog
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    close_months(state_book, 1)
    order(state_book, FUEL, StateControl.P10)
    close_months(state_book, 1, date(2022, 2, 28))
    close_months(state_book, 1, date(2022, 3, 31))

    assert len(of_type(headlines, NewsType.STATE_CONTROL_IN_FORCE)) == 1
