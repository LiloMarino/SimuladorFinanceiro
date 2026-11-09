"""A SELIC nas mãos do governo no livro: marcação, reuniões do Copom, credibilidade e retomada."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.enum import IndicatorSeries, PendingType, SelicControl
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.economy.monetary import (
    PRESIDENT_CAP,
    SelicDecision,
    meeting_days,
)
from backend.features.government.governance import monetary_card
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from tests.conftest import SetIndicator
from tests.test_government_book import (
    ALICE,
    BOB,
    SEED,
    TERM_START,
    USERS,
    book,
    engine,
    govern,
    headlines,
    notices,
    office,
    settings,
    stored,
)

# A primeira reunião do mandato que começa em 03/01/2022
MEETING = meeting_days(2022)[0]
# Com as séries vazias, a SELIC e o IPCA da partida são zero
CAP = PRESIDENT_CAP


@pytest.fixture
def selic_book(
    engine, stored, notices, captured_events, office, headlines
) -> GovernmentBook:
    rules = settings().model_copy(update={"selic_control": SelicControl.GOVERNMENT})
    return GovernmentBook(
        rules,
        engine,
        lambda user, _day: office.append(user.id),
        lambda day, headline: headlines.append((day, headline)),
        SEED,
    )


def decided(book: GovernmentBook) -> Decimal | None:
    return book.state.selic_board.selic_on(MEETING + timedelta(days=1))


def test_before_the_first_player_president_the_central_bank_decides(
    selic_book: GovernmentBook,
):
    selic_book.on_tick(USERS, meeting_days(2021)[0], False)

    assert not selic_book.selic_by_government()
    assert selic_book.state.selic_board.decisions() == []


def test_the_meeting_applies_the_marked_selic_from_the_next_day(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)
    selic_book.set_selic(ALICE, TERM_START, CAP)

    selic_book.on_tick(USERS, MEETING, False)

    assert selic_book.state.selic_board.selic_on(MEETING) is None
    assert decided(selic_book) == CAP
    assert selic_book.state.last_meeting == MEETING
    assert selic_book.state.selic_plan is None
    assert (
        selic_book.next_selic_meeting(MEETING + timedelta(days=1))
        == (meeting_days(2022)[1])
    )


def test_only_the_president_marks_in_steps_within_the_cap(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)

    with pytest.raises(ForbiddenError):
        selic_book.set_selic(BOB, TERM_START, CAP)
    with pytest.raises(UnprocessableEntityError):
        selic_book.set_selic(ALICE, TERM_START, Decimal("0.001"))
    with pytest.raises(UnprocessableEntityError):
        selic_book.set_selic(ALICE, TERM_START, CAP + Decimal("0.0025"))
    selic_book.set_selic(ALICE, TERM_START, Decimal("0.01"))


def test_the_autonomous_match_refuses_the_marking(book: GovernmentBook, engine):
    govern(book, engine)

    with pytest.raises(ConflictError):
        book.set_selic(ALICE, TERM_START, CAP)


def test_the_meeting_limits_the_plan_by_the_cap_of_its_day(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)
    selic_book.set_selic(ALICE, TERM_START, CAP)
    selic_book.state.selic_plan = Decimal("0.05")

    selic_book.on_tick(USERS, MEETING, False)

    assert decided(selic_book) == CAP


def test_without_a_plan_the_selic_stays(selic_book: GovernmentBook, engine):
    govern(selic_book, engine)

    selic_book.on_tick(USERS, MEETING, False)

    assert decided(selic_book) == 0
    assert (
        selic_book.state.selic_board.credibility_on(MEETING + timedelta(days=1)) == 100
    )


def test_cutting_below_the_history_with_inflation_high_costs_credibility(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    # IPCA de 0,5% ao mês: 6,2% em 12 meses, acima da meta mais a tolerância; a SELIC da
    # história fica em 10,44% (0,0394% ao dia)
    indicators(
        IndicatorSeries.IPCA,
        {date(2021, m, 1): Decimal("0.5") for m in range(1, 13)}
        | {date(2022, m, 1): Decimal("0.5") for m in (1, 2)},
    )
    indicators(IndicatorSeries.SELIC, {date(2021, 1, 1): Decimal("0.0394")})
    govern(selic_book, engine)
    selic_book.set_selic(ALICE, TERM_START, Decimal("0.09"))

    selic_book.on_tick(USERS, MEETING, False)

    # Cortar de 10,44% para 9%: o juro real fica 1,44 ponto abaixo da história e perde uns 5,75
    credibility = selic_book.state.selic_board.credibility_on(MEETING + timedelta(1))
    assert credibility == pytest.approx(94.25, abs=0.05)
    card = monetary_card(selic_book, MEETING)
    assert card is not None
    assert card.credibility == credibility
    assert card.credibility_premium == pytest.approx(
        Decimal("0.00115"), abs=Decimal("0.00001")
    )
    # Com o IPCA acima da meta mais a tolerância, a janela segue a de 3 pontos
    assert card.cap == CAP


@pytest.mark.parametrize("monthly_ipca", ["0.1", "0.5", "1.5"])
def test_the_window_is_three_points_for_any_ipca(
    selic_book: GovernmentBook,
    engine,
    indicators: SetIndicator,
    monthly_ipca: str,
):
    indicators(
        IndicatorSeries.IPCA,
        {date(2021, m, 1): Decimal(monthly_ipca) for m in range(1, 13)}
        | {date(2022, m, 1): Decimal(monthly_ipca) for m in (1, 2)},
    )
    govern(selic_book, engine)
    card = monetary_card(selic_book, MEETING)
    assert card is not None
    assert card.cap == PRESIDENT_CAP == Decimal("0.03")

    selic_book.set_selic(ALICE, TERM_START, Decimal("0.03"))
    with pytest.raises(UnprocessableEntityError):
        selic_book.set_selic(ALICE, TERM_START, Decimal("0.0325"))


def monthly_ipca(indicators: SetIndicator, value: str) -> None:
    indicators(
        IndicatorSeries.IPCA,
        {date(2021, m, 1): Decimal(value) for m in range(1, 13)}
        | {date(2022, m, 1): Decimal(value) for m in (1, 2)},
    )


def test_with_negative_ipca_the_president_takes_the_selic_to_minus_half_a_point(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    monthly_ipca(indicators, "-0.5")
    govern(selic_book, engine)
    card = monetary_card(selic_book, MEETING)
    assert card is not None
    assert card.floor == Decimal("-0.005")

    with pytest.raises(UnprocessableEntityError):
        selic_book.set_selic(ALICE, TERM_START, Decimal("-0.0075"))
    selic_book.set_selic(ALICE, TERM_START, Decimal("-0.005"))

    selic_book.on_tick(USERS, MEETING, False)

    assert decided(selic_book) == Decimal("-0.005")


def test_with_ipca_back_above_zero_the_floor_returns_to_zero(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    monthly_ipca(indicators, "0.3")
    govern(selic_book, engine)
    card = monetary_card(selic_book, MEETING)
    assert card is not None
    assert card.floor == 0

    with pytest.raises(UnprocessableEntityError):
        selic_book.set_selic(ALICE, TERM_START, Decimal("-0.0025"))

    # Um plano marcado com o piso aberto é limitado pelo piso do dia da reunião
    selic_book.state.selic_plan = Decimal("-0.005")
    selic_book.on_tick(USERS, MEETING, False)

    assert decided(selic_book) == 0


def test_the_window_reaches_the_history_even_when_it_moved_more_than_three_points(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    # A SELIC da história fica em 10,44% (0,0394% ao dia) e a do governo em 5%
    indicators(IndicatorSeries.SELIC, {date(2021, 1, 1): Decimal("0.0394")})
    govern(selic_book, engine)
    selic_book.state.selic_board.record(
        SelicDecision(TERM_START - timedelta(days=1), Decimal("0.05"), 100)
    )
    card = monetary_card(selic_book, TERM_START)
    assert card is not None
    assert card.history_selic == pytest.approx(Decimal("0.1044"), abs=Decimal("0.001"))

    # A janela de 3 pontos pararia em 8%; a história, em 10,5%, entra nela
    selic_book.set_selic(ALICE, TERM_START, Decimal("0.105"))
    with pytest.raises(UnprocessableEntityError):
        selic_book.set_selic(ALICE, TERM_START, Decimal("0.1075"))

    selic_book.on_tick(USERS, MEETING, False)

    assert decided(selic_book) == Decimal("0.105")


def test_holding_the_rate_of_the_history_keeps_credibility_full(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    indicators(
        IndicatorSeries.IPCA,
        {date(2021, m, 1): Decimal("0.5") for m in range(1, 13)}
        | {date(2022, m, 1): Decimal("0.5") for m in (1, 2)},
    )
    indicators(IndicatorSeries.SELIC, {date(2021, 1, 1): Decimal("0.0394")})
    govern(selic_book, engine)

    selic_book.on_tick(USERS, MEETING, False)

    assert selic_book.state.selic_board.credibility_on(MEETING + timedelta(1)) == 100


def test_the_computer_moves_toward_the_central_bank_within_the_cap(
    selic_book: GovernmentBook, engine, monkeypatch: pytest.MonkeyPatch
):
    govern(selic_book, engine)
    # 3 pontos de IPCA a mais pedem 4,5 pontos de SELIC; a reunião anda só 3
    monkeypatch.setattr(selic_book.linked().layer, "inflation_points", lambda _d: 3.0)
    monkeypatch.setattr(selic_book, "president", lambda: None)

    selic_book.on_tick(USERS, MEETING, False)

    assert decided(selic_book) == CAP


def test_the_president_is_warned_a_week_before_a_meeting_without_plan(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)
    week_before = MEETING - timedelta(days=7)

    def types(user, day: date) -> list[PendingType]:
        return [item.type for item in selic_book.pending(user, day)]

    assert PendingType.SELIC_MEETING not in types(ALICE, week_before - timedelta(1))
    assert PendingType.SELIC_MEETING in types(ALICE, week_before)
    assert PendingType.SELIC_MEETING not in types(BOB, week_before)
    selic_book.set_selic(ALICE, week_before, CAP)
    assert PendingType.SELIC_MEETING not in types(ALICE, week_before)


def test_replay_rebuilds_the_decisions(selic_book: GovernmentBook, engine, stored):
    govern(selic_book, engine)
    selic_book.set_selic(ALICE, TERM_START, CAP)
    selic_book.on_tick(USERS, MEETING, False)

    state = replay(stored)

    assert state.selic_board.decisions() == selic_book.state.selic_board.decisions()
    assert state.last_meeting == MEETING


# O que o mercado espera para a próxima reunião (o Focus no cartão)


def focus_card(
    selic_book: GovernmentBook, engine, indicators: SetIndicator, survey: date | None
):
    """O cartão no dia da primeira reunião, com a SELIC da história em 10,44% e, se pedido, uma pesquisa do Focus em 12%."""
    indicators(IndicatorSeries.SELIC, {date(2021, 1, 1): Decimal("0.0394")})
    if survey is not None:
        indicators(IndicatorSeries.FOCUS_SELIC, {survey: Decimal("12.0")})
    govern(selic_book, engine)
    card = monetary_card(selic_book, MEETING)
    assert card is not None
    return card


def test_the_market_expects_the_focus_when_the_survey_is_recent(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    card = focus_card(selic_book, engine, indicators, MEETING - timedelta(days=30))

    # Sem regra a somar nem decisão do presidente, o desvio esperado é zero
    assert card.focus == Decimal("0.12")


def test_the_market_expects_the_history_without_a_recent_survey(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    stale = focus_card(selic_book, engine, indicators, MEETING - timedelta(days=31))
    assert stale.focus == stale.history_selic


def test_the_market_expects_the_history_before_the_survey_exists(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    absent = focus_card(selic_book, engine, indicators, None)
    assert absent.focus == absent.history_selic


def test_the_market_keeps_expecting_the_gap_the_president_showed(
    selic_book: GovernmentBook, engine, indicators: SetIndicator
):
    focus_card(selic_book, engine, indicators, None)
    selic_book.set_selic(ALICE, TERM_START, Decimal("0.0975"))
    selic_book.on_tick(USERS, MEETING, False)

    card = monetary_card(selic_book, MEETING + timedelta(days=1))

    # A SELIC da história anda 10,44%; decidir 9,75% deixa o mercado esperando o mesmo corte
    assert card is not None
    assert card.focus == pytest.approx(card.selic, abs=Decimal("0.0001"))
