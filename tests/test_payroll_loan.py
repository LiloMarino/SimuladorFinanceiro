"""O consignado do Servidor no livro de crédito: contrato, margem, cobrança na virada do mês, dívida e retomada."""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import (
    CreditEventType,
    IndicatorSeries,
    PrepaymentMode,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.indicators import annual_index_rate
from backend.core.rates import STORED_RATE_STEP
from backend.core.repository.economic import IndicatorHistory
from backend.core.utils import last_month_turn, next_month_turn
from backend.features.credit.credit_book import PayrollLoan
from backend.features.credit.overview import (
    build_overview,
    build_payroll_loan,
    build_payroll_quote,
)
from backend.features.credit.price import installment
from backend.features.credit.rules import (
    MAX_TERM_MONTHS,
    MIN_TERM_MONTHS,
    PAYROLL_GRACE_DAYS,
    PAYROLL_MARGIN,
    PAYROLL_SPREAD,
    payroll_first_collection,
)
from backend.features.economy.growth import stocks_drawdown
from backend.features.profession.public_servant import (
    PayrollMove,
    payroll_amount,
    payroll_policy,
)
from backend.features.statistics.credit import credit_standing
from tests.conftest import SetIndicator
from tests.fakes import daily_series
from tests.test_credit_book import (  # noqa: F401
    PLAYER,
    START,
    CreditEngine,
    credit_events,
    engine,
    notices,
    stored_events,
)

SALARY = Decimal(5000)
# A margem de um salário líquido de 5.000: 35%
MARGIN = SALARY * PAYROLL_MARGIN
FIRST_TURN = date(2020, 3, 3)
# Patrimônio que deixa o limite de dívida folgado para o teste da margem
RICH = Decimal(1000000)


class PayrollEngine(CreditEngine):
    """O motor do livro com a cobrança da parcela do consignado, que sai do caixa."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collected: list[Decimal] = []

    def pay_payroll_installment(self, client_id: uuid.UUID, amount: Decimal) -> None:
        self.collected.append(amount)
        self.add_cash(client_id, -amount)


@pytest.fixture
def payroll_engine(engine, captured_events) -> PayrollEngine:  # noqa: F811
    return PayrollEngine(cash=dict(engine.cash), current_date=START)


def turn_to(book_engine: CreditEngine, day: date) -> None:
    """A virada do mês: o dia muda e o livro cobra o consignado, como o `_live` faz."""
    book_engine.current_date = day
    book_engine.credit_book.collect_payroll(PLAYER, 1)


def month_turns(first: date, count: int) -> list[date]:
    days = []
    year, month = first.year, first.month
    for _ in range(count):
        days.append(date(year, month, 3))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return days


def test_the_contract_has_selic_plus_two_fixed_and_the_price_installment(
    payroll_engine, captured_events, indicators: SetIndicator
):
    book = payroll_engine.credit_book

    loan = book.contract_payroll(PLAYER, Decimal(10000), 24, SALARY)

    expected_rate = (
        annual_index_rate(IndicatorSeries.SELIC, START) + PAYROLL_SPREAD
    ).quantize(STORED_RATE_STEP)
    assert loan.annual_rate == expected_rate
    assert loan.state.installment == installment(Decimal(10000), expected_rate, 24)
    assert loan.term_months == 24 and loan.total_installments == 24
    assert payroll_engine.get_cash(PLAYER) == Decimal(20000)
    [event] = credit_events(captured_events)
    assert event.event_type is CreditEventType.PAYROLL_CONTRACT
    assert event.grade is None
    assert event.annual_rate == expected_rate

    # A SELIC muda e o contrato segue com o juro do dia em que foi assinado
    indicators(IndicatorSeries.SELIC, daily_series(START, date(2023, 12, 31), "0.0008"))
    assert book.payroll_loans(PLAYER)[0].annual_rate == expected_rate
    assert book.payroll_rate(START) != expected_rate


def test_the_contract_skips_the_offer_and_the_grade_does_not_block_it(
    payroll_engine, monkeypatch
):
    book = payroll_engine.credit_book

    def refuse(*_):
        raise AssertionError("o consignado não passa pela oferta")

    monkeypatch.setattr(type(book), "offer", refuse)

    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)

    assert loan.principal == Decimal(5000)


@pytest.mark.parametrize("term", [MIN_TERM_MONTHS - 1, MAX_TERM_MONTHS + 1])
def test_a_term_outside_six_to_sixty_months_is_refused(payroll_engine, term):
    with pytest.raises(UnprocessableEntityError):
        payroll_engine.credit_book.contract_payroll(PLAYER, Decimal(1000), term, SALARY)


@pytest.mark.parametrize("term", [MIN_TERM_MONTHS, MAX_TERM_MONTHS])
def test_the_limit_terms_are_accepted(payroll_engine, term):
    loan = payroll_engine.credit_book.contract_payroll(
        PLAYER, Decimal(1000), term, SALARY
    )

    assert loan.total_installments == term


def test_an_installment_over_the_margin_is_refused(payroll_engine):
    book = payroll_engine.credit_book
    # O maior valor de 12 meses que a margem sustenta, mais um centavo de excesso
    quote = build_payroll_quote(book, PLAYER, START, Decimal(1000), 12, SALARY)
    over = quote.max_amount + Decimal(100)

    with pytest.raises(ConflictError, match="margem"):
        book.contract_payroll(PLAYER, over, 12, SALARY)

    assert book.payroll_loans(PLAYER) == []
    assert payroll_engine.get_cash(PLAYER) == Decimal(10000)


def test_the_largest_amount_of_the_quote_fits_the_margin(payroll_engine):
    payroll_engine.cash[PLAYER] = RICH
    book = payroll_engine.credit_book
    quote = build_payroll_quote(book, PLAYER, START, Decimal(1000), 12, SALARY)

    loan = book.contract_payroll(PLAYER, quote.max_amount, 12, SALARY)

    assert loan.state.installment <= MARGIN
    assert quote.margin == MARGIN
    assert quote.margin_free == MARGIN


def test_a_second_consignado_must_fit_in_the_margin_left_by_the_first(payroll_engine):
    payroll_engine.cash[PLAYER] = RICH
    book = payroll_engine.credit_book
    quote = build_payroll_quote(book, PLAYER, START, Decimal(1000), 12, SALARY)
    book.contract_payroll(PLAYER, quote.max_amount * Decimal("0.6"), 12, SALARY)

    with pytest.raises(ConflictError, match="margem"):
        book.contract_payroll(PLAYER, quote.max_amount * Decimal("0.6"), 12, SALARY)

    second = book.contract_payroll(
        PLAYER, quote.max_amount * Decimal("0.3"), 12, SALARY
    )

    assert len(book.payroll_loans(PLAYER)) == 2
    assert book.payroll_used(PLAYER) == sum(
        (loan.state.installment for loan in book.payroll_loans(PLAYER)),
        Decimal(0),
    )
    assert second.state.installment <= MARGIN


def test_the_first_installment_waits_for_the_grace_and_then_comes_every_month(
    payroll_engine, captured_events
):
    book = payroll_engine.credit_book
    # Contrato em 6/1: a virada de fevereiro fica a 28 dias, antes do fim da carência
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    amount = loan.state.due_amount()

    turn_to(payroll_engine, date(2020, 2, 3))
    assert payroll_engine.collected == []

    turn_to(payroll_engine, FIRST_TURN)
    assert payroll_engine.collected == [amount]

    turn_to(payroll_engine, date(2020, 4, 1))
    assert len(payroll_engine.collected) == 2


@pytest.mark.parametrize(
    ("signed", "first"),
    [
        # Contrato no fim do mês: a virada seguinte fica a poucos dias e a carência pula um mês
        (date(2020, 1, 24), date(2020, 3, 2)),
        # Contrato na virada de mês paga na virada seguinte, mesmo com fevereiro curto
        (date(2020, 1, 1), date(2020, 2, 3)),
        (date(2020, 2, 3), date(2020, 3, 2)),
        (date(2020, 4, 1), date(2020, 5, 1)),
        # Contrato no dia seguinte à virada: a virada de julho fica a 29 dias
        (date(2020, 6, 2), date(2020, 8, 3)),
        # O fim da carência cai num sábado e a virada é a segunda seguinte
        (date(2020, 1, 2), date(2020, 2, 3)),
        # O fim da carência cai exatamente na virada
        (date(2020, 12, 2), date(2021, 1, 1)),
    ],
)
def test_the_first_collection_is_the_first_turn_after_the_grace(signed, first):
    assert payroll_first_collection(signed) == first


def test_the_contract_on_the_first_trading_day_always_pays_in_the_next_month():
    turn = date(2019, 1, 1)
    while turn < date(2024, 1, 1):
        first = payroll_first_collection(turn)
        # O primeiro dia útil do mês seguinte
        assert first == next_month_turn(turn)
        assert (first.year, first.month) == (
            (turn.year + 1, 1) if turn.month == 12 else (turn.year, turn.month + 1)
        )
        assert first.weekday() < 5 and first.day <= 3
        turn = first


def test_the_contract_outside_the_turn_waits_at_least_the_grace():
    day = date(2020, 1, 1)
    while day < date(2022, 1, 1):
        turn = next_month_turn(day.replace(day=1) - timedelta(days=1))
        if day != turn:
            first = payroll_first_collection(day)
            assert (first - day).days >= PAYROLL_GRACE_DAYS
            assert first == last_month_turn(first)
        day += timedelta(days=1)


def test_one_installment_per_month_with_no_late_event(payroll_engine, captured_events):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 6, SALARY)

    for day in month_turns(FIRST_TURN, 6):
        turn_to(payroll_engine, day)

    types = [e.event_type for e in credit_events(captured_events)]
    assert types.count(CreditEventType.PAYROLL_INSTALLMENT) == 6
    assert CreditEventType.INSTALLMENT_LATE not in types
    assert len(payroll_engine.collected) == 6
    assert loan.is_settled
    assert book.payroll_loans(PLAYER) == []
    assert book.debt(PLAYER, date(2020, 8, 3)) == 0
    numbers = [
        e.installment_number
        for e in credit_events(captured_events)
        if e.event_type is CreditEventType.PAYROLL_INSTALLMENT
    ]
    assert numbers == [1, 2, 3, 4, 5, 6]


def test_the_installment_is_never_late_even_without_cash(
    payroll_engine,
    captured_events,
    notices,  # noqa: F811
):
    book = payroll_engine.credit_book
    book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    payroll_engine.cash[PLAYER] = Decimal(0)

    turn_to(payroll_engine, FIRST_TURN)

    client = book.client(PLAYER)
    assert not any(loan.overdue for loan in client.loans.values())
    assert not book.alert(PLAYER, FIRST_TURN)
    assert book.pending(PLAYER, FIRST_TURN) == []
    assert notices == ["credit_installment_paid"]


def test_the_consignado_counts_in_the_debt_and_reduces_the_common_limit(
    payroll_engine,
):
    book = payroll_engine.credit_book
    before = book.offer(PLAYER, START)
    loan = book.contract_payroll(PLAYER, Decimal(2000), 12, SALARY)

    assert book.loan_debt(PLAYER, START) == Decimal(2000)
    assert book.debt(PLAYER, START) == Decimal(2000)
    after = book.offer(PLAYER, START)
    # A oferta comum segue o mesmo cálculo; a dívida do consignado tira do que cabe
    assert after.annual_rate == before.annual_rate
    assert after.debt_limit_amount == before.debt_limit_amount
    assert before.max_amount - after.max_amount == loan.debt_on(START) == Decimal(2000)


def test_the_consignado_is_listed_apart_and_its_debt_matches_the_summary(
    payroll_engine,
):
    book = payroll_engine.credit_book
    book.contract_payroll(PLAYER, Decimal(2000), 12, SALARY)

    overview = build_overview(book, PLAYER, START)

    assert overview.loans == []
    assert len(overview.payroll_loans) == 1
    assert overview.open_loans == 1
    assert overview.debt == Decimal(2000)
    assert sum((x.balance for x in overview.payroll_loans), Decimal(0)) == (
        overview.loan_debt
    )


def test_the_consignado_installments_enter_the_upcoming_without_a_number(
    payroll_engine,
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(2000), 12, SALARY)
    first = payroll_first_collection(START)

    overview = build_overview(book, PLAYER, START)

    assert [row.loan_number for row in overview.upcoming] == [None] * 3
    assert overview.upcoming[0].due_date == first
    assert overview.upcoming[0].amount == loan.state.installment
    assert overview.payroll_loans[0].next_due == first
    assert overview.next_installments_total == loan.state.installment
    assert overview.next_installments_first == first


def test_the_quote_gives_the_maximum_of_every_term_and_the_comparison(payroll_engine):
    payroll_engine.cash[PLAYER] = RICH
    book = payroll_engine.credit_book

    quote = build_payroll_quote(book, PLAYER, START, Decimal(5000), 24, SALARY)

    terms = [row.term_months for row in quote.max_by_term]
    assert terms == list(range(MIN_TERM_MONTHS, MAX_TERM_MONTHS + 1))
    assert {row.term_months: row.max_amount for row in quote.max_by_term}[24] == (
        quote.max_amount
    )
    assert quote.fits_margin and quote.fits_debt_limit
    assert quote.common_total_interest is not None
    assert quote.interest_saved == quote.common_total_interest - quote.total_interest
    assert quote.interest_saved is not None and quote.interest_saved > 0


def test_an_amount_over_the_margin_is_flagged_by_the_quote(payroll_engine):
    payroll_engine.cash[PLAYER] = RICH
    book = payroll_engine.credit_book

    quote = build_payroll_quote(book, PLAYER, START, Decimal(500000), 24, SALARY)

    assert not quote.fits_margin
    assert quote.amount > quote.max_amount


def test_the_consignado_respects_the_debt_limit_of_the_common_loan(payroll_engine):
    book = payroll_engine.credit_book
    room = book.payroll_room(PLAYER, START)
    amount = room + Decimal(1)

    quote = build_payroll_quote(book, PLAYER, START, amount, 120 // 5, SALARY)

    assert quote.debt_limit_room == room
    assert not quote.fits_debt_limit
    with pytest.raises(ConflictError, match="limite de dívida"):
        book.contract_payroll(PLAYER, amount, 24, SALARY)


def test_the_standing_counts_the_debt_the_installments_and_the_interest(
    payroll_engine, captured_events
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    turn_to(payroll_engine, FIRST_TURN)
    day = FIRST_TURN
    snapshot = PatrimonialHistoryDTO(
        snapshot_date=day,
        total_networth=Decimal(4000),
        total_equity=Decimal(0),
        total_fixed=Decimal(0),
        total_cash=Decimal(0),
        total_contribution=Decimal(0),
        total_debt=book.debt(PLAYER, day),
    )

    standing = credit_standing(credit_events(captured_events), [snapshot])

    assert standing.has_borrowed
    assert not standing.delinquent
    assert standing.debt == book.debt(PLAYER, day) > 0
    assert standing.paid_installments == 1
    assert standing.late_installments == 0
    assert standing.cost_of_debt == loan.annual_rate
    assert 0 < standing.interest_paid < loan.state.installment


def test_the_debt_in_the_snapshot_lowers_the_grade_input(payroll_engine):
    book = payroll_engine.credit_book
    book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)

    # O patrimônio do jogo é caixa menos dívida: o consignado entra pela definição única
    assert payroll_engine.networth(PLAYER, book.debt(PLAYER, START)) == (
        payroll_engine.get_cash(PLAYER) - Decimal(5000)
    )


def test_replay_rebuilds_the_consignado_as_the_live_book_has_it(
    payroll_engine,
    captured_events,
    stored_events,  # noqa: F811
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    for day in month_turns(FIRST_TURN, 3):
        turn_to(payroll_engine, day)

    stored_events.extend(credit_events(captured_events))
    resumed = PayrollEngine(
        cash={PLAYER: payroll_engine.get_cash(PLAYER)},
        current_date=payroll_engine.current_date,
    )

    [back] = resumed.credit_book.payroll_loans(PLAYER)
    assert isinstance(back, PayrollLoan)
    assert back.loan_id == loan.loan_id
    assert back.state == loan.state
    assert back.paid_installments == 3
    assert resumed.credit_book.debt(PLAYER, payroll_engine.current_date) == (
        book.debt(PLAYER, payroll_engine.current_date)
    )
    assert resumed.credit_book.loans(PLAYER) == []


def test_replay_keeps_the_grace_of_a_consignado_without_installments(
    payroll_engine,
    captured_events,
    stored_events,  # noqa: F811
):
    payroll_engine.credit_book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    stored_events.extend(credit_events(captured_events))
    resumed = PayrollEngine(
        cash={PLAYER: payroll_engine.get_cash(PLAYER)}, current_date=START
    )

    turn_to(resumed, date(2020, 2, 3))
    assert resumed.collected == []

    turn_to(resumed, FIRST_TURN)
    assert len(resumed.collected) == 1


def test_replay_forgets_a_paid_off_consignado(
    payroll_engine,
    captured_events,
    stored_events,  # noqa: F811
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    turn_to(payroll_engine, FIRST_TURN)
    book.payoff(PLAYER, loan.loan_id)

    stored_events.extend(credit_events(captured_events))
    resumed = PayrollEngine(
        cash={PLAYER: payroll_engine.get_cash(PLAYER)},
        current_date=payroll_engine.current_date,
    )

    assert resumed.credit_book.payroll_loans(PLAYER) == []
    assert resumed.credit_book.debt(PLAYER, FIRST_TURN) == 0


def test_payoff_takes_the_balance_out_of_the_cash_and_closes_the_contract(
    payroll_engine, captured_events
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    turn_to(payroll_engine, FIRST_TURN)
    owed = loan.payoff_on(FIRST_TURN)
    cash = payroll_engine.get_cash(PLAYER)

    book.payoff(PLAYER, loan.loan_id)

    assert payroll_engine.get_cash(PLAYER) == cash - owed
    assert book.payroll_loans(PLAYER) == []
    assert book.debt(PLAYER, FIRST_TURN) == 0
    assert credit_events(captured_events)[-1].event_type is CreditEventType.PAYOFF
    with pytest.raises(NotFoundError):
        book.payoff(PLAYER, loan.loan_id)


def test_the_payoff_announces_the_grade_change_like_the_common_loan(
    payroll_engine,
    notices,  # noqa: F811
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    client = book.client(PLAYER)
    # A última nota que o jogador viu era pior que a de hoje
    assert client.seen is not None
    client.seen = replace(client.seen, payment_points=Decimal(0))
    notices.clear()

    book.payoff(PLAYER, loan.loan_id)

    assert "credit_rating_changed" in notices


def test_prepay_that_reduces_the_installment_frees_margin(payroll_engine):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    used = book.payroll_used(PLAYER)

    book.prepay(PLAYER, loan.loan_id, Decimal(1000), PrepaymentMode.REDUCE_INSTALLMENT)

    assert book.payroll_used(PLAYER) < used
    assert book.debt(PLAYER, START) < Decimal(5000)


def test_the_prepay_that_shortens_the_term_keeps_collecting_the_same_installment(
    payroll_engine,
):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    amount = loan.state.installment

    book.prepay(PLAYER, loan.loan_id, Decimal(1000), PrepaymentMode.SHORTEN_TERM)
    turn_to(payroll_engine, FIRST_TURN)

    assert loan.state.remaining < 12
    assert payroll_engine.collected == [amount]


def test_the_quote_reads_installment_rate_margin_and_the_largest_amount(
    payroll_engine,
):
    book = payroll_engine.credit_book
    rate = book.payroll_rate(START)

    quote = build_payroll_quote(book, PLAYER, START, Decimal(3000), 24, SALARY)

    assert quote.annual_rate == rate
    assert quote.installment == installment(Decimal(3000), rate, 24)
    assert quote.margin == MARGIN
    assert quote.margin_used == 0
    assert quote.margin_free == MARGIN
    assert quote.fits_margin
    assert quote.total_paid == quote.amount + quote.total_interest
    # O valor máximo gera uma parcela dentro da margem; dez reais a mais passam
    assert installment(quote.max_amount, rate, 24) <= MARGIN
    assert installment(quote.max_amount + Decimal(10), rate, 24) > MARGIN


def test_the_quote_shows_the_margin_used_by_an_active_consignado(payroll_engine):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(4000), 12, SALARY)

    quote = build_payroll_quote(book, PLAYER, START, Decimal(1000), 12, SALARY)

    assert quote.margin_used == loan.state.installment
    assert quote.margin_free == MARGIN - loan.state.installment


def test_the_quote_flags_an_amount_that_does_not_fit(payroll_engine):
    book = payroll_engine.credit_book

    quote = build_payroll_quote(book, PLAYER, START, Decimal(50000), 12, SALARY)

    assert not quote.fits_margin
    assert quote.installment > quote.margin_free


def test_the_loan_dto_reads_the_contract(payroll_engine):
    book = payroll_engine.credit_book
    loan = book.contract_payroll(PLAYER, Decimal(4000), 12, SALARY)

    dto = build_payroll_loan(loan, START)

    assert dto.id == loan.loan_id
    assert dto.installment == loan.state.installment
    assert dto.total_installments == 12 and dto.paid_installments == 0
    assert dto.balance == loan.balance_on(START)


# =========================
# O topo de 12 meses do Ibovespa
# =========================


def ibov(indicators: SetIndicator, points: dict[date, str]) -> None:
    indicators(
        IndicatorSeries.IBOV, {day: Decimal(value) for day, value in points.items()}
    )


def test_the_high_between_reads_the_largest_value_inside_the_window():
    values = {
        date(2020, 1, 2): Decimal(100),
        date(2020, 6, 1): Decimal(150),
        date(2021, 1, 4): Decimal(120),
    }
    history = IndicatorHistory(sorted(values), values)

    assert history.high_between(date(2020, 1, 1), date(2021, 1, 4)) == Decimal(150)
    assert history.high_between(date(2020, 7, 1), date(2021, 1, 4)) == Decimal(120)
    assert history.high_between(date(2020, 1, 2), date(2020, 1, 2)) == Decimal(100)
    assert history.high_between(date(2020, 2, 1), date(2020, 5, 1)) is None


def test_the_drawdown_measures_the_fall_from_the_twelve_month_high(
    indicators: SetIndicator,
):
    ibov(
        indicators,
        {
            date(2020, 1, 2): "100",
            date(2020, 6, 1): "200",
            date(2020, 12, 1): "160",
        },
    )

    assert stocks_drawdown(date(2020, 12, 1)) == Decimal("0.2")
    assert stocks_drawdown(date(2020, 6, 1)) == 0


def test_the_high_older_than_365_days_leaves_the_window(indicators: SetIndicator):
    ibov(
        indicators,
        {
            date(2020, 1, 2): "300",
            date(2020, 6, 1): "200",
            date(2021, 1, 4): "160",
        },
    )

    # O topo de 300 tem mais de 365 dias em 2021-01-04: o topo vale 200
    assert date(2021, 1, 4) - date(2020, 1, 2) > timedelta(days=365)
    assert stocks_drawdown(date(2021, 1, 4)) == Decimal("0.2")


def test_the_high_of_exactly_365_days_ago_is_still_in_the_window(
    indicators: SetIndicator,
):
    day = date(2021, 1, 4)
    ibov(indicators, {day - timedelta(days=365): "200", day: "160"})

    assert stocks_drawdown(day) == Decimal("0.2")


def test_the_drawdown_is_null_where_the_series_does_not_cover(
    indicators: SetIndicator,
):
    assert stocks_drawdown(date(2020, 1, 2)) is None


# =========================
# A política do Servidor-bot, sem o motor
# =========================


@pytest.mark.parametrize(
    ("drawdown", "has_payroll", "expected"),
    [
        (Decimal("0.20"), False, PayrollMove.TAKE),
        (Decimal("0.35"), False, PayrollMove.TAKE),
        (Decimal("0.19"), False, None),
        (Decimal("0"), False, None),
        (Decimal("0.20"), True, None),
        (Decimal("0.10"), True, None),
        (Decimal("0.05"), True, None),
        (Decimal("0.049"), True, PayrollMove.PAY_OFF),
        (Decimal("0"), True, PayrollMove.PAY_OFF),
        (None, False, None),
        (None, True, None),
    ],
)
def test_the_policy_takes_at_minus_twenty_and_pays_off_under_five(
    drawdown, has_payroll, expected
):
    assert payroll_policy(drawdown, has_payroll) is expected


def test_the_policy_amount_is_what_half_the_free_margin_sustains_in_24_months():
    rate = Decimal("0.12")
    margin = Decimal(1000)

    amount = payroll_amount(margin, rate)

    assert installment(amount, rate, 24) <= margin / 2
    assert installment(amount + Decimal(10), rate, 24) > margin / 2
    assert payroll_amount(Decimal(0), rate) == 0


def test_the_quote_delivers_the_debt_leverage_and_margin_after_signing(payroll_engine):
    book = payroll_engine.credit_book
    book.contract_payroll(PLAYER, Decimal(4000), 12, SALARY)
    debt = book.debt(PLAYER, START)

    quote = build_payroll_quote(book, PLAYER, START, Decimal(1000), 12, SALARY)

    assert quote.debt_after == debt + Decimal(1000)
    assert quote.leverage_after == quote.debt_after / book.networth(PLAYER, debt)
    assert quote.margin_free_after == quote.margin_free - quote.installment


def test_the_margin_left_by_a_quote_that_does_not_fit_is_zero(payroll_engine):
    book = payroll_engine.credit_book

    quote = build_payroll_quote(book, PLAYER, START, Decimal(50000), 12, SALARY)

    assert quote.margin_free_after == 0


def test_the_quote_schedule_follows_the_turns_that_collect_the_installments(
    payroll_engine,
):
    book = payroll_engine.credit_book

    quote = build_payroll_quote(book, PLAYER, START, Decimal(3000), 6, SALARY)

    first = payroll_first_collection(START)
    assert [row.number for row in quote.schedule] == [1, 2, 3, 4, 5, 6]
    assert quote.schedule[0].due_date == first
    assert quote.schedule[1].due_date == next_month_turn(first)
    assert {row.payment for row in quote.schedule[:-1]} == {quote.installment}
    assert quote.schedule[-1].balance == 0


def test_the_collection_notifies_the_paid_installment_only_at_low_speed(
    payroll_engine,
    notices,  # noqa: F811
):
    book = payroll_engine.credit_book
    book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)

    payroll_engine.current_date = FIRST_TURN
    book.collect_payroll(PLAYER, 8)
    assert "credit_installment_paid" not in notices

    payroll_engine.current_date = next_month_turn(FIRST_TURN)
    book.collect_payroll(PLAYER, 1)
    assert notices.count("credit_installment_paid") == 1


def test_the_monthly_summary_counts_the_consignado_installments(
    payroll_engine,
    notices,  # noqa: F811
):
    book = payroll_engine.credit_book
    book.contract_payroll(PLAYER, Decimal(5000), 12, SALARY)
    payroll_engine.current_date = FIRST_TURN
    book.collect_payroll(PLAYER, 8)

    book.monthly_summary([PLAYER], date(2020, 3, 31), 8)

    assert notices == ["credit_monthly_summary"]
