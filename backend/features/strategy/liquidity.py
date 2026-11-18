from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.enum import RateIndexType
from backend.core.utils import format_money, required
from backend.features.strategy.context import StrategyContext

ZERO = Decimal(0)
CENT = Decimal("0.01")
# Abaixo disto o dinheiro parado não vale uma ordem
MIN_MOVE = Decimal(1)


def liquid_offer(ctx: StrategyContext) -> FixedIncomeOfferDTO | None:
    """O CDB de liquidez diária sem teto por jogador: o que comporta o caixa inteiro."""
    offers = [
        o
        for o in ctx.fixed_offers
        if o.daily_liquidity
        and o.rate_index is RateIndexType.CDI
        and o.player_cap is None
    ]
    if not offers:
        return None
    return min(offers, key=lambda o: (-o.interest_rate, str(o.asset_uuid)))


def redeem_liquid(ctx: StrategyContext, need: Decimal, why: str) -> Decimal:
    """Resgata `need` dos títulos de liquidez diária, os maiores primeiro; devolve o resgatado."""
    redeemed = ZERO
    liquid = sorted(
        (h for h in ctx.fixed_holdings if h.redeemable),
        key=lambda h: (-(h.redeemable or ZERO), str(h.asset_uuid)),
    )
    for holding in liquid:
        value = min(need - redeemed, required(holding.redeemable)).quantize(
            CENT, ROUND_DOWN
        )
        if value < MIN_MOVE:
            continue
        ctx.redeem(
            holding.asset_uuid,
            value,
            f"{why}: resgatou {format_money(value)} de {holding.name}",
        )
        redeemed += value
    return redeemed
