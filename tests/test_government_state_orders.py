"""As ordens do presidente às estatais no livro do governo: permissão, teto, vigência, retomada e governo do computador."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.state_company import StateCompanyDTO
from backend.core.enum import (
    DividendPolicy,
    GovernmentEventType,
    MeasureKind,
    StateCompanyOrigin,
    StateCompanyStatus,
    StateControl,
    StateLever,
)
from backend.core.exceptions.http_exceptions import (
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import required
from backend.features.government import caretaker
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from backend.features.state_companies import levers
from backend.features.state_companies.orders import StateOrder
from tests.test_government_book import (
    ALICE,
    BOB,
    SEED,
    TERM_START,
    USERS,
    book,
    close_months,
    engine,
    found,
    govern,
    headlines,
    market,
    notices,
    office,
    settings,
    stored,
)

FUEL = "PETR4"
ENERGY = "ELET3"
BANK = "BBAS3"
PLAIN = "CMIG4"
D = Decimal


def company(
    ticker: str,
    lever: StateLever | None,
    status: StateCompanyStatus = StateCompanyStatus.ACTIVE,
) -> StateCompanyDTO:
    return StateCompanyDTO(
        id=sum(map(ord, ticker)),
        stock_id=1,
        ticker=ticker,
        origin=StateCompanyOrigin.IMPORTED,
        government_share=D("0.5"),
        shares=1_000_000,
        lever=lever,
        size=None,
        invested=D(0),
        mean_return=None,
        seed=None,
        status=status,
        founded_on=None,
        offer_opened_on=None,
        privatized_on=None,
        proceeds=None,
    )


def new_state_book(
    engine, office, headlines, companies: list[StateCompanyDTO]
) -> GovernmentBook:
    return GovernmentBook(
        settings(),
        engine,
        lambda user, _day: office.append(user.id),
        lambda *_: D(0),
        lambda day, headline: headlines.append((day, headline)),
        SEED,
        state_companies=companies,
    )


@pytest.fixture
def state_book(
    monkeypatch: pytest.MonkeyPatch,
    engine,
    stored,
    notices,
    captured_events,
    office,
    headlines,
):
    """O livro com quatro estatais importadas: combustível, energia, banco e uma sem preço a segurar.

    As importadas não têm proventos na história, e o livro roda sem banco.
    """
    monkeypatch.setattr(repository.corporate_event, "get_for_stock", lambda *_: [])
    return new_state_book(
        engine,
        office,
        headlines,
        [
            company(FUEL, StateLever.FUEL),
            company(ENERGY, StateLever.ENERGY),
            company(BANK, StateLever.BANK),
            company(PLAIN, None),
        ],
    )


def order(
    book: GovernmentBook,
    ticker: str = FUEL,
    control: StateControl = StateControl.P10,
    policy: DividendPolicy = DividendPolicy.NORMAL,
    user=ALICE,
) -> None:
    book.set_state_order(user, TERM_START, ticker, control, policy)


def given(book: GovernmentBook) -> dict[str, StateOrder]:
    return dict(book.state.state_orders)


def events_of(stored, kind: GovernmentEventType) -> list:
    return [e for e in stored if e.event_type is kind]


def computer_takes_office(book: GovernmentBook, day: date) -> None:
    """O partido do computador de mais cadeiras toma posse sem presidente jogador."""
    heir = required(
        caretaker.successor(
            book.state.house_on(day),
            {p.id for p in book.state.computer_parties()},
        )
    )
    book._emit(
        GovernmentEventType.TERM_STARTED,
        TERM_START,
        party_id=heir.party_id,
        president_id=None,
        vice_id=None,
        consecutive=1,
    )


# Quem pode dar a ordem


def test_the_president_gives_the_order_and_it_is_recorded(
    state_book: GovernmentBook, engine, market, stored
):
    govern(state_book, engine)

    order(state_book, FUEL, StateControl.P10, DividendPolicy.SQUEEZE)

    assert given(state_book) == {
        FUEL: StateOrder(StateControl.P10, DividendPolicy.SQUEEZE)
    }
    assert stored[-1].event_type is GovernmentEventType.STATE_ORDER_SET


def test_only_the_president_gives_orders(state_book: GovernmentBook, engine, market):
    govern(state_book, engine)

    with pytest.raises(ForbiddenError):
        order(state_book, user=BOB)

    assert given(state_book) == {}


def test_an_unknown_company_is_not_found(state_book: GovernmentBook, engine, market):
    govern(state_book, engine)

    with pytest.raises(NotFoundError):
        order(state_book, "ZZZZ3")


def test_a_company_in_privatization_takes_no_order(
    engine, stored, notices, captured_events, office, headlines, market
):
    privatizing = new_state_book(
        engine,
        office,
        headlines,
        [company(FUEL, StateLever.FUEL, StateCompanyStatus.PRIVATIZING)],
    )
    govern(privatizing, engine)

    with pytest.raises(ForbiddenError):
        order(privatizing)


def test_a_queued_privatization_blocks_the_order(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    state_book.propose(
        ALICE,
        TERM_START,
        MeasureKind.PRIVATIZE_STATE_COMPANY,
        None,
        None,
        None,
        ticker=FUEL,
    )

    with pytest.raises(ForbiddenError):
        order(state_book, FUEL)
    # As outras estatais seguem recebendo ordem
    order(state_book, ENERGY, StateControl.P5)


# Teto de IPCA e degraus


def test_a_step_over_the_ceiling_is_rejected(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P20)

    # Combustível a 20% segura 1,0 ponto: a energia a 20% somaria 1,8 e passa do teto de 1,5
    with pytest.raises(UnprocessableEntityError):
        order(state_book, ENERGY, StateControl.P20)
    order(state_book, ENERGY, StateControl.P10)

    held = levers.total_held_points(
        [(StateLever.FUEL, StateControl.P20), (StateLever.ENERGY, StateControl.P10)]
    )
    assert held <= levers.IPCA_CAP_POINTS


def test_the_company_own_previous_order_does_not_count_against_the_ceiling(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P20)

    order(state_book, FUEL, StateControl.P15)

    assert given(state_book)[FUEL].control is StateControl.P15


def test_a_company_without_price_to_hold_takes_only_the_dividend_policy(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)

    with pytest.raises(UnprocessableEntityError):
        order(state_book, PLAIN, StateControl.P5)
    order(state_book, PLAIN, StateControl.NONE, DividendPolicy.REINVEST)

    assert given(state_book)[PLAIN].dividend_policy is DividendPolicy.REINVEST


def test_the_bank_takes_a_control_step_without_holding_ipca(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)

    order(state_book, BANK, StateControl.P20)

    assert given(state_book)[BANK].control is StateControl.P20
    assert levers.held_points(StateLever.BANK, StateControl.P20) == 0


def test_the_default_order_leaves_no_trace(state_book: GovernmentBook, engine, market):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)

    order(state_book, FUEL, StateControl.NONE, DividendPolicy.NORMAL)

    assert given(state_book) == {}


# Vigência: a ordem vale do mês seguinte


def test_the_order_given_in_the_month_applies_from_the_next_month(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    companies = state_book.state_companies()

    assert companies.orders(date(2022, 1, 31)) == {}

    close_months(state_book, 1)

    assert companies.orders(date(2022, 1, 31)) == {}
    assert companies.orders(date(2022, 2, 1)) == {
        FUEL: StateOrder(StateControl.P10, DividendPolicy.NORMAL)
    }
    assert date(2022, 2, 1) in state_book.state.state_order_history


def test_a_month_without_news_snapshots_nothing_new(
    state_book: GovernmentBook, engine, market, stored
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    close_months(state_book, 1)
    before = len(events_of(stored, GovernmentEventType.STATE_ORDERS_IN_FORCE))

    close_months(state_book, 1, date(2022, 2, 28))

    after = len(events_of(stored, GovernmentEventType.STATE_ORDERS_IN_FORCE))
    assert (before, after) == (1, 1)


def test_releasing_an_order_enters_the_history_as_the_empty_order(
    state_book: GovernmentBook, engine, market
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10)
    close_months(state_book, 1)

    order(state_book, FUEL, StateControl.NONE)
    close_months(state_book, 1, date(2022, 2, 28))

    assert state_book.state_companies().orders(date(2022, 3, 1)) == {}
    # O mês sem controle solta o que ele represou
    assert state_book.state_companies().backlog(date(2022, 2, 15)) > 0
    assert state_book.state_companies().inflation_points(date(2022, 3, 1)) > 0


def test_replay_rebuilds_the_orders_and_the_history(
    state_book: GovernmentBook, engine, market, stored
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10, DividendPolicy.REINVEST)
    close_months(state_book, 1)
    order(state_book, ENERGY, StateControl.P5)

    rebuilt = replay(stored)

    assert rebuilt.state_orders == state_book.state.state_orders
    assert rebuilt.state_order_history == state_book.state.state_order_history


# Governo do computador


def test_the_computer_government_releases_every_order(
    state_book: GovernmentBook, engine, market, stored
):
    govern(state_book, engine)
    order(state_book, FUEL, StateControl.P10, DividendPolicy.SQUEEZE)
    order(state_book, ENERGY, StateControl.P5)
    day = date(2022, 2, 1)

    computer_takes_office(state_book, day)
    state_book.on_tick(USERS, day, False)

    release = events_of(stored, GovernmentEventType.STATE_ORDER_SET)[-1]
    assert release.payload["ticker"] is None
    assert release.payload["control"] == StateControl.NONE.value
    assert release.payload["dividend_policy"] == DividendPolicy.NORMAL.value
    assert given(state_book) == {}


def test_without_orders_the_computer_government_emits_no_release(
    state_book: GovernmentBook, engine, market, stored
):
    govern(state_book, engine)
    day = date(2022, 2, 1)

    computer_takes_office(state_book, day)
    state_book.on_tick(USERS, day, False)

    assert events_of(stored, GovernmentEventType.STATE_ORDER_SET) == []
