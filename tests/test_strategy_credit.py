"""As operações de crédito das estratégias dentro da partida: registro com motivo, recusa e reserva de parcelas."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

import pytest

from backend.core.enum import StrategyAction, StrategyGroup, StrategyOrderStatus
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.context import StrategyContext
from backend.features.strategy.registry import STRATEGIES
from tests.test_simulation_loader import started  # noqa: F401
from tests.test_strategy_engine import log_of, match  # noqa: F401

Step = Callable[[StrategyContext], None]


class Scripted(BaseStrategy):
    """Executa, a cada dia, o próximo passo da fila `STEPS`; sem passo, não faz nada."""

    key = "scripted"
    name = "Roteiro"
    summary = "Teste"
    description = "Teste"
    group = StrategyGroup.TACTIC

    def next(self, ctx: StrategyContext, params) -> None:
        if STEPS:
            STEPS.pop(0)(ctx)


STEPS: list[Step] = []


@pytest.fixture
def credit_match(match, monkeypatch: pytest.MonkeyPatch):  # noqa: F811
    monkeypatch.setitem(STRATEGIES, Scripted.key, Scripted)
    STEPS.clear()
    sim, ana, bia = match
    sim.set_my_strategy(ana, Scripted.key, {})
    yield sim, ana, bia
    STEPS.clear()


def credit_lines(sim, user):
    # O registro lista o mais novo primeiro; aqui as linhas vêm na ordem em que aconteceram
    return [r for r in reversed(log_of(sim, user)) if r.action in CREDIT]


CREDIT = {
    StrategyAction.TAKE_LOAN,
    StrategyAction.PREPAY_LOAN,
    StrategyAction.PAYOFF_LOAN,
    StrategyAction.PAY_OVERDUE,
}


def test_taking_a_loan_runs_the_screen_operation_and_logs_the_reason(credit_match):
    sim, ana, _ = credit_match
    cash = sim.get_cash(ana.client_id)
    STEPS.append(lambda ctx: ctx.take_loan(Decimal(5000), 24, "Faltava caixa"))

    sim.next_tick()

    [line] = credit_lines(sim, ana)
    assert line.action is StrategyAction.TAKE_LOAN
    assert line.status is StrategyOrderStatus.EXECUTED
    assert (line.price, line.term_months) == (Decimal(5000), 24)
    assert line.quantity is None and line.loan_number is None
    assert line.reason == "Faltava caixa"
    assert line.annual_rate is not None and line.annual_rate > 0
    [loan] = sim._engine.credit_book.loans(ana.client_id)
    assert loan.annual_rate == line.annual_rate
    assert sim.get_cash(ana.client_id) > cash


def test_prepaying_paying_off_and_the_overdue_each_log_a_line_with_the_reason(
    credit_match,
):
    sim, ana, _ = credit_match
    STEPS.append(lambda ctx: ctx.take_loan(Decimal(5000), 24, "Tomou"))

    def prepay(ctx: StrategyContext) -> None:
        [loan] = ctx.loans
        ctx.prepay_loan(loan.id, Decimal(1000), "Amortizou")

    def payoff(ctx: StrategyContext) -> None:
        [loan] = ctx.loans
        ctx.payoff_loan(loan.id, "Quitou")

    STEPS.extend([prepay, payoff])

    for _ in range(3):
        sim.next_tick()

    lines = credit_lines(sim, ana)
    assert [(r.action, r.status, r.reason) for r in lines] == [
        (StrategyAction.TAKE_LOAN, StrategyOrderStatus.EXECUTED, "Tomou"),
        (StrategyAction.PREPAY_LOAN, StrategyOrderStatus.EXECUTED, "Amortizou"),
        (StrategyAction.PAYOFF_LOAN, StrategyOrderStatus.EXECUTED, "Quitou"),
    ]
    # Amortização e quitação apontam o empréstimo pelo número; a quantidade fica nula
    assert lines[1].loan_number == lines[2].loan_number == 1
    assert lines[1].quantity is None and lines[2].quantity is None
    assert lines[1].term_months is None and lines[2].term_months is None
    assert lines[1].price == Decimal(1000)
    assert lines[2].price is not None and lines[2].price > 0
    assert sim._engine.credit_book.loans(ana.client_id) == []


def test_a_refused_credit_operation_is_logged_and_the_strategy_keeps_running(
    credit_match,
):
    sim, ana, _ = credit_match

    def refused(ctx: StrategyContext) -> None:
        ctx.take_loan(Decimal(999999), 24, "Quis demais")

    def overdue_of_a_loan_in_day(ctx: StrategyContext) -> None:
        [loan] = ctx.loans
        ctx.pay_overdue(loan.id, "Sem atraso para pagar")

    STEPS.extend(
        [
            refused,
            lambda ctx: ctx.take_loan(Decimal(5000), 24, "Tomou"),
            overdue_of_a_loan_in_day,
        ]
    )

    for _ in range(3):
        sim.next_tick()

    lines = credit_lines(sim, ana)
    assert [r.status for r in lines] == [
        StrategyOrderStatus.REFUSED,
        StrategyOrderStatus.EXECUTED,
        StrategyOrderStatus.REFUSED,
    ]
    assert [r.reason for r in lines] == [
        "Quis demais",
        "Tomou",
        "Sem atraso para pagar",
    ]
    assert lines[0].detail and lines[2].detail
    assert lines[0].price == Decimal(999999)
    assert sim.get_my_strategy(ana).error is None
    assert sim.get_my_strategy(ana).active is not None


def test_the_cash_of_the_context_holds_back_the_installments_of_the_next_30_days(
    credit_match,
):
    sim, ana, _ = credit_match
    sim.contract_loan(ana, ana.client_id, Decimal(5000), 6)
    seen: list[tuple[Decimal, Decimal, Decimal]] = []

    def probe(ctx: StrategyContext) -> None:
        engine = sim._engine
        reserve = engine.credit_book.installments_due(
            ana.client_id, engine.current_date, 30
        )
        seen.append((ctx.cash, engine.get_cash(ana.client_id), reserve))

    STEPS.append(probe)

    sim.next_tick()

    [(ctx_cash, engine_cash, reserve)] = seen
    assert reserve > 0
    assert ctx_cash == max(engine_cash - reserve, 0)
    assert ctx_cash < engine_cash
