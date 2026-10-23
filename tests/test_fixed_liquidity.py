"""Liquidez diária: total resgatável da carteira e o título que paga o cheque especial."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.liquidity import (
    overdraft_cover,
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


def test_no_cover_while_the_cash_is_not_negative():
    assert overdraft_cover(Decimal(0), [_position("A", "0.1")], TODAY) is None


def test_cover_is_the_lowest_rate_title_that_pays_the_whole_debt():
    cheap = _position("Barato", "0.08", value="10000")
    dear = _position("Caro", "0.12", value="10000")
    small = _position("Pequeno", "0.05", value="100")

    cover = overdraft_cover(Decimal("-2140.50"), [dear, small, cheap], TODAY)

    assert cover is not None
    assert cover.asset_name == "Barato"
    assert cover.net_amount == Decimal("2140.50")
    assert cover.gross_amount > cover.net_amount


def test_no_cover_when_no_single_title_pays_the_debt():
    positions = [
        _position("A", "0.1", value="1000"),
        _position("B", "0.1", value="1000"),
    ]

    assert overdraft_cover(Decimal("-5000"), positions, TODAY) is None
