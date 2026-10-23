"""
Estado de um empréstimo em Price, sem banco: o que falta pagar e o que cada
decisão (parcela, amortização, quitação) faz com isso.

O ciclo corrente começa na parcela `cycles_done` (ou na assinatura, em 0) com
`cycle_balance` e vence na parcela seguinte. O ciclo avança no vencimento, paga
ou não: a parcela que não foi paga vira um atraso à parte, e o saldo segue o
cronograma.
"""

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

from backend.core.enum import PrepaymentMode
from backend.features.credit.price import (
    ZERO,
    ScheduleRow,
    add_months,
    grown_balance,
    installment,
    money,
    monthly_rate,
    schedule,
)


@dataclass(frozen=True)
class LoanState:
    contract_date: date
    annual_rate: Decimal
    # Saldo no início do ciclo corrente
    cycle_balance: Decimal
    # Parcelas cujo vencimento já passou, pagas ou não
    cycles_done: int
    # Parcelas que faltam vencer, a do ciclo corrente incluída
    remaining: int
    installment: Decimal

    @classmethod
    def sign(
        cls, contract_date: date, principal: Decimal, annual_rate: Decimal, months: int
    ) -> "LoanState":
        return cls(
            contract_date=contract_date,
            annual_rate=annual_rate,
            cycle_balance=principal,
            cycles_done=0,
            remaining=months,
            installment=installment(principal, annual_rate, months),
        )

    @property
    def is_closed(self) -> bool:
        return self.remaining == 0

    @property
    def cycle_start(self) -> date:
        return add_months(self.contract_date, self.cycles_done)

    @property
    def next_due(self) -> date:
        return add_months(self.contract_date, self.cycles_done + 1)

    @property
    def next_number(self) -> int:
        return self.cycles_done + 1

    def balance_on(self, day: date) -> Decimal:
        """Saldo devedor do dia: o que quitaria o empréstimo agora."""
        if self.is_closed:
            return ZERO
        return grown_balance(
            self.cycle_balance,
            self.annual_rate,
            self.cycle_start,
            self.next_due,
            day,
        )

    def due_amount(self) -> Decimal:
        """Valor da parcela que vence; a última paga o que sobra do saldo."""
        owed = self.cycle_balance * (1 + monthly_rate(self.annual_rate))
        if self.remaining == 1 or owed <= self.installment:
            return money(owed)
        return self.installment

    def advance(self) -> "LoanState":
        """O vencimento passou: o ciclo seguinte parte do saldo que a parcela deixa."""
        owed = self.cycle_balance * (1 + monthly_rate(self.annual_rate))
        is_last = self.remaining == 1 or owed <= self.installment
        return replace(
            self,
            cycle_balance=ZERO if is_last else owed - self.installment,
            cycles_done=self.cycles_done + 1,
            remaining=0 if is_last else self.remaining - 1,
        )

    def close(self) -> "LoanState":
        """Quitação: nada mais a vencer."""
        return replace(self, cycle_balance=ZERO, remaining=0)

    def schedule(self) -> list[ScheduleRow]:
        """Cronograma das parcelas que faltam, a partir do ciclo corrente."""
        if self.is_closed:
            return []
        return schedule(
            self.cycle_balance,
            self.annual_rate,
            self.installment,
            self.contract_date,
            first_number=self.next_number,
            count=self.remaining,
        )

    def prepay(self, amount: Decimal, day: date, mode: PrepaymentMode) -> "LoanState":
        """
        Abate `amount` do saldo do dia. O ciclo mantém as datas: o abatimento
        entra no saldo do início do ciclo descontado do juro que já correu.
        """
        grown = self.balance_on(day) / self.cycle_balance
        cycle_balance = self.cycle_balance - amount / grown
        if mode is PrepaymentMode.REDUCE_INSTALLMENT:
            return replace(
                self,
                cycle_balance=cycle_balance,
                installment=installment(
                    cycle_balance, self.annual_rate, self.remaining
                ),
            )

        rows = schedule(
            cycle_balance,
            self.annual_rate,
            self.installment,
            self.contract_date,
            first_number=self.next_number,
        )
        return replace(self, cycle_balance=cycle_balance, remaining=len(rows))

    def interest_saved(self, prepaid: "LoanState", amount: Decimal) -> Decimal:
        """Juro que a amortização `amount` poupa: o que se pagaria menos o que se paga agora e depois."""
        before = sum((row.payment for row in self.schedule()), ZERO)
        after = amount + sum((row.payment for row in prepaid.schedule()), ZERO)
        return before - after
