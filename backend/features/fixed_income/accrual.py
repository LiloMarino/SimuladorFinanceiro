"""
Cálculo de renda fixa: a única fórmula de rendimento do simulador.

O jogo ao vivo (um `accrue` por tick), a reconstrução a partir dos eventos
(retomada) e a projeção mostrada na compra aplicam a mesma sequência de
multiplicações `valor *= daily_factor(...)`, um dia útil por vez e na mesma
ordem, em `Decimal`. Ao vivo e reconstrução leem a taxa real de cada dia e
chegam ao mesmo valor ao centavo; a projeção congela o último valor conhecido
na compra, e coincide com eles quando o indexador não muda.

A taxa do dia útil `d` remunera a noite de `d` até o próximo dia útil: o tick
rende com a taxa do dia útil anterior a ele.
"""

from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from functools import lru_cache

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_projection import FixedIncomeProjectionDTO
from backend.core.enum import FixedIncomeType, IndicatorSeries, RateIndexType
from backend.core.indicators import (
    BUSINESS_DAYS_PER_YEAR,
    annual_index_rate,
    daily_rate,
    index_daily_rate,
    last_known_value,
)
from backend.core.utils import is_business_day, next_business_day

CENT = Decimal("0.01")

# Tabela regressiva de IR: (até N dias corridos de aplicação, alíquota)
INCOME_TAX_BRACKETS: list[tuple[int, Decimal]] = [
    (180, Decimal("0.225")),
    (360, Decimal("0.20")),
    (720, Decimal("0.175")),
]
INCOME_TAX_FLOOR = Decimal("0.15")


INDEX_SERIES: dict[RateIndexType, IndicatorSeries] = {
    RateIndexType.CDI: IndicatorSeries.CDI,
    RateIndexType.IPCA: IndicatorSeries.IPCA,
    RateIndexType.SELIC: IndicatorSeries.SELIC,
}


def index_rate_on(rate_index: RateIndexType, on: date) -> Decimal:
    """Taxa anual do indexador conhecida em `on`. Prefixado não tem indexador: vale 0."""
    if rate_index is RateIndexType.PREFIXADO:
        return Decimal(0)
    return annual_index_rate(INDEX_SERIES[rate_index], on)


def effective_annual_rate(asset: FixedIncomeAssetDTO, index_rate: Decimal) -> Decimal:
    """
    Taxa anual que o título rende, combinando o indexador com a taxa do título.

    - Prefixado: a própria taxa (0.12 = 12% a.a.).
    - CDI: percentual do CDI (interest_rate 1.05 = 105% do CDI).
    - IPCA/SELIC: spread composto sobre o índice, como no mercado:
      (1 + índice) * (1 + spread) - 1.
    """
    match asset.rate_index:
        case RateIndexType.PREFIXADO:
            return asset.interest_rate
        case RateIndexType.CDI:
            return index_rate * asset.interest_rate
        case RateIndexType.IPCA | RateIndexType.SELIC:
            return (1 + index_rate) * (1 + asset.interest_rate) - 1


@lru_cache(maxsize=1024)
def annual_to_daily_factor(annual_rate: Decimal) -> Decimal:
    """Fator de um dia útil: (1 + taxa anual) ^ (1/252)."""
    return (1 + annual_rate) ** (Decimal(1) / BUSINESS_DAYS_PER_YEAR)


def daily_factor(asset: FixedIncomeAssetDTO, index_rate: Decimal | None) -> Decimal:
    """
    Fator de um dia útil do título, com `index_rate` a fração que o indexador
    rendeu no dia. None é dia sem pregão no indexador: nada rende.

    - Prefixado: (1 + taxa) ^ (1/252).
    - CDI: 1 + CDI do dia x percentual do CDI.
    - IPCA/SELIC: (1 + índice do dia) x (1 + spread) ^ (1/252).
    """
    if index_rate is None:
        return Decimal(1)

    match asset.rate_index:
        case RateIndexType.PREFIXADO:
            return annual_to_daily_factor(asset.interest_rate)
        case RateIndexType.CDI:
            return 1 + index_rate * asset.interest_rate
        case RateIndexType.IPCA | RateIndexType.SELIC:
            return (1 + index_rate) * annual_to_daily_factor(asset.interest_rate)


def index_daily_rate_on(rate_index: RateIndexType, day: date) -> Decimal | None:
    """Fração que o indexador rendeu no dia útil `day`. Prefixado: 0."""
    if rate_index is RateIndexType.PREFIXADO:
        return Decimal(0)
    return index_daily_rate(INDEX_SERIES[rate_index], day)


def redemption_date(maturity: date) -> date:
    """Dia do resgate: o primeiro dia útil a partir do vencimento (o tick que o vê)."""
    return maturity if is_business_day(maturity) else next_business_day(maturity)


def income_tax_rate(investment_type: FixedIncomeType, days_held: int) -> Decimal:
    """Alíquota de IR pelos dias corridos de aplicação. LCI e LCA são isentas."""
    if investment_type in (FixedIncomeType.LCI, FixedIncomeType.LCA):
        return Decimal(0)

    for max_days, rate in INCOME_TAX_BRACKETS:
        if days_held <= max_days:
            return rate
    return INCOME_TAX_FLOOR


def net_redemption(
    current_value: Decimal, total_applied: Decimal, tax_rate: Decimal
) -> Decimal:
    """Valor creditado no resgate: montante menos o IR sobre o lucro, ao centavo."""
    profit = max(current_value - total_applied, Decimal(0))
    return (current_value - profit * tax_rate).quantize(CENT, ROUND_HALF_EVEN)


def project(
    asset: FixedIncomeAssetDTO, amount: Decimal, on: date
) -> FixedIncomeProjectionDTO:
    """
    Projeta `amount` aplicado em `on` até o resgate, com o indexador congelado no
    último valor conhecido em `on`. O primeiro dia que rende é o tick seguinte à
    compra, e o último é o dia do resgate — igual ao jogo ao vivo.
    """
    index_rate = index_rate_on(asset.rate_index, on)
    annual_rate = effective_annual_rate(asset, index_rate)
    redeem_on = redemption_date(asset.maturity_date)

    series = INDEX_SERIES.get(asset.rate_index)
    frozen = None if series is None else last_known_value(series, on)

    def frozen_rate(day: date) -> Decimal | None:
        if series is None:
            return Decimal(0)
        return None if frozen is None else daily_rate(series, frozen, day)

    # `gross_amount` cresce a partir de `amount`; `growth`, a partir de 1 (percentuais)
    gross_amount = amount
    growth = Decimal(1)
    business_days = 0
    previous, day = on, next_business_day(on)
    while day <= redeem_on:
        factor = daily_factor(asset, frozen_rate(previous))
        gross_amount *= factor
        growth *= factor
        business_days += 1
        previous, day = day, next_business_day(day)

    tax_rate = income_tax_rate(asset.investment_type, (redeem_on - on).days)
    gross_return = gross_amount - amount
    net_amount = net_redemption(gross_amount, amount, tax_rate)
    gross_return_pct = growth - 1

    return FixedIncomeProjectionDTO(
        amount=amount,
        index_rate=index_rate,
        effective_annual_rate=annual_rate,
        business_days=business_days,
        redemption_date=redeem_on,
        gross_amount=gross_amount,
        gross_return=gross_return,
        gross_return_pct=gross_return_pct,
        income_tax_rate=tax_rate,
        income_tax=gross_amount - net_amount,
        income_tax_pct=gross_return_pct * tax_rate,
        net_amount=net_amount,
        net_return=net_amount - amount,
        net_return_pct=gross_return_pct * (1 - tax_rate),
    )
