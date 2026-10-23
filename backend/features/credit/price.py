"""
Tabela Price: parcela fixa, juro que cai e amortização que sobe a cada mês.

Cálculo puro, sem banco nem relógio. O juro anual vira taxa mensal equivalente
(1 + anual)^(1/12) - 1. O saldo cresce todo dia corrido entre uma parcela e a
próxima e fecha a taxa mensal cheia no vencimento, então a tabela bate com a
Price clássica nas datas das parcelas.
"""

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal

from backend.features.credit.rules import (
    LATE_FEE,
    LATE_INTEREST_PER_MONTH,
    MONTH_DAYS,
)

CENT = Decimal("0.01")
ZERO = Decimal(0)


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_EVEN)


def add_months(day: date, months: int) -> date:
    """Mesmo dia `months` meses depois; mês mais curto cai no último dia dele."""
    index = day.month - 1 + months
    year, month = day.year + index // 12, index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def monthly_rate(annual_rate: Decimal) -> Decimal:
    return (1 + annual_rate) ** (Decimal(1) / 12) - 1


def installment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    """Parcela fixa da Price: P·i / (1 - (1+i)^-n)."""
    rate = monthly_rate(annual_rate)
    return money(principal * rate / (1 - (1 + rate) ** -months))


def grown_balance(
    cycle_balance: Decimal,
    annual_rate: Decimal,
    cycle_start: date,
    next_due: date,
    day: date,
) -> Decimal:
    """
    Saldo no dia `day` de um ciclo que começa em `cycle_start` com `cycle_balance`
    e vence em `next_due`: a fração do ciclo já corrida compõe a taxa mensal.
    """
    cycle_days = (next_due - cycle_start).days
    elapsed = min(max((day - cycle_start).days, 0), cycle_days)
    return cycle_balance * (1 + monthly_rate(annual_rate)) ** (
        Decimal(elapsed) / cycle_days
    )


@dataclass(frozen=True)
class ScheduleRow:
    number: int
    due_date: date
    interest: Decimal
    principal: Decimal
    payment: Decimal
    balance: Decimal


def schedule(
    balance: Decimal,
    annual_rate: Decimal,
    payment: Decimal,
    contract_date: date,
    first_number: int = 1,
    count: int | None = None,
) -> list[ScheduleRow]:
    """
    Cronograma das parcelas que faltam, a partir de `balance` no início do ciclo
    da parcela `first_number`. A última paga o que sobra do saldo: com `count` é
    a parcela `first_number + count - 1`; sem `count` é a primeira em que a
    parcela cobre o saldo (prazo encurtado por amortização). O vencimento da
    parcela N é `contract_date` + N meses.
    """
    rate = monthly_rate(annual_rate)
    rows: list[ScheduleRow] = []
    number = first_number
    while True:
        owed = balance * (1 + rate)
        is_last = owed <= payment or (
            count is not None and number == first_number + count - 1
        )
        paid = owed if is_last else payment
        interest = balance * rate
        balance = owed - paid
        rows.append(
            ScheduleRow(
                number=number,
                due_date=add_months(contract_date, number),
                interest=money(interest),
                principal=money(paid - interest),
                payment=money(paid),
                balance=money(balance),
            )
        )
        if is_last:
            return rows
        number += 1


def total_interest(rows: list[ScheduleRow], principal: Decimal) -> Decimal:
    """Juro do prazo todo: o que se paga a mais que o principal."""
    return sum((row.payment for row in rows), ZERO) - principal


@dataclass(frozen=True)
class OverdueCharges:
    installment: Decimal
    fee: Decimal
    interest: Decimal

    @property
    def total(self) -> Decimal:
        return self.installment + self.fee + self.interest


def overdue_charges(amount: Decimal, due_date: date, today: date) -> OverdueCharges:
    """Parcela atrasada: a parcela, a multa de 2% (uma vez) e a mora pro rata dia."""
    days = max((today - due_date).days, 0)
    return OverdueCharges(
        installment=amount,
        fee=money(amount * LATE_FEE),
        interest=money(amount * LATE_INTEREST_PER_MONTH * days / MONTH_DAYS),
    )
