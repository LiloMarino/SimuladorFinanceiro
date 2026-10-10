"""Negócios, giro e custo de impacto de cada jogador."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.enum import EquityEventType
from backend.features.statistics import operations
from backend.features.variable_income.price_impact import PriceImpact

BUY, SELL = EquityEventType.BUY, EquityEventType.SELL
JAN, FEB = date(2020, 1, 6), date(2020, 2, 3)


def trade(day: date, kind: EquityEventType, quantity: int, price: str):
    return EquityEventDTO(
        simulation_id=1,
        user_id=1,
        event_date=day,
        ticker="ITUB4",
        event_type=kind,
        quantity=quantity,
        price=Decimal(price),
    )


class FixedImpact(PriceImpact):
    """Fator de impacto conhecido por dia, sem passar pelos eventos."""

    def __init__(self, factors: dict[date, float]):
        super().__init__(1, enabled=True, k=0.02, decay_days=20)
        self.factors = factors

    def factors_on(self, ticker: str, days: list[date]) -> dict[date, float]:
        return {day: self.factors[day] for day in days}


def test_impact_cost_charges_buys_above_and_sells_below_history():
    """
    Compra de 100 a R$ 11 com fator 1,1 (histórico R$ 10) custa R$ 100; venda de
    100 a R$ 9 com fator 0,9 (histórico R$ 10) custa mais R$ 100.
    """
    trades = [trade(JAN, BUY, 100, "11"), trade(FEB, SELL, 100, "9")]
    cost = operations.impact_cost(trades, FixedImpact({JAN: 1.1, FEB: 0.9}))

    assert cost is not None
    assert float(cost) == pytest.approx(200)


def test_selling_above_history_is_a_gain():
    cost = operations.impact_cost(
        [trade(JAN, SELL, 100, "11")], FixedImpact({JAN: 1.1})
    )

    assert cost is not None
    assert float(cost) == pytest.approx(-100)


def test_impact_cost_is_none_with_impact_disabled():
    impact = PriceImpact(1, enabled=False, k=0.02, decay_days=20)

    assert operations.impact_cost([trade(JAN, BUY, 1, "10")], impact) is None


def test_turnover_and_monthly_volume():
    """R$ 3.000 negociados sobre patrimônio médio de R$ 1.500: girou 2 vezes."""
    trades = [
        trade(JAN, BUY, 100, "10"),
        trade(FEB, SELL, 50, "20"),
        trade(FEB, BUY, 50, "20"),
    ]
    history = [
        PatrimonialHistoryDTO(
            snapshot_date=day,
            total_networth=Decimal(networth),
            total_equity=Decimal(0),
            total_fixed=Decimal(0),
            total_cash=Decimal(networth),
            total_contribution=Decimal(0),
        )
        for day, networth in ((JAN, "1000"), (FEB, "2000"))
    ]

    assert operations.traded_volume(trades) == Decimal("3000")
    assert operations.turnover(trades, history) == Decimal("2")
    assert [(m.month, m.bought, m.sold) for m in operations.monthly_volume(trades)] == [
        (date(2020, 1, 1), Decimal("1000"), Decimal("0")),
        (date(2020, 2, 1), Decimal("1000"), Decimal("1000")),
    ]
