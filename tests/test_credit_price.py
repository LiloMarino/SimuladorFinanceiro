from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import PrepaymentMode
from backend.features.credit.loan import LoanState
from backend.features.credit.price import (
    add_months,
    installment,
    overdue_charges,
    schedule,
    total_interest,
)

D = Decimal
CONTRACT = date(2020, 3, 14)


def test_installment_matches_board():
    assert installment(D(50000), D("0.0925"), 24) == D("2281.48")


def test_schedule_total_interest_matches_board():
    state = LoanState.sign(CONTRACT, D(50000), D("0.0925"), 24)
    rows = state.schedule()
    assert len(rows) == 24
    assert total_interest(rows, D(50000)) == pytest.approx(D("4755.40"), abs=D("0.05"))
    assert rows[0].interest == D("369.98")
    assert rows[0].due_date == date(2020, 4, 14)
    assert rows[-1].balance == D("0.00")


def test_schedule_payment_is_constant_until_the_last():
    rows = schedule(
        D(10000), D("0.12"), installment(D(10000), D("0.12"), 12), CONTRACT, count=12
    )
    assert {row.payment for row in rows[:-1]} == {rows[0].payment}
    assert abs(rows[-1].payment - rows[0].payment) < D("0.20")


def test_add_months_clamps_to_month_end():
    assert add_months(date(2020, 1, 31), 1) == date(2020, 2, 29)
    assert add_months(date(2020, 1, 31), 2) == date(2020, 3, 31)
    assert add_months(date(2020, 3, 14), -12) == date(2019, 3, 14)


def test_overdue_charges_match_board():
    charges = overdue_charges(D("2769.42"), date(2020, 4, 5), date(2020, 4, 11))
    assert charges.fee == D("55.39")
    assert charges.interest == D("5.54")
    assert charges.total == D("2830.35")


def test_overdue_charges_on_due_date_only_fee():
    charges = overdue_charges(D(1000), date(2020, 4, 5), date(2020, 4, 5))
    assert charges.interest == D("0.00")
    assert charges.total == D("1020.00")


def _loan_after_14_payments() -> LoanState:
    state = LoanState.sign(date(2019, 1, 10), D(80000), D("0.095"), 36)
    for _ in range(14):
        state = state.advance()
    return state


def test_balance_after_installments_matches_board():
    state = _loan_after_14_payments()
    assert state.remaining == 22
    assert state.installment == D("2548.07")
    # A parcela é debitada em centavos, então o saldo real fica a centavos da conta exata
    assert state.cycle_balance == pytest.approx(D("51447.23"), abs=D("0.02"))


def test_balance_grows_daily_inside_the_cycle():
    state = LoanState.sign(CONTRACT, D(50000), D("0.0925"), 24)
    assert state.balance_on(CONTRACT) == D(50000)
    midway = state.balance_on(date(2020, 3, 29))
    assert D(50000) < midway < state.balance_on(date(2020, 4, 14))
    # No vencimento o saldo fecha a taxa mensal cheia
    assert round(state.balance_on(date(2020, 4, 14)), 2) == D("50369.98")


def test_shorten_term_prepayment_matches_board():
    state = _loan_after_14_payments()
    day = state.cycle_start
    prepaid = state.prepay(D(20000), day, PrepaymentMode.SHORTEN_TERM)
    assert prepaid.remaining == 14
    assert prepaid.installment == D("2548.07")
    saved = state.interest_saved(prepaid, D(20000))
    assert saved == pytest.approx(D("2912.89"), abs=D("0.05"))


def test_reduce_installment_prepayment_matches_board():
    state = _loan_after_14_payments()
    prepaid = state.prepay(
        D(20000), state.cycle_start, PrepaymentMode.REDUCE_INSTALLMENT
    )
    assert prepaid.remaining == 22
    assert prepaid.installment == D("1557.51")
    saved = state.interest_saved(prepaid, D(20000))
    assert saved == pytest.approx(D("1792.33"), abs=D("0.10"))


def test_prepayment_mid_cycle_keeps_balance_continuous():
    state = _loan_after_14_payments()
    day = date(2020, 3, 1)
    before = state.balance_on(day)
    prepaid = state.prepay(D(10000), day, PrepaymentMode.SHORTEN_TERM)
    assert prepaid.balance_on(day) == pytest.approx(before - D(10000), abs=D("0.001"))


def test_advance_to_the_end_closes_the_loan():
    state = LoanState.sign(CONTRACT, D(6000), D("0.10"), 6)
    for _ in range(6):
        assert not state.is_closed
        state = state.advance()
    assert state.is_closed
    assert state.balance_on(date(2021, 1, 1)) == 0


def test_payoff_is_the_balance_of_the_day():
    state = LoanState.sign(CONTRACT, D(50000), D("0.0925"), 24)
    # Quitar antes do vencimento não cobra o juro futuro: o saldo do dia é menor que o do vencimento
    assert state.balance_on(date(2020, 3, 20)) < state.cycle_balance * D("1.0074")
