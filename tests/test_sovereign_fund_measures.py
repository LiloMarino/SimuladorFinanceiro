"""O aporte no Fundo Soberano como medida: validação, título, voto, vigência, prévia e retomada."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.enum import MeasureKind, MeasureStatus, SovereignFlowKind
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.features.government import measures as rules
from backend.features.government import promises
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from backend.features.sovereign_fund import rules as fund_rules
from tests.test_government_book import (
    ALICE,
    FIRST_VOTE,
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
from tests.test_state_company_measures import (
    approve_first,
    match,
    no_frozen_portfolio,
)

CONTRIBUTE = MeasureKind.CONTRIBUTE_SOVEREIGN_FUND
D = Decimal
BILLION = D(10) ** 9


def contribute(book: GovernmentBook, billions: int = 25) -> None:
    book.propose(ALICE, TERM_START, CONTRIBUTE, billions * BILLION, None, None)


def fund_cash(book: GovernmentBook, engine) -> Decimal:
    return engine.get_cash(book.sovereign_fund().client_id)


# Validação e título


def test_the_contribution_queues_with_its_value_and_a_title_in_billions(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    contribute(book, 25)

    [queued] = book.state.measures.values()
    assert queued.status is MeasureStatus.QUEUED
    assert queued.value == 25 * BILLION
    assert rules.title(queued) == "Aportar R$ 25 bi no Fundo Soberano"


@pytest.mark.parametrize("value", [None, D(0), D(-1), fund_rules.MAX_CONTRIBUTION + 1])
def test_the_contribution_value_goes_from_one_real_to_the_limit(
    book: GovernmentBook, engine, market, match, value
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        book.propose(ALICE, TERM_START, CONTRIBUTE, value, None, None)


def test_the_contribution_takes_only_a_value(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        book.propose(
            ALICE, TERM_START, CONTRIBUTE, 10 * BILLION, "Energia", None, ticker="X"
        )
    assert book.state.measures == {}


# Voto e vigência


def test_the_approved_contribution_enters_the_fund_cash_on_the_effective_day(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    contribute(book, 25)
    effective = approve_first(book, monkeypatch)
    assert fund_cash(book, engine) == 0

    book.on_tick(USERS, effective - timedelta(days=1), False)
    assert fund_cash(book, engine) == 0

    book.on_tick(USERS, effective, False)

    assert fund_cash(book, engine) == 25 * BILLION
    assert book.sovereign_fund().contributed() == 25 * BILLION
    assert (
        repository.sovereign_fund.flows(match)[0].kind is SovereignFlowKind.CONTRIBUTION
    )


def test_the_contribution_enters_once(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    contribute(book, 25)
    effective = approve_first(book, monkeypatch)

    book.on_tick(USERS, effective, False)
    book.on_tick(USERS, effective + timedelta(days=1), False)

    assert fund_cash(book, engine) == 25 * BILLION
    assert len(repository.sovereign_fund.flows(match)) == 1


def test_a_rejected_contribution_leaves_the_fund_empty(
    book: GovernmentBook, engine, market, match, monkeypatch
):
    govern(book, engine)
    contribute(book, 25)
    congress_says(monkeypatch, False)

    hold_vote_day(book)
    book.on_tick(USERS, FIRST_VOTE + timedelta(days=120), False)

    assert book.state.measures[1].status is MeasureStatus.REJECTED
    assert fund_cash(book, engine) == 0
    assert repository.sovereign_fund.flows(match) == []


def test_the_contribution_announces_itself_in_the_news(
    book: GovernmentBook, engine, market, match, monkeypatch, headlines
):
    govern(book, engine)
    contribute(book, 25)
    effective = approve_first(book, monkeypatch)

    book.on_tick(USERS, effective, False)

    titles = [headline.text for _day, headline in headlines]
    assert any("aporta R$ 25 bi no Fundo Soberano" in title for title in titles)


# Prévia e PIB


def test_the_preview_charges_the_contribution_to_the_debt_and_leaves_the_gdp(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    preview = book.sovereign_contribution_preview(ALICE, TERM_START, 25 * BILLION)

    budget = preview.measure.budget
    assert budget.debt_after > budget.debt_before
    assert budget.revenue_change == 0
    assert budget.spending_change == 0
    assert preview.measure.inflation is None
    assert preview.cash_before == 0
    assert preview.cash_after == 25 * BILLION


def test_a_bigger_contribution_charges_more_debt(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    def extra(billions: int) -> Decimal:
        budget = book.sovereign_contribution_preview(
            ALICE, TERM_START, billions * BILLION
        ).measure.budget
        return budget.debt_after - budget.debt_before

    assert extra(100) > extra(10)


# Governo do computador e retomada


def test_the_computer_government_never_proposes_the_contribution():
    assert CONTRIBUTE not in promises.GENERAL_KINDS


def test_replay_rebuilds_the_contribution(
    book: GovernmentBook, engine, market, match, stored
):
    govern(book, engine)
    contribute(book, 25)

    rebuilt = replay(stored).measures[1]

    assert rebuilt.kind is CONTRIBUTE
    assert rebuilt.value == 25 * BILLION
