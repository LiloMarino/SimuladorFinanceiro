"""
As ligações da economia interligada: o que o desvio da partida contra a história num
mês fechado faz com a inflação, o dólar, a bolsa, o crédito e o orçamento a partir do mês
seguinte. A entrada é sempre o desvio (partida menos linha de base), então sem ação
do governo toda ligação é zero e as séries ficam como a história.
"""

import math
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import cached_property

from backend.core.periods import MONTHS_PER_YEAR

ZERO = Decimal(0)
HUNDRED = 100

# Curva de Phillips: cada ponto de desemprego abaixo da história soma 0,35 ponto ao IPCA em 12 meses
PHILLIPS = 0.35
# Câmbio: o dólar da partida é o da história vezes e elevado ao desvio. Cada ponto de prêmio
# acima da história soma 4% ao dólar (o investidor de fora foge) e cada ponto de juro real
# acima da história tira 2% (o dinheiro de fora vem atrás do juro)
DOLLAR_PER_PREMIUM = 0.04
DOLLAR_PER_REAL_RATE = 0.02
# Cada causa mexe no expoente do dólar até o teto: o prêmio leva o dólar a no máximo 4,5
# vezes o da história (e^1,5) e a no mínimo 0,6 (e^-0,5); o juro real, a e^±0,5. Com o
# teto, o ciclo prêmio → dólar → inflação → juro → prêmio fecha com números finitos
MAX_DOLLAR_PREMIUM = 1.5
MIN_DOLLAR_PREMIUM = -0.5
MAX_DOLLAR_REAL_RATE = 0.5
# Repasse do câmbio: cada 1% de alta do dólar em 12 meses soma 0,07 ponto ao IPCA em 12
# meses, porque o importado e o combustível encarecem. O repasse muda o patamar dos preços
# uma vez, então conta a alta em 12 meses e não o nível do dólar
DOLLAR_PASS_THROUGH = 0.07
# Ciclo fiscal: a arrecadação acompanha o PIB, 6% de cada ponto de PIB acima da história
CYCLE_REVENUE = Decimal("0.06")
# Seguro-desemprego: cada ponto de desemprego acima da história custa 0,05% do PIB por ano
INSURANCE = Decimal("0.05")
# Impulso fiscal: cada ponto do PIB que o primário piorou contra a história em 12 meses soma meio
# ponto ao alvo do crescimento. O empurrão vem quando o gasto sobe ou o imposto cai; o déficit
# que fica no mesmo patamar deixa o PIB mais alto, mas não o faz crescer mais rápido
IMPULSE = Decimal("0.5")
IMPULSE_MONTHS = 12
# Efeito expulsão: cada ponto de prêmio de risco acima da história encarece o crédito das
# empresas e tira três quartos de ponto do alvo do crescimento, mesmo com a SELIC baixa;
# prêmio abaixo da história não empurra o crescimento
CROWDING_OUT = Decimal("0.75")
# Imposto sobre o consumo: cada ponto de alíquota a mais, repassado aos preços ao longo de 12
# meses, soma meio ponto ao IPCA em 12 meses
CONSUMPTION_PASS_THROUGH = 0.5
# IR das empresas: cada ponto de alíquota acima do padrão tira 1,2% do nível da bolsa, pelo
# lucro menor das empresas (o corte levanta)
CORPORATE_STOCKS = 0.012
# Contribuição sobre a folha: cada ponto de alíquota acima do padrão soma 0,06 ponto ao ano
# ao desemprego, porque contratar fica mais caro
PAYROLL_JOBS = Decimal("0.0006")


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
    # A alíquota em vigor menos a padrão (0.02 = 2 pontos) no imposto sobre o consumo, no IR
    # das empresas e na contribuição sobre a folha; no consumo, também quanto ela mudou em 12 meses
    consumption_gap: Decimal = ZERO
    consumption_change: Decimal = ZERO
    corporate_gap: Decimal = ZERO
    payroll_gap: Decimal = ZERO
    # O desvio do dólar do mês de 12 meses antes, de onde sai a alta que o IPCA repassa
    dollar_gap_year_ago: float = 0.0

    @cached_property
    def phillips_points(self) -> float:
        return -PHILLIPS * float(self.unemployment_gap) * HUNDRED

    @cached_property
    def premium_points(self) -> float:
        return float(self.premium_gap) * HUNDRED

    @cached_property
    def dollar_premium(self) -> float:
        """A parte do desvio do dólar que o prêmio acima da história põe."""
        return max(
            MIN_DOLLAR_PREMIUM,
            min(MAX_DOLLAR_PREMIUM, DOLLAR_PER_PREMIUM * self.premium_points),
        )

    @cached_property
    def dollar_real_rate(self) -> float:
        """A parte do desvio do dólar que o juro real acima da história põe."""
        raw = -DOLLAR_PER_REAL_RATE * float(self.real_rate_gap) * HUNDRED
        return max(-MAX_DOLLAR_REAL_RATE, min(MAX_DOLLAR_REAL_RATE, raw))

    @cached_property
    def dollar_gap(self) -> float:
        """O dólar da partida contra o da história, como expoente: o dólar é a história vezes e elevado a ele."""
        return self.dollar_premium + self.dollar_real_rate

    @cached_property
    def dollar_change(self) -> float:
        """A alta em 12 meses do dólar da partida contra a da história, em fração."""
        return math.exp(self.dollar_gap - self.dollar_gap_year_ago) - 1

    @cached_property
    def dollar_inflation_points(self) -> float:
        return DOLLAR_PASS_THROUGH * self.dollar_change * HUNDRED

    @cached_property
    def consumption_points(self) -> float:
        return CONSUMPTION_PASS_THROUGH * float(self.consumption_change) * HUNDRED

    @cached_property
    def corporate_points(self) -> float:
        """O expoente do nível da bolsa que o IR das empresas põe."""
        return -CORPORATE_STOCKS * float(self.corporate_gap) * HUNDRED

    @cached_property
    def inflation_points(self) -> float:
        return (
            self.phillips_points
            + self.dollar_inflation_points
            + self.rate_points
            + self.consumption_points
        )

    @property
    def payroll_jobs(self) -> Decimal:
        """O que a contribuição sobre a folha soma ao desemprego, em fração ao ano."""
        return PAYROLL_JOBS * self.payroll_gap * HUNDRED

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
    def crowding_out(self) -> Decimal:
        return -CROWDING_OUT * max(Decimal(0), self.premium_gap)

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
            or self.consumption_gap
            or self.consumption_change
            or self.corporate_gap
            or self.payroll_gap
            or self.dollar_gap_year_ago
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
            and self.consumption_gap == other.consumption_gap
            and self.consumption_change == other.consumption_change
            and self.corporate_gap == other.corporate_gap
            and self.payroll_gap == other.payroll_gap
            and self.dollar_gap_year_ago == other.dollar_gap_year_ago
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
    consumption_gap: Decimal = ZERO,
    consumption_gap_year_ago: Decimal = ZERO,
    corporate_gap: Decimal = ZERO,
    payroll_gap: Decimal = ZERO,
    dollar_gap_year_ago: float = 0.0,
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
        consumption_gap=consumption_gap,
        consumption_change=consumption_gap - consumption_gap_year_ago,
        corporate_gap=corporate_gap,
        payroll_gap=payroll_gap,
        dollar_gap_year_ago=dollar_gap_year_ago,
    )


NO_LINK = LinkMonth(date.min, ZERO, ZERO, ZERO, ZERO, ZERO)
