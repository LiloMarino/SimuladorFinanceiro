"""Livro de crédito no motor: contratação, vencimento, atraso, nota e retomada."""

from __future__ import annotations

import threading
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import (
    CreditEventType,
    CreditGrade,
    IndicatorSeries,
    PendingSeverity,
    PendingType,
    PrepaymentMode,
)
from backend.core.exceptions import InsufficentCashError
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.utils import format_money
from backend.features.credit.credit_book import CreditBook
from backend.features.credit.overview import build_overview, build_quote
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.statistics.credit import credit_standing
from tests.conftest import SetIndicator
from tests.fakes import FakeSimulationEngine, client, daily_series

PLAYER = client("player")
START = date(2020, 1, 6)
STARTING_CASH = Decimal(10000)


class CreditEngine(FakeSimulationEngine):
    """Motor em memória com o que o livro de crédito pede: caixa, ativos e a renda fixa à venda."""

    def __init__(self, history: list[PatrimonialHistoryDTO] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.fixed_income_market = FixedIncomeMarket(1, date(2030, 1, 1))
        self.snapshots = history if history is not None else []
        self.credit_book = CreditBook(
            self, threading.RLock(), history=lambda _client_id: self.snapshots
        )

    def receive_loan(self, client_id: uuid.UUID, amount: Decimal) -> None:
        self.add_cash(client_id, amount)

    def pay_loan(self, client_id: uuid.UUID, amount: Decimal) -> None:
        self.add_cash(client_id, -amount)

    def assets_value(self, client_id: uuid.UUID) -> Decimal:
        return self.cash[client_id]


@pytest.fixture
def stored_events(monkeypatch: pytest.MonkeyPatch) -> list[CreditEventDTO]:
    """O que o repositório devolve na retomada; os testes o alimentam com os eventos gravados."""
    stored: list[CreditEventDTO] = []
    monkeypatch.setattr(
        repository.credit, "get_events", lambda _simulation_id, _user_id: list(stored)
    )
    return stored


@pytest.fixture
def notices(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Os avisos de crédito enviados ao jogador, pelo nome do evento."""
    sent: list[str] = []
    monkeypatch.setattr(
        "backend.features.credit.credit_book.notify",
        lambda name, _payload, to=None: sent.append(name),
    )
    return sent


@pytest.fixture
def engine(captured_events, indicators: SetIndicator, stored_events) -> CreditEngine:
    indicators(IndicatorSeries.SELIC, daily_series(START, date(2023, 12, 31), "0.0004"))
    return CreditEngine(cash={PLAYER: STARTING_CASH}, current_date=START)


def credit_events(captured_events) -> list[CreditEventDTO]:
    return [e for e in captured_events if isinstance(e, CreditEventDTO)]


def run_until(engine: CreditEngine, end: date, speed: int = 1) -> None:
    """Corre os dias até `end`, liquidando os vencimentos como o tick faz."""
    day = engine.current_date
    while day < end:
        day += timedelta(days=1)
        engine.current_date = day
        engine.credit_book.process_due([PLAYER], day, speed)


def test_contract_credits_cash_and_records_the_event(engine, captured_events):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)

    assert engine.get_cash(PLAYER) == Decimal(15000)
    assert engine.credit_book.debt(PLAYER, START) == Decimal(5000)
    assert loan.number == 1
    [event] = credit_events(captured_events)
    assert event.event_type is CreditEventType.CONTRACT
    assert event.amount == Decimal(5000)
    assert event.term_months == 12
    assert event.annual_rate == loan.annual_rate


def test_contract_beyond_the_limit_is_refused(engine):
    with pytest.raises(ConflictError):
        engine.credit_book.contract(PLAYER, Decimal(10001), 12)


def test_installment_is_debited_on_the_due_date(engine, captured_events, notices):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)
    installment = loan.state.due_amount()
    due = loan.state.next_due

    run_until(engine, due - timedelta(days=1))
    assert engine.get_cash(PLAYER) == Decimal(15000)

    run_until(engine, due)
    assert engine.get_cash(PLAYER) == Decimal(15000) - installment
    assert loan.paid_installments == 1
    assert credit_events(captured_events)[-1].event_type is (
        CreditEventType.INSTALLMENT_PAID
    )
    assert "credit_installment_paid" in notices


def test_fast_speed_skips_the_installment_notice(engine, notices):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)

    run_until(engine, loan.state.next_due, speed=8)

    assert "credit_installment_paid" not in notices


def test_installment_without_cash_becomes_overdue(engine, captured_events, notices):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(0)
    installment = loan.state.due_amount()

    run_until(engine, loan.state.next_due)

    assert engine.get_cash(PLAYER) == Decimal(0)
    assert [o.amount for o in loan.overdue] == [installment]
    assert loan.paid_installments == 0
    assert credit_events(captured_events)[-1].event_type is (
        CreditEventType.INSTALLMENT_LATE
    )
    assert "credit_installment_late" in notices
    assert engine.credit_book.alert(PLAYER, engine.current_date)


def test_warning_comes_once_when_the_cash_does_not_cover_the_installment(
    engine, notices
):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(10)
    due = loan.state.next_due

    run_until(engine, due - timedelta(days=7))
    run_until(engine, due - timedelta(days=3))

    assert notices.count("credit_installment_warning") == 1


def test_overdue_installment_is_a_pending_with_the_loan_to_pay(engine):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(0)
    installment = loan.state.due_amount()

    run_until(engine, loan.state.next_due)

    [pending] = engine.credit_book.pending(PLAYER, engine.current_date)
    assert pending.type is PendingType.OVERDUE_INSTALLMENT
    assert pending.severity is PendingSeverity.SEVERE
    assert pending.loan_id == loan.loan_id
    assert pending.detail.startswith(f"Empréstimo 1 · {format_money(installment)}")
    assert pending.key == f"OVERDUE_INSTALLMENT:{loan.loan_id}"


def test_overdue_pending_goes_away_when_the_installment_is_paid(engine):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(0)
    run_until(engine, loan.state.next_due)
    engine.cash[PLAYER] = Decimal(10000)

    engine.credit_book.pay_overdue(PLAYER, loan.loan_id)

    assert engine.credit_book.pending(PLAYER, engine.current_date) == []


def test_short_cash_is_a_warning_only_inside_the_seven_days_before_the_due_date(
    engine,
):
    loan = engine.credit_book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(10)
    due = loan.state.next_due

    assert engine.credit_book.pending(PLAYER, due - timedelta(days=8)) == []

    [pending] = engine.credit_book.pending(PLAYER, due - timedelta(days=7))
    assert pending.type is PendingType.CASH_SHORT
    assert pending.severity is PendingSeverity.WARNING
    assert pending.key == "CASH_SHORT"
    assert f"{due:%d/%m}" in pending.detail

    engine.cash[PLAYER] = Decimal(20000)
    assert engine.credit_book.pending(PLAYER, due - timedelta(days=7)) == []


def test_late_installment_drops_the_grade_at_once(engine):
    book = engine.credit_book
    assert book.score(PLAYER, START).grade is CreditGrade.AAA

    loan = book.contract(PLAYER, Decimal(1000), 12)
    engine.cash[PLAYER] = Decimal(0)
    run_until(engine, loan.state.next_due)
    assert book.score(PLAYER, engine.current_date).grade is CreditGrade.AAA
    run_until(engine, loan.state.next_due)

    # Duas parcelas atrasadas: 100 menos 20 pontos
    assert len(loan.overdue) == 2
    assert book.score(PLAYER, engine.current_date).grade is CreditGrade.AA


def test_leverage_and_volatility_count_only_after_the_month_closes(engine):
    book = engine.credit_book
    before = book.score(PLAYER, START)

    engine.snapshots.append(
        PatrimonialHistoryDTO(
            snapshot_date=date(2019, 12, 30),
            total_networth=Decimal(1000),
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_cash=Decimal(2000),
            total_contribution=Decimal(0),
            total_debt=Decimal(1000),
        )
    )
    assert book.score(PLAYER, START) == before

    book.close_month([PLAYER], START)

    # Dívida igual ao patrimônio: alavancagem 100%, zero pontos nessa parte
    assert book.score(PLAYER, START).leverage_points == Decimal(0)


def volatile_history() -> list[PatrimonialHistoryDTO]:
    """Pregões que oscilam muito e fecham com a dívida maior que o patrimônio."""
    return [
        PatrimonialHistoryDTO(
            snapshot_date=date(2019, 12, 1) + timedelta(days=i),
            total_networth=Decimal(1000 if i % 2 else 2000),
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_cash=Decimal(2000),
            total_contribution=Decimal(0),
            total_debt=Decimal(2000),
        )
        for i in range(25)
    ]


def test_grade_d_blocks_new_credit(engine):
    engine.snapshots.extend(volatile_history())
    engine.credit_book.close_month([PLAYER], START)
    # Uma parcela atrasada no último ano tira 10 dos 30 pontos de pagamento
    engine.credit_book.client(PLAYER).events.append(
        CreditEventDTO(
            simulation_id=1,
            user_id=1,
            event_date=START,
            loan_id=uuid.uuid4(),
            event_type=CreditEventType.INSTALLMENT_LATE,
            amount=Decimal(100),
        )
    )

    offer = engine.credit_book.offer(PLAYER, START)

    assert offer.score.grade is CreditGrade.D
    assert offer.annual_rate is None
    assert offer.max_amount == 0
    with pytest.raises(ConflictError):
        engine.credit_book.contract(PLAYER, Decimal(100), 12)


def test_pay_overdue_charges_fee_and_late_interest(engine):
    book = engine.credit_book
    loan = book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(0)
    run_until(engine, loan.state.next_due)
    overdue = loan.overdue[0]
    engine.add_cash(PLAYER, Decimal(10000))
    run_until(engine, overdue.due_date + timedelta(days=6))
    # O caixa cobre as próximas parcelas; só a em atraso fica
    charges = overdue.charges(engine.current_date)

    cash_before = engine.get_cash(PLAYER)
    total = book.pay_overdue(PLAYER, loan.loan_id)

    assert total == charges.total
    assert total > overdue.amount
    assert engine.get_cash(PLAYER) == cash_before - total
    assert loan.overdue == []


def test_payoff_pays_the_balance_of_the_day_and_closes_the_loan(
    engine, captured_events, notices
):
    book = engine.credit_book
    loan = book.contract(PLAYER, Decimal(5000), 12)
    run_until(engine, START + timedelta(days=60))
    owed = loan.payoff_on(engine.current_date)
    cash_before = engine.get_cash(PLAYER)

    paid = book.payoff(PLAYER, loan.loan_id)

    assert paid == owed
    assert engine.get_cash(PLAYER) == cash_before - owed
    assert book.loans(PLAYER) == []
    assert credit_events(captured_events)[-1].event_type is CreditEventType.PAYOFF
    assert "credit_loan_paid_off" in notices


def test_payoff_without_cash_is_refused(engine):
    book = engine.credit_book
    loan = book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(100)

    with pytest.raises(InsufficentCashError):
        book.payoff(PLAYER, loan.loan_id)


def test_prepayment_modes_shorten_the_term_or_cut_the_installment(engine):
    book = engine.credit_book
    shorter = book.contract(PLAYER, Decimal(5000), 24)
    smaller = book.contract(PLAYER, Decimal(1000), 24)
    installment = shorter.state.due_amount()

    book.prepay(PLAYER, shorter.loan_id, Decimal(2000), PrepaymentMode.SHORTEN_TERM)
    book.prepay(
        PLAYER, smaller.loan_id, Decimal(500), PrepaymentMode.REDUCE_INSTALLMENT
    )

    assert shorter.state.due_amount() == installment
    assert shorter.state.remaining < 24
    assert smaller.state.remaining == 24
    assert smaller.state.due_amount() < Decimal(1000) / 24 * 2


def test_resume_rebuilds_the_same_debt_as_the_live_game(
    engine, captured_events, stored_events
):
    book = engine.credit_book
    first = book.contract(PLAYER, Decimal(5000), 12)
    second = book.contract(PLAYER, Decimal(2000), 18)
    run_until(engine, START + timedelta(days=75))
    book.prepay(PLAYER, first.loan_id, Decimal(800), PrepaymentMode.SHORTEN_TERM)
    engine.cash[PLAYER] = Decimal(0)
    run_until(engine, START + timedelta(days=140))
    engine.add_cash(PLAYER, Decimal(20000))
    book.pay_overdue(PLAYER, first.loan_id)
    run_until(engine, START + timedelta(days=200))
    book.payoff(PLAYER, second.loan_id)
    run_until(engine, START + timedelta(days=320))

    stored_events.extend(credit_events(captured_events))
    resumed = CreditEngine(
        cash={PLAYER: engine.get_cash(PLAYER)}, current_date=engine.current_date
    )

    live_book, resumed_book = book, resumed.credit_book
    assert [loan.number for loan in resumed_book.loans(PLAYER)] == [
        loan.number for loan in live_book.loans(PLAYER)
    ]
    for day in (engine.current_date, engine.current_date + timedelta(days=40)):
        assert resumed_book.debt(PLAYER, day) == live_book.debt(PLAYER, day)
    for live, back in zip(
        live_book.loans(PLAYER), resumed_book.loans(PLAYER), strict=True
    ):
        assert back.state == live.state
        assert back.overdue == live.overdue
    assert resumed_book.score(PLAYER, engine.current_date) == live_book.score(
        PLAYER, engine.current_date
    )


def test_overview_reads_the_loans_and_the_offer(engine):
    book = engine.credit_book
    book.contract(PLAYER, Decimal(5000), 12)

    overview = build_overview(book, PLAYER, engine.current_date)

    assert overview.debt == Decimal(5000)
    assert overview.open_loans == 1
    assert overview.networth == Decimal(10000)
    assert overview.rating.grade is CreditGrade.AAA
    assert overview.offer.available
    assert overview.loans[0].total_installments == 12
    assert overview.upcoming[0].installment_number == 1


def test_negative_networth_leaves_leverage_unbounded_in_overview_and_quote(engine):
    book = engine.credit_book
    book.contract(PLAYER, Decimal(5000), 12)
    # Caixa abaixo da dívida: patrimônio líquido negativo
    engine.cash[PLAYER] = Decimal(1000)

    overview = build_overview(book, PLAYER, engine.current_date)
    quote = build_quote(book, PLAYER, engine.current_date, Decimal(1000), 12)

    assert overview.networth == Decimal(-4000)
    assert overview.leverage is None
    assert quote.leverage_before is None
    assert quote.leverage_after is None
    assert quote.projected_points <= 100


def test_zero_networth_leaves_leverage_unbounded_in_quote(engine):
    book = engine.credit_book
    book.contract(PLAYER, Decimal(5000), 12)
    engine.cash[PLAYER] = Decimal(5000)

    quote = build_quote(book, PLAYER, engine.current_date, Decimal(1000), 12)

    assert quote.leverage_before is None
    assert quote.leverage_after is None


def test_standing_reads_debt_delinquency_and_interest_from_the_events(
    engine, captured_events
):
    book = engine.credit_book
    loan = book.contract(PLAYER, Decimal(5000), 12)
    run_until(engine, START + timedelta(days=65))
    engine.cash[PLAYER] = Decimal(0)
    run_until(engine, START + timedelta(days=100))
    snapshot = PatrimonialHistoryDTO(
        snapshot_date=engine.current_date,
        total_networth=Decimal(4000),
        total_equity=Decimal(0),
        total_fixed=Decimal(0),
        total_cash=Decimal(0),
        total_contribution=Decimal(0),
        total_debt=book.debt(PLAYER, engine.current_date),
    )

    standing = credit_standing(credit_events(captured_events), [snapshot])

    assert standing.has_borrowed
    assert standing.delinquent
    assert standing.debt == book.debt(PLAYER, engine.current_date)
    assert standing.paid_installments == 2
    assert standing.late_installments == len(loan.overdue) == 1
    assert standing.cost_of_debt == loan.annual_rate
    # Duas parcelas pagas: o que passa do principal amortizado é juro
    assert 0 < standing.interest_paid < 2 * loan.state.installment
    assert standing.leverage == standing.debt / Decimal(4000)
