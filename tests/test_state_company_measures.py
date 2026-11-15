"""Medidas de fundar e privatizar estatal no livro do governo: validação, título, voto, vigência, prévia e retomada."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import (
    AssetClass,
    MeasureKind,
    MeasureStatus,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateLever,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.utils import required
from backend.features.government import governance, promises
from backend.features.government import measures as rules
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from backend.features.state_companies.book import FOUNDING_GOVERNMENT_SHARE, invested_by
from tests.fakes import simulation_settings
from tests.test_government_book import (
    ALICE,
    FIRST_VOTE,
    SEED,
    TERM_START,
    USERS,
    book,
    congress_says,
    engine,
    govern,
    headlines,
    hold_vote_day,
    market,
    notices,
    office,
    settings,
    stored,
)
from tests.test_government_state_orders import company, new_state_book

FOUND = MeasureKind.FOUND_STATE_COMPANY
PRIVATIZE = MeasureKind.PRIVATIZE_STATE_COMPANY
SMALL = StateCompanySize.SMALL
D = Decimal


@pytest.fixture(autouse=True)
def no_frozen_portfolio(monkeypatch: pytest.MonkeyPatch) -> None:
    """O motor de teste não monta carteira; o painel aqui é só da medida."""
    monkeypatch.setattr(governance, "_portfolio", lambda *_: None)


@pytest.fixture
def match(database: Engine) -> int:
    """A partida no banco: as estatais fundadas guardam o id dela."""
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    assert simulation_id == settings().id
    return simulation_id


def found_company(
    book: GovernmentBook,
    ticker: str = "PNOV3",
    name: str = "Petro Nova",
    size: StateCompanySize | None = SMALL,
    lever: StateLever | None = StateLever.FUEL,
) -> None:
    book.propose(ALICE, TERM_START, FOUND, None, None, None, name, ticker, size, lever)


def privatize(book: GovernmentBook, ticker: str) -> None:
    book.propose(ALICE, TERM_START, PRIVATIZE, None, None, None, ticker=ticker)


def approve_first(book: GovernmentBook, monkeypatch) -> date:
    """Aprova a primeira medida da fila no voto de janeiro e devolve o dia em que ela vale."""
    congress_says(monkeypatch, True)
    hold_vote_day(book)
    effective = book.state.measures[1].effective
    assert effective is not None
    return effective


# Fundar: validação e título


def test_founding_queues_the_measure_with_name_ticker_size_and_lever(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    found_company(book)

    [queued] = book.state.measures.values()
    assert queued.status is MeasureStatus.QUEUED
    assert (queued.name, queued.ticker, queued.size, queued.lever) == (
        "Petro Nova",
        "PNOV3",
        SMALL,
        StateLever.FUEL,
    )
    assert queued.value is None


def test_the_titles_name_the_company_and_the_ticker(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    found_company(book)

    assert rules.title(book.state.measures[1]) == "Fundar a Petro Nova (PNOV3)"


@pytest.mark.parametrize("ticker", ["PNOV", "PNO3", "pnov3", "PNOV33", "PNOVA", None])
def test_the_ticker_is_four_letters_and_one_digit(
    book: GovernmentBook, engine, market, match, ticker
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        found_company(book, ticker=ticker)


def test_founding_asks_for_a_name_and_a_size(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        found_company(book, name="")
    with pytest.raises(UnprocessableEntityError):
        found_company(book, size=None)


def test_a_ticker_whose_letters_belong_to_another_asset_is_taken(
    book: GovernmentBook, engine, market, match
):
    repository.stock.add_stock("PETR4", "Petrobras", AssetClass.STOCK)
    govern(book, engine)

    with pytest.raises(ConflictError):
        found_company(book, ticker="PETR3")


def test_two_foundations_cannot_share_the_letters_while_one_is_pending(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    found_company(book, ticker="PNOV3")

    with pytest.raises(ConflictError):
        found_company(book, ticker="PNOV4")
    found_company(book, ticker="ABCD3")

    assert len(book.state.measures) == 2


def test_a_measure_that_is_not_of_a_state_company_takes_no_ticker(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        book.propose(
            ALICE,
            TERM_START,
            MeasureKind.WELFARE_SPENDING,
            D("0.02"),
            None,
            None,
            ticker="PNOV3",
        )


def test_a_state_company_measure_takes_no_value_or_sector(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        book.propose(
            ALICE,
            TERM_START,
            FOUND,
            D("0.02"),
            None,
            None,
            "Petro Nova",
            "PNOV3",
            SMALL,
        )


# Privatizar: validação e título


def test_privatizing_takes_an_active_company_of_the_government(
    engine, stored, notices, captured_events, office, headlines, market, match
):
    state_book = new_state_book(
        engine,
        office,
        headlines,
        [company("PETR4", StateLever.FUEL)],
    )
    govern(state_book, engine)

    privatize(state_book, "PETR4")

    assert rules.title(state_book.state.measures[1]) == "Privatizar a PETR4"
    with pytest.raises(ConflictError):
        privatize(state_book, "PETR4")


def test_privatizing_an_unknown_or_privatizing_company_is_refused(
    engine, stored, notices, captured_events, office, headlines, market, match
):
    state_book = new_state_book(
        engine,
        office,
        headlines,
        [company("PETR4", StateLever.FUEL, StateCompanyStatus.PRIVATIZING)],
    )
    govern(state_book, engine)

    with pytest.raises(ConflictError):
        privatize(state_book, "PETR4")
    with pytest.raises(ConflictError):
        privatize(state_book, "ZZZZ3")


def test_privatizing_takes_only_the_ticker(
    engine, stored, notices, captured_events, office, headlines, market, match
):
    state_book = new_state_book(
        engine, office, headlines, [company("PETR4", StateLever.FUEL)]
    )
    govern(state_book, engine)

    with pytest.raises(UnprocessableEntityError):
        state_book.propose(
            ALICE, TERM_START, PRIVATIZE, None, None, None, "Outro nome", "PETR4"
        )
    with pytest.raises(UnprocessableEntityError):
        state_book.propose(
            ALICE, TERM_START, PRIVATIZE, None, None, None, ticker="PETR4", size=SMALL
        )


# Voto e vigência


def test_an_approved_foundation_creates_the_company_ninety_days_after_the_vote(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    found_company(book)

    effective = approve_first(book, monkeypatch)

    assert effective == FIRST_VOTE + timedelta(days=90)
    assert book.state_companies().company("PNOV3") is None
    book.on_tick(USERS, effective - timedelta(days=1), False)
    assert book.state_companies().company("PNOV3") is None

    book.on_tick(USERS, effective, False)

    created = required(book.state_companies().company("PNOV3"))
    assert created.origin is StateCompanyOrigin.FOUNDED
    assert created.status is StateCompanyStatus.ACTIVE
    assert created.government_share == FOUNDING_GOVERNMENT_SHARE
    assert created.invested == invested_by(SMALL)
    assert created.founded_on == effective
    assert created.lever is StateLever.FUEL
    assert repository.state_company.of_simulation(match) == [created]


def test_the_foundation_happens_once(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    found_company(book)
    effective = approve_first(book, monkeypatch)

    book.on_tick(USERS, effective, False)
    book.on_tick(USERS, effective + timedelta(days=1), False)

    assert len(book.state_companies().companies()) == 1
    assert len(repository.state_company.of_simulation(match)) == 1


def test_a_rejected_foundation_creates_nothing(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    found_company(book)
    congress_says(monkeypatch, False)

    hold_vote_day(book)
    book.on_tick(USERS, FIRST_VOTE + timedelta(days=120), False)

    assert book.state.measures[1].status is MeasureStatus.REJECTED
    assert book.state_companies().companies() == []
    assert repository.state_company.of_simulation(match) == []


def test_an_approved_privatization_opens_the_offer_on_the_effective_day(
    engine,
    stored,
    notices,
    captured_events,
    office,
    headlines,
    market,
    match,
    monkeypatch,
):
    state_book = new_state_book(
        engine, office, headlines, [company("PETR4", StateLever.FUEL)]
    )
    govern(state_book, engine)
    privatize(state_book, "PETR4")

    effective = approve_first(state_book, monkeypatch)
    state_book.on_tick(USERS, effective - timedelta(days=1), False)
    assert (
        required(state_book.state_companies().company("PETR4")).status
        is StateCompanyStatus.ACTIVE
    )

    state_book.on_tick(USERS, effective, False)

    opened = required(state_book.state_companies().company("PETR4"))
    assert opened.status is StateCompanyStatus.PRIVATIZING
    assert opened.offer_opened_on == effective


# Prévia


def test_the_foundation_preview_charges_the_capital_to_the_debt(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    preview = book.preview(
        ALICE, TERM_START, FOUND, None, None, None, "Petro Nova", "PNOV3", SMALL
    )

    assert preview.title == "Fundar a Petro Nova (PNOV3)"
    assert preview.budget.debt_after > preview.budget.debt_before
    assert preview.budget.revenue_change == 0
    assert preview.budget.spending_change == 0
    assert preview.inflation is None


def test_the_preview_of_a_bigger_size_charges_more(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    def extra(size: StateCompanySize) -> Decimal:
        budget = book.preview(
            ALICE, TERM_START, FOUND, None, None, None, "Petro Nova", "PNOV3", size
        ).budget
        return budget.debt_after - budget.debt_before

    assert extra(StateCompanySize.LARGE) > extra(StateCompanySize.SMALL)


def test_the_privatization_preview_adds_no_debt(
    engine, stored, notices, captured_events, office, headlines, market, match
):
    state_book = new_state_book(
        engine, office, headlines, [company("PETR4", StateLever.FUEL)]
    )
    govern(state_book, engine)

    budget = state_book.preview(
        ALICE, TERM_START, PRIVATIZE, None, None, None, ticker="PETR4"
    ).budget

    assert budget.debt_after == budget.debt_before


# Governo do computador e retomada


def test_the_computer_government_never_proposes_these_measures():
    assert FOUND not in promises.GENERAL_KINDS
    assert PRIVATIZE not in promises.GENERAL_KINDS


def test_replay_rebuilds_the_ticker_size_and_lever_of_the_measure(
    book: GovernmentBook, engine, market, match, stored
):
    govern(book, engine)
    found_company(book)

    rebuilt = replay(stored).measures[1]

    original = book.state.measures[1]
    assert (rebuilt.name, rebuilt.ticker, rebuilt.size, rebuilt.lever) == (
        original.name,
        original.ticker,
        original.size,
        original.lever,
    )
    assert rebuilt.kind is FOUND


def test_a_resumed_game_keeps_the_foundation_it_already_made(
    book: GovernmentBook, engine, market, match, monkeypatch, stored, office, headlines
):
    govern(book, engine)
    found_company(book)
    effective = approve_first(book, monkeypatch)
    book.on_tick(USERS, effective, False)
    created = required(book.state_companies().company("PNOV3"))

    # A retomada relê os eventos e as empresas do banco, e o dia seguinte não funda outra
    resumed = new_state_book(
        engine, office, headlines, repository.state_company.of_simulation(match)
    )
    resumed.on_tick(USERS, effective + timedelta(days=1), False)

    assert resumed.state_companies().company("PNOV3") == created
    assert len(repository.state_company.of_simulation(match)) == 1
