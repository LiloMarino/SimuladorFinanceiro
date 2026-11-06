"""Liquidez diária: total resgatável da carteira."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.liquidity import (
    redeemable_today,
    total_redeemable,
)

BUY_DATE = date(2020, 1, 6)
TODAY = date(2020, 6, 1)


def _position(
    name: str, rate: str, *, liquid: bool = True, value: str = "10000"
) -> FixedIncomePosition:
    asset = FixedIncomeAssetDTO(
        name=name,
        issuer="Banco",
        investment_type=FixedIncomeType.CDB,
        rate_index=RateIndexType.PREFIXADO,
        maturity_date=date(2022, 1, 6),
        interest_rate=Decimal(rate),
        daily_liquidity=liquid,
    )
    position = FixedIncomePosition(asset, Decimal(value), BUY_DATE)
    position.current_value = Decimal(value) * Decimal("1.05")
    return position


def test_only_daily_liquidity_positions_are_redeemable():
    liquid, locked = (
        _position("Líquido", "0.1"),
        _position("Preso", "0.1", liquid=False),
    )

    assert redeemable_today(locked, TODAY) is None
    net = redeemable_today(liquid, TODAY)
    assert net is not None and Decimal("10000") < net < Decimal("10500")
    assert total_redeemable([liquid, locked], TODAY) == net
