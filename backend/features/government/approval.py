"""
A aprovação do governo: começa em 50 na posse e se move pelos fatores do mês. Tudo aqui
é função pura sobre o estado político e o mercado do dia.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from backend.core.enum import ApprovalFactorKind, IndicatorSeries, MeasureStatus
from backend.core.indicators import annual_index_rate, last_known_value
from backend.core.utils import required
from backend.features.government import measures as rules
from backend.features.government.state import Measure, Term

BASE = 50
# Abaixo do piso, 3 meses seguidos levam ao impeachment
FLOOR = 25
IMPEACHMENT_MONTHS = 3
# Inflação dentro da meta soma 4 pontos; cada ponto acima da meta tira 3
INFLATION_ON_TARGET = 4
INFLATION_PENALTY = Decimal(3)
# A bolsa soma ou tira 1 ponto a cada 5% de alta ou queda, até 6
STOCKS_STEP = Decimal("0.05")
STOCKS_LIMIT = 6

# Meta de inflação do CMN em cada ano; fora da tabela vale a última
INFLATION_TARGETS: dict[int, Decimal] = {
    2000: Decimal("6.0"),
    2001: Decimal("4.0"),
    2002: Decimal("3.5"),
    2003: Decimal("4.0"),
    2004: Decimal("5.5"),
    **dict.fromkeys(range(2005, 2019), Decimal("4.5")),
    2019: Decimal("4.25"),
    2020: Decimal("4.0"),
    2021: Decimal("3.75"),
    2022: Decimal("3.5"),
    2023: Decimal("3.25"),
    2024: Decimal("3.0"),
}
DEFAULT_TARGET = Decimal("3.0")
MINUS = "\u2212"


@dataclass(frozen=True)
class Market:
    """O que a aprovação lê do mercado no dia: a inflação e a bolsa dos últimos 12 meses."""

    inflation: Decimal
    # Alta (0.18) ou queda (-0.10) do Ibovespa; nulo quando a série não cobre o período
    stocks: Decimal | None
    # Meta de inflação do ano (0.04)
    target: Decimal


@dataclass(frozen=True)
class Factor:
    kind: ApprovalFactorKind
    points: int
    description: str
    measure_id: int | None = None


@dataclass(frozen=True)
class Approval:
    value: int
    factors: list[Factor]
    # Medidas aprovadas que ainda vão pesar quando valerem
    upcoming: list[Measure]


def inflation_target(day: date) -> Decimal:
    if day.year in INFLATION_TARGETS:
        return INFLATION_TARGETS[day.year] / 100
    return DEFAULT_TARGET / 100


def market_on(day: date) -> Market:
    stocks = None
    now = last_known_value(IndicatorSeries.IBOV, day)
    before = last_known_value(IndicatorSeries.IBOV, day - timedelta(days=365))
    if now is not None and before:
        stocks = now / before - 1
    return Market(
        inflation=annual_index_rate(IndicatorSeries.IPCA, day),
        stocks=stocks,
        target=inflation_target(day),
    )


def month_label(day: date) -> str:
    return f"{rules.MONTHS[day.month - 1]} {day.year}"


def _signed(points: int) -> str:
    return f"{points:+d}".replace("-", MINUS)


def _rounded(value: Decimal) -> int:
    return int(value.quantize(Decimal(1), ROUND_HALF_UP))


def inflation_factor(market: Market) -> Factor:
    shown = rules.percent(market.inflation)
    target = rules.percent(market.target)
    excess = max(Decimal(0), market.inflation - market.target) * 100
    points = _rounded(INFLATION_ON_TARGET - INFLATION_PENALTY * excess)
    where = "dentro da meta" if excess == 0 else "acima da meta"
    return Factor(
        ApprovalFactorKind.INFLATION,
        points,
        f"Inflação de {shown} em 12 meses, {where} de {target}",
    )


def stocks_factor(market: Market) -> Factor | None:
    if market.stocks is None:
        return None
    steps = int(market.stocks / STOCKS_STEP)
    points = max(-STOCKS_LIMIT, min(STOCKS_LIMIT, steps))
    if points == 0:
        return None
    movement = "subiu" if market.stocks > 0 else "caiu"
    shown = rules.percent(abs(market.stocks))
    return Factor(
        ApprovalFactorKind.STOCKS,
        points,
        f"Bolsa {movement} {shown} em 12 meses: {'+' if points > 0 else MINUS}1 a cada 5%",
    )


def measure_factors(measures: Iterable[Measure], today: date) -> list[Factor]:
    """Corte soma enquanto o governo dura; imposto novo tira ao valer e some em 6 meses."""
    factors = []
    for measure in measures:
        effective = required(measure.effective)
        if effective > today:
            continue
        impact = rules.approval_impact(measure)
        since = f"valendo desde {month_label(effective)}"
        if impact > 0:
            factors.append(
                Factor(
                    ApprovalFactorKind.TAX_CUT,
                    impact,
                    f"Corte: {rules.title(measure)}, {since}",
                    measure.id,
                )
            )
            continue
        points = rules.current_effect(measure, today)
        if points == 0:
            continue
        ends = effective + timedelta(days=rules.FADE_DAYS)
        factors.append(
            Factor(
                ApprovalFactorKind.NEW_TAX,
                points,
                f"Imposto novo: {rules.title(measure)}, {since}; "
                f"começou em {_signed(impact)} e some em {month_label(ends)}",
                measure.id,
            )
        )
    return factors


def term_measures(measures: Iterable[Measure], term: Term) -> list[Measure]:
    """As medidas aprovadas do governo em curso."""
    return [
        m
        for m in measures
        if m.status is MeasureStatus.APPROVED
        and m.term_start == term.start
        and m.effective is not None
    ]


def assess(
    term: Term, measures: Iterable[Measure], market: Market, today: date
) -> Approval:
    approved = term_measures(measures, term)
    factors = [
        Factor(
            ApprovalFactorKind.BASE,
            BASE,
            "Base: todo governo começa em 50% na posse",
        ),
        inflation_factor(market),
        stocks_factor(market),
        *measure_factors(approved, today),
    ]
    present = [f for f in factors if f is not None]
    value = max(0, min(100, sum(f.points for f in present)))
    return Approval(
        value=value,
        factors=present,
        upcoming=[
            m
            for m in approved
            if m.effective and m.effective > today and rules.approval_impact(m) < 0
        ],
    )
