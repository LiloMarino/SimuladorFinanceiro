"""
Liquidez diária: o que cada posição manda ao caixa se resgatada hoje e o título que
paga o cheque especial. Fonte única da reserva, do total resgatável da carteira e do
botão de resgate do alerta.
"""

from collections.abc import Iterable
from datetime import date
from decimal import ROUND_CEILING, Decimal

from backend.core.dto.life import OverdraftCoverDTO
from backend.features.fixed_income.accrual import RedemptionBreakdown
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy

CENT = Decimal("0.01")


def redeemable_today(
    position: FixedIncomePosition,
    today: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> Decimal | None:
    """Líquido de resgatar a posição inteira hoje; None sem liquidez diária."""
    if not position.asset.daily_liquidity:
        return None
    return position.breakdown(today, None, policy).net


def total_redeemable(
    positions: Iterable[FixedIncomePosition],
    today: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> Decimal:
    """Soma do líquido resgatável hoje das posições de liquidez diária."""
    return sum(
        (
            net
            for p in positions
            if (net := redeemable_today(p, today, policy)) is not None
        ),
        Decimal(0),
    )


def overdraft_cover(
    cash: Decimal,
    positions: Iterable[FixedIncomePosition],
    today: date,
    policy: TaxPolicy = DEFAULT_TAX_POLICY,
) -> OverdraftCoverDTO | None:
    """
    Com o caixa negativo, o título de liquidez diária de menor taxa cujo líquido de
    hoje cobre a dívida inteira sozinho; None se o caixa é positivo ou nenhum cobre.
    """
    if cash >= 0:
        return None

    debt = (-cash).quantize(CENT, ROUND_CEILING)
    covering: list[tuple[FixedIncomePosition, RedemptionBreakdown]] = []
    for position in positions:
        net = redeemable_today(position, today, policy)
        if net is not None and net >= debt:
            covering.append((position, position.breakdown(today, debt, policy)))
    if not covering:
        return None

    position, breakdown = min(covering, key=lambda c: c[0].asset.interest_rate)
    return OverdraftCoverDTO(
        asset_uuid=position.asset.asset_uuid,
        asset_name=position.asset.name,
        net_amount=debt,
        gross_amount=breakdown.gross,
    )
