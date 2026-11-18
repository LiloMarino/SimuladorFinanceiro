"""O desempenho da cota contra o CDI: o retorno total na janela e o corte dos pontos."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.fund import FundDistributionDTO
from backend.features.funds.performance import (
    PERFORMANCE_WINDOW,
    NavPoint,
    cut_window,
    excess_return,
)

START = date(2020, 1, 6)


def distribution(paid_on: date, paid_per_quota: str | None) -> FundDistributionDTO:
    return FundDistributionDTO(
        data_com=paid_on - timedelta(days=5),
        realized_profit=Decimal(0),
        rate=Decimal(0),
        quotas=Decimal(0),
        per_quota=Decimal(0),
        paid_per_quota=None if paid_per_quota is None else Decimal(paid_per_quota),
        paid=None,
        paid_on=paid_on,
    )


def cdi(growth: str):
    """O CDI que rende `growth` (1,04 é 4%) em qualquer intervalo."""
    return lambda start, end: Decimal(growth)


def test_excess_return_is_the_nav_growth_minus_the_cdi():
    points = [NavPoint(START, Decimal(100))]

    # A cota foi de 100 a 106 (6%) e o CDI rendeu 4%: 2 pontos acima
    result = excess_return(
        points, Decimal(106), START + timedelta(days=30), [], cdi("1.04")
    )

    assert result == Decimal("0.02")


def test_excess_return_is_negative_when_the_quota_trails_the_cdi():
    points = [NavPoint(START, Decimal(100))]

    result = excess_return(
        points, Decimal(101), START + timedelta(days=30), [], cdi("1.04")
    )

    assert result == Decimal("-0.03")


def test_excess_return_without_history_is_zero():
    assert excess_return([], Decimal(100), START, [], cdi("1.04")) == 0


def test_the_window_has_one_hundred_and_twenty_six_points():
    points = [NavPoint(START + timedelta(days=i), Decimal(100)) for i in range(200)]

    cut = cut_window(points)

    assert len(cut) == PERFORMANCE_WINDOW == 126
    assert cut[-1] == points[-1]
    assert cut[0] == points[-126]


def test_what_the_fund_paid_per_quota_in_the_window_counts_as_return():
    points = [NavPoint(START, Decimal(100))]
    today = START + timedelta(days=60)
    paid = [
        # Pago antes do início da janela, não entra
        distribution(START, "5"),
        distribution(START + timedelta(days=20), "2"),
        # Ainda sem pagamento, não entra
        distribution(START + timedelta(days=40), None),
    ]

    # O PL caiu a 100 mas a cota pagou 2: retorno de 2% contra 1% do CDI
    result = excess_return(points, Decimal(100), today, paid, cdi("1.01"))

    assert result == Decimal("0.01")
