"""
Liquidez diária: o que cada posição manda ao caixa se vendida hoje e a ordem em que a
cobertura automática vende. Fonte única da reserva e do total resgatável da carteira.
"""

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.accrual import effective_annual_rate, index_rate_on
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.quotes import NO_QUOTES, FixedIncomeQuotes
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy


def sellable_any_day(asset: FixedIncomeAssetDTO) -> bool:
    """Vende em qualquer pregão: liquidez diária ou Tesouro (a Selic antiga está gravada sem a flag)."""
    return (
        asset.daily_liquidity or asset.investment_type is FixedIncomeType.TESOURO_DIRETO
    )


def loss_free(asset: FixedIncomeAssetDTO) -> bool:
    """Vende sem perda de marcação: liquidez diária ou Tesouro Selic."""
    return asset.daily_liquidity or (
        asset.investment_type is FixedIncomeType.TESOURO_DIRETO
        and asset.rate_index is RateIndexType.SELIC
    )


def redeemable_today(
    position: FixedIncomePosition,
    today: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
    quotes: FixedIncomeQuotes = NO_QUOTES,
) -> Decimal | None:
    """Líquido de vender a posição inteira hoje, a mercado; None em título que só sai no vencimento."""
    if not sellable_any_day(position.asset):
        return None
    return position.sell_breakdown(today, None, quotes, policy).net


def total_redeemable(
    positions: Iterable[FixedIncomePosition],
    today: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
    quotes: FixedIncomeQuotes = NO_QUOTES,
) -> Decimal:
    """Soma do líquido vendável hoje das posições de liquidez diária e do Tesouro."""
    return sum(
        (
            net
            for p in positions
            if (net := redeemable_today(p, today, policy, quotes)) is not None
        ),
        Decimal(0),
    )


def cover_order(
    positions: Iterable[FixedIncomePosition],
    today: date,
    include_marked: bool,
    quotes: FixedIncomeQuotes = NO_QUOTES,
) -> list[FixedIncomePosition]:
    """
    A ordem em que a cobertura automática vende. Primeiro os títulos sem perda de
    marcação (liquidez diária e Tesouro Selic), do que rende menos para o que rende
    mais. Com `include_marked`, depois o Prefixado e o IPCA+, do que perde menos
    (ou ganha mais) por real vendido para o que perde mais.
    """
    held = list(positions)
    steady = sorted(
        (p for p in held if loss_free(p.asset)),
        key=lambda p: effective_annual_rate(
            p.asset, index_rate_on(p.asset.rate_index, today)
        ),
    )
    if not include_marked:
        return steady

    def mark_per_real(position: FixedIncomePosition) -> Decimal:
        market = position.market_value(today, quotes)
        return Decimal(0) if market <= 0 else position.mark(today, quotes) / market

    marked = sorted(
        (p for p in held if sellable_any_day(p.asset) and not loss_free(p.asset)),
        key=mark_per_real,
        reverse=True,
    )
    return steady + marked
