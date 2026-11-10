"""Renda e despesa mensais da partida e a meta do viver de renda que sai delas."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import IncomeLoss, IndicatorSeries, Profession
from backend.core.indicators import (
    anniversaries,
    annual_index_rate,
    inflation_factor,
)
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.professions import (
    PROFESSIONS,
    REFERENCE_RATES,
    REFERENCE_WELFARE_SPENDING,
    LifeLevers,
    ProfessionRule,
    RealRaise,
    entrepreneur_gdp_factor,
    no_levers,
)

CENT = Decimal("0.01")

# Parte do crescimento real do PIB de 12 meses que entra no salário, além do IPCA
SALARY_GDP_SHARE = Decimal("0.5")


def no_growth(day: date) -> Decimal:
    return Decimal(0)


@dataclass(frozen=True)
class LifeBudget:
    """
    Renda e despesa mensais de uma profissão na partida. A renda é o salário do host
    vezes o múltiplo da profissão (a de carteira vale 1). Com `inflation_adjusted`, a
    despesa sobe pelo IPCA acumulado em 12 meses a cada aniversário da data de início e
    a meta sobe junto; a renda sobe pelo IPCA mais o reajuste real da profissão (a de
    carteira ganha `SALARY_GDP_SHARE` do crescimento do PIB de 12 meses, que na recessão
    não soma nada). A despesa e a meta são as mesmas para toda profissão.
    """

    monthly_salary: Decimal
    monthly_expense: Decimal
    # Fração do patrimônio retirada por ano (0.04 = regra dos 4%)
    withdrawal_rate: Decimal
    inflation_adjusted: bool
    start_date: date
    # Crescimento do PIB de 12 meses da partida em cada dia, em fração (0.031)
    growth_on: Callable[[date], Decimal] = no_growth
    profession: Profession = Profession.CLT
    # As medidas do governo que valem em cada dia; sem governo, o país padrão
    levers_on: Callable[[date], LifeLevers] = no_levers
    # No cargo de presidente a renda é este múltiplo do salário do host, no lugar da
    # renda da profissão, e nenhum sorteio de demissão a alcança
    presidency_multiple: Decimal | None = None

    @classmethod
    def of(
        cls,
        settings: SimulationSettingsDTO,
        growth_on: Callable[[date], Decimal] = no_growth,
        levers_on: Callable[[date], LifeLevers] = no_levers,
    ) -> "LifeBudget":
        return cls(
            monthly_salary=settings.monthly_salary,
            monthly_expense=settings.monthly_expense,
            withdrawal_rate=settings.withdrawal_rate,
            inflation_adjusted=settings.inflation_adjusted,
            start_date=settings.start_date,
            growth_on=growth_on,
            levers_on=levers_on,
        )

    def for_profession(self, profession: Profession) -> "LifeBudget":
        return replace(self, profession=profession)

    def as_president(self, multiple: Decimal) -> "LifeBudget":
        """O orçamento de quem recebe `multiple` salários do host pela presidência; reajuste e imposto seguem os da profissão."""
        return replace(self, presidency_multiple=multiple)

    @property
    def rule(self) -> ProfessionRule:
        return PROFESSIONS[self.profession]

    def income_parts(self, day: date) -> tuple[Decimal, Decimal]:
        """A renda bruta do mês em duas partes: a que a demissão sorteada tira e a que fica."""
        rule = self.rule
        factor = self._salary_factor(day)
        if self.presidency_multiple is not None:
            return Decimal(0), cents(
                self.monthly_salary * self.presidency_multiple * factor
            )
        exposed = self.monthly_salary * rule.income_multiple * factor
        if rule.follows_gdp:
            exposed *= entrepreneur_gdp_factor(self.growth_on(day))
        benefit = (
            self.monthly_salary
            * rule.benefit_multiple
            * factor
            * self.levers_on(day).welfare_spending
            / REFERENCE_WELFARE_SPENDING
        )
        return cents(exposed), cents(benefit)

    def salary_on(self, day: date) -> Decimal:
        """A renda bruta do mês, antes do imposto."""
        return sum(self.income_parts(day), Decimal(0))

    def net_salary_on(self, day: date, income_lost: bool = False) -> Decimal:
        """
        A renda do mês depois do imposto da profissão: o desvio da alíquota em vigor
        contra a da lei corta a renda (alíquota abaixo dela soma). Com `income_lost`, a
        demissão sorteada tira a parte exposta, se a profissão está exposta a ela.
        """
        exposed, protected = self.income_parts(day)
        kept = protected if income_lost and self.rule.loss else exposed + protected
        return cents(kept * (1 - self.tax_deviation_on(day)))

    def income_loss(self) -> IncomeLoss | None:
        return None if self.presidency_multiple is not None else self.rule.loss

    def tax_rate_on(self, day: date) -> Decimal:
        """A alíquota em vigor do imposto que mexe na renda da profissão."""
        return self.levers_on(day).rate_of(self.rule.tax)

    def tax_reference(self) -> Decimal:
        return REFERENCE_RATES[self.rule.tax]

    def tax_deviation_on(self, day: date) -> Decimal:
        return self.tax_rate_on(day) - self.tax_reference()

    def salary_raise_inputs(self, anniversary: date) -> tuple[Decimal, Decimal]:
        """O IPCA de 12 meses e o crescimento do PIB de 12 meses que reajustam o salário no aniversário."""
        return (
            annual_index_rate(IndicatorSeries.IPCA, anniversary),
            self.growth_on(anniversary),
        )

    def real_raise_on(self, anniversary: date) -> Decimal:
        """O reajuste acima do IPCA que a profissão ganha no aniversário."""
        source = self.rule.real_raise
        if source is RealRaise.GDP_SHARE:
            return SALARY_GDP_SHARE * max(self.growth_on(anniversary), Decimal(0))
        return self.levers_on(anniversary).real_raise_of(source)

    def expense_on(self, day: date) -> Decimal:
        return cents(self.monthly_expense * self._inflation_factor(day))

    def readjustments(self, until: date) -> list[date]:
        """Os dias em que renda, despesa e meta sobem: o início e, com IPCA, cada aniversário."""
        if not self.inflation_adjusted:
            return [self.start_date]
        return [self.start_date, *anniversaries(self.start_date, until)]

    def goal_on(self, day: date) -> Decimal:
        """O patrimônio que paga a despesa do ano retirando `withdrawal_rate` dele."""
        return MONTHS_PER_YEAR * self.expense_on(day) / self.withdrawal_rate

    def _inflation_factor(self, day: date) -> Decimal:
        if not self.inflation_adjusted:
            return Decimal(1)
        return inflation_factor(self.start_date, day)

    def _salary_factor(self, day: date) -> Decimal:
        if not self.inflation_adjusted:
            return Decimal(1)
        factor = Decimal(1)
        for anniversary in anniversaries(self.start_date, day):
            ipca = annual_index_rate(IndicatorSeries.IPCA, anniversary)
            factor *= 1 + ipca + self.real_raise_on(anniversary)
        return factor


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)
