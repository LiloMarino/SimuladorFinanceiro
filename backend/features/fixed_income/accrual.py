"""
Cálculo de renda fixa: a única fórmula de rendimento do simulador.

O jogo ao vivo (um `accrue` por tick), a reconstrução a partir dos eventos
(retomada) e a projeção mostrada na compra aplicam a mesma sequência de
multiplicações `valor *= daily_factor(taxa)`, um dia útil por vez e na mesma
ordem, em `Decimal`. Por isso os três chegam ao mesmo valor ao centavo.
"""

from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from functools import lru_cache

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_projection import FixedIncomeProjectionDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.core.utils import is_business_day, next_business_day

BUSINESS_DAYS_PER_YEAR = 252
CENT = Decimal("0.01")

# Tabela regressiva de IR: (até N dias corridos de aplicação, alíquota)
INCOME_TAX_BRACKETS: list[tuple[int, Decimal]] = [
    (180, Decimal("0.225")),
    (360, Decimal("0.20")),
    (720, Decimal("0.175")),
]
INCOME_TAX_FLOOR = Decimal("0.15")


def index_rate_on(rate_index: RateIndexType, on: date) -> Decimal:
    """Taxa anual do indexador no dia. Prefixado não tem indexador: vale 0."""
    match rate_index:
        case RateIndexType.CDI:
            return repository.economic.get_cdi_rate(on)
        case RateIndexType.IPCA:
            return repository.economic.get_ipca_rate(on)
        case RateIndexType.SELIC:
            return repository.economic.get_selic_rate(on)
        case RateIndexType.PREFIXADO:
            return Decimal(0)


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
def daily_factor(annual_rate: Decimal) -> Decimal:
    """Fator de um dia útil: (1 + taxa anual) ^ (1/252)."""
    return (1 + annual_rate) ** (Decimal(1) / BUSINESS_DAYS_PER_YEAR)


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
    asset: FixedIncomeAssetDTO, amount: Decimal, on: date, index_rate: Decimal
) -> FixedIncomeProjectionDTO:
    """
    Projeta `amount` aplicado em `on` até o resgate, com o indexador congelado em
    `index_rate` (o último conhecido). O primeiro dia que rende é o tick seguinte
    à compra, e o último é o dia do resgate — igual ao jogo ao vivo.
    """
    annual_rate = effective_annual_rate(asset, index_rate)
    factor = daily_factor(annual_rate)
    redeem_on = redemption_date(asset.maturity_date)

    # `gross_amount` cresce a partir de `amount`; `growth`, a partir de 1 (percentuais)
    gross_amount = amount
    growth = Decimal(1)
    business_days = 0
    day = next_business_day(on)
    while day <= redeem_on:
        gross_amount *= factor
        growth *= factor
        business_days += 1
        day = next_business_day(day)

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
