"""
Nota de risco: 100 pontos repartidos em alavancagem (40), volatilidade (30) e
pagamentos em dia (30). Cálculo puro; quem chama fornece os números do mês.
"""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal

from backend.core.enum import CreditGrade
from backend.features.credit.price import ZERO, add_months
from backend.features.credit.rules import (
    LATE_WINDOW_MONTHS,
    LEVERAGE_MAX_POINTS,
    LEVERAGE_POINTS_PER_UNIT,
    PAYMENT_MAX_POINTS,
    PAYMENT_PENALTY,
    VOLATILITY_CEILING,
    VOLATILITY_MAX_POINTS,
    VOLATILITY_MIN_SAMPLE,
    grade_for_points,
    next_tier,
)

CENT = Decimal("0.01")
POINT = Decimal(1)


@dataclass(frozen=True)
class RatingScore:
    leverage_points: Decimal
    volatility_points: Decimal
    payment_points: Decimal

    @property
    def total(self) -> Decimal:
        return self.leverage_points + self.volatility_points + self.payment_points

    @property
    def points(self) -> int:
        """Pontos inteiros, como a tela os mostra."""
        return int(self.total.quantize(POINT, ROUND_HALF_UP))

    @property
    def grade(self) -> CreditGrade:
        return grade_for_points(self.total)


def leverage(debt: Decimal, networth: Decimal) -> Decimal:
    """Dívida sobre o patrimônio líquido; sem patrimônio, a dívida não cabe em nada."""
    if debt <= 0:
        return ZERO
    return debt / networth if networth > 0 else Decimal("Infinity")


def leverage_points(value: Decimal) -> Decimal:
    return max(LEVERAGE_MAX_POINTS - LEVERAGE_POINTS_PER_UNIT * value, ZERO)


def volatility_points(volatility: Decimal | None, sample_size: int) -> Decimal:
    """Pouco histórico conta como volatilidade zero: ninguém perde ponto por começar."""
    if volatility is None or sample_size < VOLATILITY_MIN_SAMPLE:
        return VOLATILITY_MAX_POINTS
    return max(VOLATILITY_MAX_POINTS * (1 - volatility / VOLATILITY_CEILING), ZERO)


def payment_points(late_installments: int) -> Decimal:
    return max(PAYMENT_MAX_POINTS - PAYMENT_PENALTY * late_installments, ZERO)


def count_recent_late(late_dates: list[date], today: date) -> int:
    """Parcelas que atrasaram na janela de 12 meses que termina em `today`."""
    start = add_months(today, -LATE_WINDOW_MONTHS)
    return sum(1 for day in late_dates if start < day <= today)


def score(
    debt: Decimal,
    networth: Decimal,
    volatility: Decimal | None,
    sample_size: int,
    late_installments: int,
) -> RatingScore:
    return RatingScore(
        leverage_points=leverage_points(leverage(debt, networth)),
        volatility_points=volatility_points(volatility, sample_size),
        payment_points=payment_points(late_installments),
    )


def payoff_to_next_grade(
    current: RatingScore, debt: Decimal, networth: Decimal
) -> Decimal | None:
    """
    Quanto quitar para a nota subir, com a volatilidade e os pagamentos como
    estão. Quitar troca caixa por dívida e não mexe no patrimônio líquido.
    None quando a alavancagem sozinha não alcança a nota de cima.
    """
    tier = next_tier(current.grade)
    if tier is None or networth <= 0:
        return None
    needed = (
        Decimal(tier.min_points) - current.volatility_points - current.payment_points
    )
    if needed > LEVERAGE_MAX_POINTS:
        return None
    target_leverage = (LEVERAGE_MAX_POINTS - needed) / LEVERAGE_POINTS_PER_UNIT
    return max((debt - target_leverage * networth).quantize(CENT, ROUND_CEILING), ZERO)


def volatility_to_next_grade(current: RatingScore) -> Decimal | None:
    """
    Maior volatilidade anual, em pontos percentuais inteiros, que leva à nota de
    cima com a alavancagem e os pagamentos como estão. None quando nem
    volatilidade zero basta.
    """
    tier = next_tier(current.grade)
    if tier is None:
        return None
    needed = Decimal(tier.min_points) - current.leverage_points - current.payment_points
    if needed > VOLATILITY_MAX_POINTS:
        return None
    ceiling = VOLATILITY_CEILING * (1 - needed / VOLATILITY_MAX_POINTS)
    return (ceiling * 100).quantize(POINT, ROUND_FLOOR) / 100
