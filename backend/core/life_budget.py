"""Salário e despesa mensais da partida e a meta do viver de renda que sai deles."""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import annual_index_rate

MONTHS_PER_YEAR = 12
CENT = Decimal("0.01")


@dataclass(frozen=True)
class LifeBudget:
    """
    Salário e despesa mensais da partida. Com `inflation_adjusted`, os dois sobem
    pelo IPCA acumulado em 12 meses a cada aniversário da data de início, e a meta
    sobe junto.
    """

    monthly_salary: Decimal
    monthly_expense: Decimal
    # Fração do patrimônio retirada por ano (0.04 = regra dos 4%)
    withdrawal_rate: Decimal
    inflation_adjusted: bool
    start_date: date

    @classmethod
    def of(cls, settings: SimulationSettingsDTO) -> "LifeBudget":
        return cls(
            monthly_salary=settings.monthly_salary,
            monthly_expense=settings.monthly_expense,
            withdrawal_rate=settings.withdrawal_rate,
            inflation_adjusted=settings.inflation_adjusted,
            start_date=settings.start_date,
        )

    def salary_on(self, day: date) -> Decimal:
        return cents(self.monthly_salary * self._inflation_factor(day))

    def expense_on(self, day: date) -> Decimal:
        return cents(self.monthly_expense * self._inflation_factor(day))

    def readjustments(self, until: date) -> list[date]:
        """Os dias em que salário, despesa e meta sobem: o início e, com IPCA, cada aniversário."""
        if not self.inflation_adjusted:
            return [self.start_date]
        return [self.start_date, *_anniversaries(self.start_date, until)]

    def goal_on(self, day: date) -> Decimal:
        """O patrimônio que paga a despesa do ano retirando `withdrawal_rate` dele."""
        return MONTHS_PER_YEAR * self.expense_on(day) / self.withdrawal_rate

    def _inflation_factor(self, day: date) -> Decimal:
        if not self.inflation_adjusted:
            return Decimal(1)
        factor = Decimal(1)
        for anniversary in _anniversaries(self.start_date, day):
            factor *= 1 + annual_index_rate(IndicatorSeries.IPCA, anniversary)
        return factor


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)


def _anniversaries(start: date, day: date) -> list[date]:
    """Os aniversários de `start` até `day`, inclusive; 29/02 vira 28/02 nos anos comuns."""
    result = []
    year = start.year + 1
    while True:
        try:
            anniversary = start.replace(year=year)
        except ValueError:
            anniversary = start.replace(year=year, day=28)
        if anniversary > day:
            return result
        result.append(anniversary)
        year += 1
