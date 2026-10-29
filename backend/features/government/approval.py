"""
A aprovação do governo, grupo a grupo: o mercado e as medidas vigentes dão um alvo de 0
a 100 para cada grupo de eleitores, e a satisfação anda um terço do caminho até ele a
cada fechamento de mês. A aprovação geral é a média das satisfações pesada pelo tamanho
de cada grupo. Tudo aqui é função pura sobre o estado político e o mercado do dia.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from backend.core.enum import (
    ApprovalFactorKind,
    IndicatorSeries,
    MeasureStatus,
    VoterGroup,
)
from backend.core.indicators import (
    annual_index_rate,
    inflation_target,
    last_known_value,
)
from backend.core.utils import required
from backend.features.government import measures as rules
from backend.features.government import voters
from backend.features.government.state import Measure, Term

G = VoterGroup

HUNDRED = Decimal(100)
ZERO = Decimal(0)

# Sem nada a favor nem contra, o grupo mira o meio
NEUTRAL = Decimal(50)
# A satisfação anda um terço do caminho até o alvo a cada fechamento: com alvo 70 e
# satisfação 40, fica 50, depois 57 e depois 61
STEP = Decimal(1) / 3

# Impeachment: abaixo do piso por 6 fechamentos seguidos, só depois da carência de 12
FLOOR = 25
IMPEACHMENT_MONTHS = 6
GRACE_MONTHS = 12
# A faixa de risco: aprovação a menos de 10 pontos do piso, ou já abaixo dele
RISK_MARGIN = 10

# Inflação: pontos por ponto percentual abaixo da meta somada a 1,5, até 5 para cada lado
INFLATION_TOLERANCE = Decimal("1.5")
INFLATION_CAP = Decimal(5)
INFLATION_WEIGHT: dict[VoterGroup, Decimal] = {
    G.INVESTORS: Decimal(2),
    G.ENTREPRENEURS: Decimal(2),
    G.FORMAL_WORKERS: Decimal("3.5"),
    G.PUBLIC_SERVANTS: Decimal(3),
    G.RETIREES: Decimal(4),
    G.WELFARE: Decimal(4),
}
# SELIC: pontos por ponto percentual acima de 10% ao ano, até 6 para cada lado
SELIC_NEUTRAL = Decimal(10)
SELIC_CAP = Decimal(6)
SELIC_WEIGHT: dict[VoterGroup, Decimal] = {
    G.INVESTORS: Decimal("0.5"),
    G.ENTREPRENEURS: Decimal(-2),
    G.FORMAL_WORKERS: Decimal("-1.5"),
    G.PUBLIC_SERVANTS: ZERO,
    G.RETIREES: Decimal("1.5"),
    G.WELFARE: Decimal("-0.5"),
}
# Ibovespa: pontos a cada 10% de alta em 12 meses acima de 5%, até 3 passos para cada lado
STOCKS_NEUTRAL = Decimal("0.05")
STOCKS_STEP = Decimal("0.10")
STOCKS_CAP = Decimal(3)
STOCKS_WEIGHT: dict[VoterGroup, Decimal] = {
    G.INVESTORS: Decimal(8),
    G.ENTREPRENEURS: Decimal(4),
    G.FORMAL_WORKERS: Decimal(1),
    G.PUBLIC_SERVANTS: ZERO,
    G.RETIREES: Decimal(1),
    G.WELFARE: ZERO,
}
# Medida: 6 pontos por unidade de reação do grupo, cheia ao valer e pela metade a cada 6 meses
MEASURE_POINTS = Decimal(6)
MEASURE_HALF_LIFE_MONTHS = Decimal(6)
DAYS_PER_MONTH = Decimal("30.4375")

SATISFACTION_PRECISION = Decimal("0.0001")


@dataclass(frozen=True)
class Market:
    """O que o alvo lê do mercado no dia: inflação, SELIC e bolsa."""

    inflation: Decimal
    # Taxa anual da SELIC (0.1075)
    selic: Decimal
    # Alta (0.18) ou queda (-0.10) do Ibovespa em 12 meses; nulo quando a série não cobre
    stocks: Decimal | None
    # Meta de inflação do ano (0.04)
    target: Decimal


@dataclass(frozen=True)
class Factor:
    kind: ApprovalFactorKind
    points: Decimal
    description: str
    measure_id: int | None = None


@dataclass(frozen=True)
class GroupTarget:
    """Onde a satisfação do grupo para se nada mudar, e o que a puxa até lá."""

    target: Decimal
    factors: list[Factor]


@dataclass(frozen=True)
class Approval:
    """A aprovação de hoje: a satisfação de cada grupo, o alvo dela e o que ainda vai pesar."""

    satisfaction: dict[VoterGroup, Decimal]
    targets: dict[VoterGroup, GroupTarget]
    # Medidas aprovadas que ainda vão pesar quando valerem
    upcoming: list[Measure]

    @property
    def value(self) -> int:
        return rounded(overall(self.satisfaction))

    @property
    def target(self) -> int:
        return rounded(overall({g: t.target for g, t in self.targets.items()}))


def market_on(day: date) -> Market:
    stocks = None
    now = last_known_value(IndicatorSeries.IBOV, day)
    before = last_known_value(IndicatorSeries.IBOV, day - timedelta(days=365))
    if now is not None and before:
        stocks = now / before - 1
    return Market(
        inflation=annual_index_rate(IndicatorSeries.IPCA, day),
        selic=annual_index_rate(IndicatorSeries.SELIC, day),
        stocks=stocks,
        target=inflation_target(day),
    )


def rounded(value: Decimal) -> int:
    return int(value.quantize(Decimal(1), ROUND_HALF_UP))


def month_label(day: date) -> str:
    return f"{rules.MONTHS[day.month - 1]} {day.year}"


def overall(values: Mapping[VoterGroup, Decimal]) -> Decimal:
    """A média dos grupos pesada pelo tamanho de cada um no eleitorado."""
    return sum((voters.WEIGHTS[g] * v for g, v in values.items()), ZERO)


def _clip(value: Decimal, limit: Decimal) -> Decimal:
    return max(-limit, min(limit, value))


def _pp(value: Decimal) -> Decimal:
    """Fração (0.04) em pontos percentuais (4)."""
    return value * HUNDRED


def inflation_factor(group: VoterGroup, market: Market) -> Factor:
    gap = _clip(
        _pp(market.target) + INFLATION_TOLERANCE - _pp(market.inflation), INFLATION_CAP
    )
    shown = rules.percent(market.inflation)
    target = rules.percent(market.target)
    where = "abaixo" if market.inflation < market.target else "acima"
    return Factor(
        ApprovalFactorKind.INFLATION,
        INFLATION_WEIGHT[group] * gap,
        f"Inflação de {shown} em 12 meses, {where} da meta de {target}",
    )


def selic_factor(group: VoterGroup, market: Market) -> Factor:
    gap = _clip(_pp(market.selic) - SELIC_NEUTRAL, SELIC_CAP)
    where = "acima" if _pp(market.selic) > SELIC_NEUTRAL else "abaixo"
    return Factor(
        ApprovalFactorKind.SELIC,
        SELIC_WEIGHT[group] * gap,
        f"SELIC de {rules.percent(market.selic)}, {where} dos "
        f"{rules.number(SELIC_NEUTRAL)}% neutros",
    )


def stocks_factor(group: VoterGroup, market: Market) -> Factor | None:
    if market.stocks is None:
        return None
    steps = _clip((market.stocks - STOCKS_NEUTRAL) / STOCKS_STEP, STOCKS_CAP)
    movement = "subiu" if market.stocks >= 0 else "caiu"
    return Factor(
        ApprovalFactorKind.STOCKS,
        STOCKS_WEIGHT[group] * steps,
        f"Bolsa {movement} {rules.percent(abs(market.stocks))} em 12 meses",
    )


def measure_fade(measure: Measure, today: date) -> Decimal:
    """Quanto do efeito da medida ainda pesa: cheio ao valer e pela metade a cada 6 meses."""
    elapsed = Decimal((today - required(measure.effective)).days) / DAYS_PER_MONTH
    return Decimal("0.5") ** (elapsed / MEASURE_HALF_LIFE_MONTHS)


def measure_reaction(group: VoterGroup, measure: Measure) -> Decimal:
    """Pontos no alvo do grupo quando a medida vale cheia."""
    effects = voters.measure_effects(measure.kind, measure.value, measure.before)
    return MEASURE_POINTS * voters.reaction(group, effects)


def measure_impact(measure: Measure) -> int:
    """O que a medida muda no alvo da aprovação geral quando vale cheia."""
    return rounded(
        overall({g: measure_reaction(g, measure) for g in VoterGroup}),
    )


def measure_factors(
    group: VoterGroup, measures: Iterable[Measure], today: date
) -> list[Factor]:
    factors = []
    for measure in measures:
        effective = required(measure.effective)
        if effective > today:
            continue
        points = measure_reaction(group, measure) * measure_fade(measure, today)
        if points.quantize(Decimal("0.1")) == 0:
            continue
        factors.append(
            Factor(
                ApprovalFactorKind.MEASURE,
                points,
                f"Medida: {rules.title(measure)}, valendo desde {month_label(effective)}",
                measure.id,
            )
        )
    return factors


def group_target(
    group: VoterGroup, market: Market, measures: Iterable[Measure], today: date
) -> GroupTarget:
    """O alvo do grupo: o neutro mais o que cada resultado e cada medida vigente puxam, de 0 a 100."""
    factors = [
        Factor(
            ApprovalFactorKind.BASE,
            NEUTRAL,
            "Ponto neutro: sem nada a favor nem contra, o grupo fica no meio",
        ),
        inflation_factor(group, market),
        selic_factor(group, market),
        stocks_factor(group, market),
        *measure_factors(group, measures, today),
    ]
    present = [f for f in factors if f is not None]
    total = sum((f.points for f in present), ZERO)
    return GroupTarget(voters.clamp(total), present)


def term_measures(measures: Iterable[Measure], term: Term) -> list[Measure]:
    """As medidas aprovadas do governo em curso."""
    return [
        m
        for m in measures
        if m.status is MeasureStatus.APPROVED
        and m.term_start == term.start
        and m.effective is not None
    ]


def next_satisfaction(current: Decimal, target: Decimal) -> Decimal:
    """Um terço do caminho até o alvo."""
    return (current + (target - current) * STEP).quantize(SATISFACTION_PRECISION)


def months_in_office(term: Term, month: date) -> int:
    """O mês do fechamento contado desde a posse: o mês da posse é o 1º."""
    return (month.year - term.start.year) * 12 + month.month - term.start.month + 1


def in_grace(term: Term, month: date) -> bool:
    """Nos primeiros 12 meses do mandato o piso não conta."""
    return months_in_office(term, month) <= GRACE_MONTHS


def grace_end(term: Term) -> date:
    """O último dia do 12º mês do mandato."""
    index = term.start.year * 12 + term.start.month - 1 + GRACE_MONTHS
    year, month = divmod(index, 12)
    first_after = date(year, month + 1, 1)
    return first_after - timedelta(days=1)


def assess(
    term: Term,
    satisfaction: dict[VoterGroup, Decimal],
    measures: Iterable[Measure],
    market: Market,
    today: date,
) -> Approval:
    approved = term_measures(measures, term)
    return Approval(
        satisfaction=satisfaction,
        targets={g: group_target(g, market, approved, today) for g in VoterGroup},
        upcoming=[
            m
            for m in approved
            if m.effective and m.effective > today and measure_impact(m) != 0
        ],
    )
