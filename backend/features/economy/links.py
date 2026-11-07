"""
As ligações da economia interligada: o que o desvio da partida contra a história num
mês fechado faz com a inflação, a bolsa, o crédito e o orçamento a partir do mês
seguinte. A entrada é sempre o desvio (partida menos linha de base), então sem ação
do governo toda ligação é zero e as séries ficam como a história.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import cached_property

from backend.core.periods import MONTHS_PER_YEAR

ZERO = Decimal(0)
HUNDRED = 100

# Curva de Phillips: cada ponto de desemprego abaixo da história soma 0,35 ponto ao IPCA em 12 meses
PHILLIPS = 0.35
# Risco fiscal: cada ponto de prêmio acima da história soma meio ponto ao IPCA (o real se desvaloriza)
PREMIUM_INFLATION = 0.5
# Ciclo fiscal: a arrecadação acompanha o PIB, 6% de cada ponto de PIB acima da história
CYCLE_REVENUE = Decimal("0.06")
# Seguro-desemprego: cada ponto de desemprego acima da história custa 0,05% do PIB por ano
INSURANCE = Decimal("0.05")
# Impulso fiscal: cada ponto do PIB que o primário piorou contra a história em 12 meses soma meio
# ponto ao alvo do crescimento. O empurrão vem quando o gasto sobe ou o imposto cai; o déficit
# que fica no mesmo patamar deixa o PIB mais alto, mas não o faz crescer mais rápido
IMPULSE = Decimal("0.5")
IMPULSE_MONTHS = 12


@dataclass(frozen=True)
class LinkMonth:
    """
    O desvio da partida contra a história num mês fechado, e o que ele vale do mês
    seguinte em diante. Frações (0.02 = 2 pontos); os pontos de IPCA em ponto percentual,
    contados uma vez por mês e lidos por todo dia que a camada refaz.
    """

    month_end: date
    unemployment_gap: Decimal
    premium_gap: Decimal
    # O nível do PIB acima da história: a soma do crescimento a mais de cada mês
    gdp_gap: Decimal
    # O resultado primário escolhido pelo governo (sem obras e sem o ciclo) contra a história
    primary_gap: Decimal
    # Quanto esse desvio do primário mudou em 12 meses
    primary_change: Decimal
    # O juro real da partida (SELIC menos IPCA em 12 meses) contra o da história
    real_rate_gap: Decimal = ZERO
    # O que os juros reais dos últimos 12 meses somam ao IPCA em 12 meses, já pela defasagem
    rate_points: float = 0.0

    @cached_property
    def phillips_points(self) -> float:
        return -PHILLIPS * float(self.unemployment_gap) * HUNDRED

    @cached_property
    def premium_points(self) -> float:
        return float(self.premium_gap) * HUNDRED

    @cached_property
    def premium_inflation_points(self) -> float:
        return PREMIUM_INFLATION * self.premium_points

    @cached_property
    def inflation_points(self) -> float:
        return self.phillips_points + self.premium_inflation_points + self.rate_points

    @property
    def cycle_revenue(self) -> Decimal:
        return CYCLE_REVENUE * self.gdp_gap

    @property
    def insurance(self) -> Decimal:
        return INSURANCE * self.unemployment_gap

    @property
    def impulse(self) -> Decimal:
        return -IMPULSE * self.primary_change

    @property
    def is_zero(self) -> bool:
        return not (
            self.unemployment_gap
            or self.premium_gap
            or self.gdp_gap
            or self.primary_gap
            or self.primary_change
            or self.real_rate_gap
            or self.rate_points
        )

    def same_effect(self, other: "LinkMonth") -> bool:
        """Os dois meses põem o mesmo efeito nas séries e no orçamento."""
        return (
            self.unemployment_gap == other.unemployment_gap
            and self.premium_gap == other.premium_gap
            and self.gdp_gap == other.gdp_gap
            and self.primary_gap == other.primary_gap
            and self.primary_change == other.primary_change
            and self.real_rate_gap == other.real_rate_gap
            and self.rate_points == other.rate_points
        )


def link_month(
    previous: LinkMonth | None,
    month_end: date,
    *,
    unemployment_gap: Decimal,
    premium_gap: Decimal,
    growth_gap: Decimal,
    primary_gap: Decimal,
    primary_gap_year_ago: Decimal,
    real_rate_gap: Decimal = ZERO,
    rate_points: float = 0.0,
) -> LinkMonth:
    """
    O mês fechado: o nível do PIB acumula o crescimento a mais do mês, um doze avos do
    anual, e o impulso sai do desvio do primário contra o de 12 meses antes.
    """
    level = ZERO if previous is None else previous.gdp_gap
    return LinkMonth(
        month_end=month_end,
        unemployment_gap=unemployment_gap,
        premium_gap=premium_gap,
        gdp_gap=level + growth_gap / MONTHS_PER_YEAR,
        primary_gap=primary_gap,
        primary_change=primary_gap - primary_gap_year_ago,
        real_rate_gap=real_rate_gap,
        rate_points=rate_points,
    )


NO_LINK = LinkMonth(date.min, ZERO, ZERO, ZERO, ZERO, ZERO)
