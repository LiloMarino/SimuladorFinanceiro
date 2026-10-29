"""
O orçamento do governo: a receita pela alíquota de cada imposto do jogo, o gasto, o
resultado e a dívida mês a mês, e o prêmio de risco que a dívida alta cobra. Os
impostos da partida só incidem sobre as operações dos jogadores, pequenas demais perto
de um país, então a receita é modelada em % do PIB e o IR dos jogadores não entra nela.
Valores em fração do PIB por ano (0.0183 = 1,83%) e taxas em fração ao ano; o
`BudgetCourse` guarda o que já andou. É o contrato em que o gasto público e as emendas
se apoiam.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import IndicatorSeries, InitialAccount
from backend.core.indicators import (
    annual_index_rate,
    gross_debt_ratio,
    nominal_gdp,
    primary_result_ratio,
)
from backend.core.utils import last_day_of_month
from backend.features.economy.growth import MacroCourse
from backend.features.government import measures as rules
from backend.features.government.state import Measure
from backend.features.tax_policy import DEFAULT_TAX_POLICY, LossPool, TaxPolicy

ZERO = Decimal(0)
HUNDRED = Decimal(100)
MONTHS_PER_YEAR = Decimal(12)
ONE_TWELFTH = Decimal(1) / MONTHS_PER_YEAR

# Gasto base do governo, em fração do PIB por ano
BASE_SPENDING = Decimal("0.19")


@dataclass(frozen=True)
class Tax:
    """
    Um imposto do jogo: a receita com a alíquota de referência (em fração do PIB por
    ano) e a elasticidade. Cortar a alíquota pela metade tira menos que metade da
    receita, porque quem paga menos passa a operar mais.
    """

    base: Decimal
    reference: Decimal
    elasticity: Decimal

    def revenue(self, rate: Decimal) -> Decimal:
        if rate <= 0:
            return ZERO
        return self.base * (rate / self.reference) ** (1 - self.elasticity)


COMMON = Tax(Decimal("0.0006"), Decimal("0.15"), Decimal("0.4"))
DAY_TRADE_FII = Tax(Decimal("0.0003"), Decimal("0.20"), Decimal("0.3"))
FIXED_INCOME = Tax(Decimal("0.0060"), Decimal("0.175"), Decimal("0.15"))
LCI_LCA = Tax(Decimal("0.0012"), Decimal("0.15"), Decimal("0.3"))

# A isenção das vendas até R$ 20 mil deixa 30% do ganho comum fora do IR; a fração
# cresce com a raiz do teto, até 90%
EXEMPT_SHARE = Decimal("0.3")
EXEMPT_REFERENCE = Decimal(20000)
EXEMPT_CAP = Decimal("0.9")
# Quanto do IR do ganho comum vem de cada setor com regra
SECTOR_SHARE = Decimal("0.1")


def exempt_share(limit: Decimal) -> Decimal:
    return min(EXEMPT_SHARE * (max(limit, ZERO) / EXEMPT_REFERENCE).sqrt(), EXEMPT_CAP)


def taxed_share(limit: Decimal) -> Decimal:
    """Quanto do ganho comum o IR alcança com o teto da isenção, contra o teto padrão."""
    default = exempt_share(DEFAULT_TAX_POLICY.stock_exemption_limit)
    return (1 - exempt_share(limit)) / (1 - default)


@dataclass(frozen=True)
class SectorTax:
    """A regra mais nova de um setor (ou segmento) e o que ela soma ao IR do ganho comum."""

    sector: str
    segment: str | None
    exempt: bool
    extra: Decimal
    adjustment: Decimal


@dataclass(frozen=True)
class TaxRow:
    """Um imposto do jogo: a alíquota de hoje e a padrão, o que arrecada e a diferença contra a padrão."""

    key: str
    name: str
    # Nula quando o imposto é isento
    rate: Decimal | None
    default_rate: Decimal | None
    revenue: Decimal
    difference: Decimal
    # Na renda fixa, a alíquota do prazo mais curto e a do mais longo, hoje e na política padrão
    top_rate: Decimal | None = None
    floor_rate: Decimal | None = None
    default_top_rate: Decimal | None = None
    default_floor_rate: Decimal | None = None


def sector_taxes(policy: TaxPolicy) -> list[SectorTax]:
    """Cada setor com regra conta uma vez, pela regra mais nova dele."""
    newest: dict[tuple[str, str | None], SectorTax] = {}
    taxed = taxed_share(policy.stock_exemption_limit)
    common = policy.rates[LossPool.COMMON]
    for rule in policy.sector_rules:
        if rule.exempt:
            adjustment = -SECTOR_SHARE * COMMON.revenue(common) * taxed
        else:
            adjustment = (
                SECTOR_SHARE
                * (COMMON.revenue(common + rule.extra) - COMMON.revenue(common))
                * taxed
            )
        newest[(rule.sector, rule.segment)] = SectorTax(
            rule.sector, rule.segment, rule.exempt, rule.extra, adjustment
        )
    return list(newest.values())


def tax_rows(policy: TaxPolicy) -> list[TaxRow]:
    """Uma linha por imposto do jogo; a soma das linhas é a receita do jogo."""
    default = DEFAULT_TAX_POLICY
    common = policy.rates[LossPool.COMMON]
    day_trade = policy.rates[LossPool.DAY_TRADE]
    taxed = taxed_share(policy.stock_exemption_limit)

    def row(
        key: str,
        name: str,
        rate: Decimal,
        default_rate: Decimal,
        revenue: Decimal,
        default_revenue: Decimal,
    ) -> TaxRow:
        return TaxRow(
            key=key,
            name=name,
            rate=rate,
            default_rate=default_rate,
            revenue=revenue,
            difference=revenue - default_revenue,
        )

    rows = [
        row(
            "STOCK_PROFIT",
            "Ações · vendas com lucro",
            common,
            default.rates[LossPool.COMMON],
            COMMON.revenue(common) * taxed,
            COMMON.revenue(default.rates[LossPool.COMMON]),
        ),
        row(
            "DAY_TRADE",
            "Ações · day trade e FII",
            day_trade,
            default.rates[LossPool.DAY_TRADE],
            DAY_TRADE_FII.revenue(day_trade),
            DAY_TRADE_FII.revenue(default.rates[LossPool.DAY_TRADE]),
        ),
        replace(
            row(
                "FIXED_INCOME",
                "Renda fixa · tabela",
                policy.fixed_income_average_rate,
                default.fixed_income_average_rate,
                FIXED_INCOME.revenue(policy.fixed_income_average_rate),
                FIXED_INCOME.revenue(default.fixed_income_average_rate),
            ),
            top_rate=policy.fixed_income_top_rate,
            floor_rate=policy.fixed_income_floor,
            default_top_rate=default.fixed_income_top_rate,
            default_floor_rate=default.fixed_income_floor,
        ),
        row(
            "LCI_LCA",
            "LCI e LCA",
            policy.lci_lca_rate,
            default.lci_lca_rate,
            LCI_LCA.revenue(policy.lci_lca_rate),
            LCI_LCA.revenue(default.lci_lca_rate),
        ),
    ]
    # O setor com regra ajusta o IR do ganho comum da linha de cima: isento tira a fatia dele
    rows.extend(
        TaxRow(
            key="SECTOR",
            name=f"{sector.segment or sector.sector} · setor",
            rate=None if sector.exempt else common + sector.extra,
            default_rate=common,
            revenue=sector.adjustment,
            difference=sector.adjustment,
        )
        for sector in sector_taxes(policy)
    )
    return rows


def game_revenue(policy: TaxPolicy) -> Decimal:
    """A receita dos impostos do jogo, em fração do PIB por ano."""
    return sum((r.revenue for r in tax_rows(policy)), ZERO)


# Com a política padrão os impostos do jogo somam 0,69% do PIB
DEFAULT_GAME_REVENUE = game_revenue(DEFAULT_TAX_POLICY)


def measure_effect(policy_before: TaxPolicy, measure: Measure) -> Decimal:
    """A diferença que a medida causa na receita, em fração do PIB por ano."""
    return game_revenue(rules.apply_measure(policy_before, measure)) - game_revenue(
        policy_before
    )


# Prêmio de risco: 2 pontos x (e^(0,02 x pontos de dívida acima de 50%) - 1), sem teto
PREMIUM_FLOOR = Decimal("0.5")
PREMIUM_PACE = Decimal("0.02")
PREMIUM_SCALE = Decimal(2)


def premium(debt: Decimal) -> Decimal:
    """O prêmio que a dívida cobra nos títulos novos, em fração ao ano (0.0164 com 80% do PIB)."""
    if debt <= PREMIUM_FLOOR:
        return ZERO
    points = (debt - PREMIUM_FLOOR) * HUNDRED
    return PREMIUM_SCALE * ((PREMIUM_PACE * points).exp() - 1) / HUNDRED


def premium_curve() -> list[tuple[Decimal, Decimal]]:
    """Os pontos do gráfico: de 0% a 150% do PIB de dívida, de 10 em 10 pontos."""
    return [
        (Decimal(points) / HUNDRED, premium(Decimal(points) / HUNDRED))
        for points in range(0, 151, 10)
    ]


def step(
    debt: Decimal, selic: Decimal, ipca: Decimal, growth: Decimal, primary: Decimal
) -> Decimal:
    """
    A dívida um mês depois: ela rende a SELIC mais o prêmio, encolhe com o crescimento e
    a inflação (que aumentam o PIB) e o resultado primário a abate.
    """
    rate = selic + premium(debt)
    factor = ((1 + rate) / ((1 + growth) * (1 + ipca))) ** ONE_TWELFTH
    return debt * factor - primary * ONE_TWELFTH


@dataclass(frozen=True)
class AccountStart:
    """A conta do governo no primeiro dia: a dívida e o primário em fração do PIB e o PIB em reais."""

    debt: Decimal
    # Fração do PIB por ano; negativo é déficit
    primary: Decimal
    gdp: Decimal


def initial_account(start: date, kind: InitialAccount) -> AccountStart:
    """A dívida e o PIB do fim do ano anterior ao início; o primário real só na conta realista."""
    previous = start.year - 1
    return AccountStart(
        debt=gross_debt_ratio(previous),
        primary=(
            primary_result_ratio(start.year)
            if kind is InitialAccount.REALISTIC
            else ZERO
        ),
        gdp=nominal_gdp(previous),
    )


def fixed_revenue(account: AccountStart) -> Decimal:
    """
    O resto da arrecadação do país, fixo em fração do PIB: fecha o gasto base com a
    política padrão e, na conta realista, soma o primário real (negativo no déficit).
    """
    return BASE_SPENDING - DEFAULT_GAME_REVENUE + account.primary


@dataclass(frozen=True)
class BudgetMonth:
    """O orçamento no fim de um mês; sem `closed` é o ponto de partida, antes do primeiro fechamento."""

    month_end: date
    # Frações do PIB por ano
    revenue: Decimal
    spending: Decimal
    primary: Decimal
    interest: Decimal
    result: Decimal
    # Dívida em fração do PIB, o prêmio que ela cobra depois do fechamento e o PIB em 12 meses
    debt: Decimal
    premium: Decimal
    gdp: Decimal
    closed: bool = True

    def monthly(self, ratio: Decimal) -> Decimal:
        """Uma fração do PIB por ano, no mês, em reais."""
        return ratio * self.gdp * ONE_TWELFTH


SpendingOn = Callable[[date], Decimal]


def base_spending_on(_day: date) -> Decimal:
    return BASE_SPENDING


class BudgetCourse:
    """
    Os fechamentos de mês do orçamento desde o começo da partida. Uma medida só vale 90
    dias depois de aprovada, então um mês fechado nunca muda e o cálculo avança com
    memória; numa retomada refaz tudo desde o início, no molde do replay.
    """

    def __init__(
        self,
        start: date,
        policy_on: Callable[[date], TaxPolicy],
        account: AccountStart,
        macro: MacroCourse,
        spending_on: SpendingOn = base_spending_on,
    ):
        self._policy_on = policy_on
        self._macro = macro
        self._spending_on = spending_on
        self._fixed = fixed_revenue(account)
        self._lock = threading.Lock()
        self._initial = BudgetMonth(
            month_end=start - timedelta(days=1),
            revenue=self._fixed + DEFAULT_GAME_REVENUE,
            spending=BASE_SPENDING,
            primary=account.primary,
            interest=ZERO,
            result=ZERO,
            debt=account.debt,
            premium=premium(account.debt),
            gdp=account.gdp,
            closed=False,
        )
        self._months: list[BudgetMonth] = []

    def fixed_revenue(self) -> Decimal:
        return self._fixed

    def revenue_on(self, day: date) -> Decimal:
        """A receita total em vigor no dia: o resto do país mais os impostos do jogo."""
        return self._fixed + game_revenue(self._policy_on(day))

    def months_until(self, day: date) -> list[BudgetMonth]:
        """Os meses já fechados em `day`: o fim do mês é hoje ou já passou."""
        with self._lock:
            while True:
                last = self._months[-1] if self._months else self._initial
                following = last_day_of_month(last.month_end + timedelta(days=1))
                if following > day:
                    break
                self._months.append(self._close(last, following))
            return [m for m in self._months if m.month_end <= day]

    def latest(self, day: date) -> BudgetMonth:
        """O último mês fechado em `day`; antes do primeiro, o ponto de partida."""
        closed = self.months_until(day)
        return closed[-1] if closed else self._initial

    def debt_on(self, day: date) -> Decimal:
        return self.latest(day).debt

    def premium_on(self, day: date) -> Decimal:
        """O prêmio de risco que vale no dia, pela dívida do último fechamento."""
        return self.latest(day).premium

    def project(
        self,
        day: date,
        until: date,
        revenue_delta: Decimal = ZERO,
        delta_from: date | None = None,
    ) -> list[BudgetMonth]:
        """
        Os meses de depois do último fechamento até `until`, se nada mais mudar: SELIC,
        IPCA e crescimento de `day` ficam como estão, e valem os impostos que o governo
        já aprovou. `revenue_delta` soma à receita dos meses a partir de `delta_from`.
        """
        previous = self.latest(day)
        selic = annual_index_rate(IndicatorSeries.SELIC, day)
        ipca = annual_index_rate(IndicatorSeries.IPCA, day)
        growth = self._macro.latest(day).growth
        projected: list[BudgetMonth] = []
        while (
            month_end := last_day_of_month(previous.month_end + timedelta(days=1))
        ) <= until:
            extra = (
                revenue_delta
                if delta_from is not None and month_end >= delta_from
                else ZERO
            )
            previous = self._month(previous, month_end, selic, ipca, growth, extra)
            projected.append(previous)
        return projected

    def _close(self, previous: BudgetMonth, month_end: date) -> BudgetMonth:
        return self._month(
            previous,
            month_end,
            annual_index_rate(IndicatorSeries.SELIC, month_end),
            annual_index_rate(IndicatorSeries.IPCA, month_end),
            self._macro.latest(month_end).growth,
            ZERO,
        )

    def _month(
        self,
        previous: BudgetMonth,
        month_end: date,
        selic: Decimal,
        ipca: Decimal,
        growth: Decimal,
        extra_revenue: Decimal,
    ) -> BudgetMonth:
        revenue = self.revenue_on(month_end) + extra_revenue
        spending = self._spending_on(month_end)
        primary = revenue - spending
        rate = selic + premium(previous.debt)
        debt = step(previous.debt, selic, ipca, growth, primary)
        interest = debt * rate
        return BudgetMonth(
            month_end=month_end,
            revenue=revenue,
            spending=spending,
            primary=primary,
            interest=interest,
            result=primary - interest,
            debt=debt,
            premium=premium(debt),
            gdp=previous.gdp * (((1 + growth) * (1 + ipca)) ** ONE_TWELFTH),
        )
