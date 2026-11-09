"""
O que as medidas de gasto fazem com a economia da partida. Cada medida aprovada é um
efeito que nasce quando ela passa a valer, enche em linha reta até o atraso, vale cheio
e cai pela metade a cada meia-vida; a soma dos efeitos soma pontos ao IPCA, a SELIC reage
pela regra do Banco Central e a bolsa cai por ponto de SELIC. Os efeitos saem só das
medidas aprovadas, então a retomada de uma partida reconstrói os mesmos números. A
camada da economia (`economy/layer.py`) leva isso para as séries da partida.
"""

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import EffectPhase, MeasureKind, MeasureStatus
from backend.core.periods import DAYS_PER_MONTH
from backend.core.utils import required
from backend.features.economy.layer import (
    STOCKS_PER_SELIC,
    central_bank_reaction,
    months_to_days,
    quarter_mean,
)
from backend.features.government import spending
from backend.features.government.state import Measure

# Meses até o efeito valer cheio e meia-vida da queda, em meses
DELAY_MONTHS = 6.0
HALF_LIFE_MONTHS = 12.0
# Resto do efeito abaixo do qual ele já não pesa: a medida "some"
FADED = 0.05
# Meses que o desenho da curva do efeito cobre
CURVE_MONTHS = 36

# Pontos de IPCA em 12 meses que um passo soma quando o efeito vale cheio
INFLATION_PER_STEP: dict[MeasureKind, float] = {
    MeasureKind.WELFARE_SPENDING: 0.25,
    MeasureKind.SERVANT_RAISE: 0.20,
    MeasureKind.RETIREE_RAISE: 0.25,
    MeasureKind.PUBLIC_WORKS: 0.15,
    MeasureKind.OPERATING_COST: 0.10,
}
# Pontos de crescimento do PIB que um passo soma, com a mesma forma do efeito na inflação;
# o custeio, como o auxílio e os reajustes, age pelo impulso fiscal do primário
GROWTH_PER_STEP: dict[MeasureKind, float] = {MeasureKind.PUBLIC_WORKS: 0.6}


@dataclass(frozen=True)
class Effect:
    """O efeito de uma medida aprovada: quando vale e quantos passos ela anda (negativo é corte)."""

    measure_id: int
    kind: MeasureKind
    start: date
    steps: float


@dataclass(frozen=True)
class EffectNow:
    """Um efeito no dia: a fase e a parte dele na inflação, na SELIC e na bolsa."""

    effect: Effect
    phase: EffectPhase
    # Pontos de IPCA, pontos de SELIC e variação da bolsa (fração) que o efeito põe hoje
    inflation: float
    selic: float
    stocks: float


def elapsed_months(start: date, day: date) -> float:
    return (day - start).days / float(DAYS_PER_MONTH)


def shape(months: float) -> float:
    """A fração do efeito cheio `months` depois de valer: sobe em linha reta até o atraso e depois cai pela metade a cada meia-vida."""
    if months <= 0:
        return 0.0
    if months < DELAY_MONTHS:
        return months / DELAY_MONTHS
    return 0.5 ** ((months - DELAY_MONTHS) / HALF_LIFE_MONTHS)


def effects_of(measures: Iterable[Measure]) -> tuple[Effect, ...]:
    return tuple(
        Effect(
            measure_id=m.id,
            kind=m.kind,
            start=required(m.effective),
            steps=float(spending.steps_of(m.kind, m.value, m.before)),
        )
        for m in sorted(measures, key=lambda m: m.id)
        if m.kind.is_spending
        and m.status is MeasureStatus.APPROVED
        and m.effective is not None
    )


def inflation_points(effects: Iterable[Effect], day: date) -> float:
    """Pontos de IPCA em 12 meses que as medidas somam no dia."""
    return sum(
        INFLATION_PER_STEP[e.kind] * e.steps * shape(elapsed_months(e.start, day))
        for e in effects
    )


def growth_points(effects: Iterable[Effect], day: date) -> float:
    """Pontos de crescimento do PIB que as medidas somam no dia."""
    return sum(
        GROWTH_PER_STEP.get(e.kind, 0.0) * e.steps * shape(elapsed_months(e.start, day))
        for e in effects
    )


def selic_points(effects: Iterable[Effect], day: date) -> float:
    return central_bank_reaction(inflation_points(effects, day))


def stocks_level(effects: Iterable[Effect], day: date) -> float:
    """O nível da bolsa contra a série guardada: cai pela média da SELIC a mais nos últimos três meses."""
    effects = tuple(effects)
    return math.exp(
        -STOCKS_PER_SELIC * quarter_mean(lambda d: selic_points(effects, d), day)
    )


def phase_of(effect: Effect, day: date) -> EffectPhase:
    months = elapsed_months(effect.start, day)
    if months <= 0:
        return EffectPhase.WAITING
    if months < DELAY_MONTHS:
        return EffectPhase.RISING
    if shape(months) < FADED:
        return EffectPhase.FADED
    return EffectPhase.FALLING


def effects_now(effects: Iterable[Effect], day: date) -> list[EffectNow]:
    """Cada efeito no dia, com a parte dele na inflação, na SELIC e na bolsa."""
    result = []
    for effect in effects:
        own = (effect,)
        selic = selic_points(own, day)
        result.append(
            EffectNow(
                effect=effect,
                phase=phase_of(effect, day),
                inflation=inflation_points(own, day),
                selic=selic,
                stocks=stocks_level(own, day) - 1,
            )
        )
    return result


def peak_on(effect: Effect) -> date:
    """O dia em que o efeito chega cheio."""
    return effect.start + timedelta(days=months_to_days(DELAY_MONTHS))


def faded_on(effect: Effect) -> date:
    """O dia em que o efeito já caiu abaixo do que pesa."""
    months = DELAY_MONTHS + HALF_LIFE_MONTHS * math.log2(1 / FADED)
    return effect.start + timedelta(days=months_to_days(months))


def curve(kind: MeasureKind, steps: float) -> list[float]:
    """Os pontos de IPCA que a medida soma a cada mês depois de valer, do mês 0 ao fim do desenho."""
    return [
        INFLATION_PER_STEP[kind] * steps * shape(month)
        for month in range(CURVE_MONTHS + 1)
    ]


def peak_inflation(kind: MeasureKind, steps: float) -> float:
    """Os pontos de IPCA que a medida soma quando o efeito vale cheio."""
    return INFLATION_PER_STEP[kind] * steps


def peak_stocks(kind: MeasureKind, steps: float) -> float:
    """A maior variação da bolsa que a medida causa no trimestre, contra a série guardada."""
    effect = Effect(0, kind, date(2000, 1, 1), steps)
    levels = [
        stocks_level((effect,), effect.start + timedelta(days=months_to_days(month)))
        - 1
        for month in range(CURVE_MONTHS + 1)
    ]
    return max(levels, key=abs)


class SpendingEconomy:
    """
    Os efeitos das medidas de gasto aprovadas na partida. `on_change` roda quando o
    conjunto muda, para as séries da partida serem lidas de novo com o efeito novo.
    """

    def __init__(self, on_change: Callable[[], None] = lambda: None):
        self._effects: tuple[Effect, ...] = ()
        self._first: date | None = None
        self._on_change = on_change

    @property
    def effects(self) -> tuple[Effect, ...]:
        return self._effects

    def use_on_change(self, on_change: Callable[[], None]) -> None:
        self._on_change = on_change

    def update(self, measures: Iterable[Measure]) -> None:
        """Passa a valer o conjunto de medidas aprovadas."""
        self._effects = effects_of(measures)
        self._first = min((e.start for e in self._effects), default=None)
        self._on_change()

    def first_day(self) -> date | None:
        return self._first

    def inflation_points(self, day: date) -> float:
        return inflation_points(self._effects, day)

    def selic_points(self, day: date) -> float:
        return selic_points(self._effects, day)

    def growth_points(self, day: date) -> Decimal:
        """Fração do crescimento do PIB (0.006 é 0,6 ponto) que as medidas somam no dia."""
        return Decimal(str(round(growth_points(self._effects, day) / 100, 6)))

    def now(self, day: date) -> list[EffectNow]:
        return effects_now(self._effects, day)

    def inflation_of(self, kind: MeasureKind, day: date) -> float:
        """Pontos de IPCA que as mudanças aprovadas de uma medida somam no dia."""
        return inflation_points([e for e in self._effects if e.kind is kind], day)

    def latest_of(self, kind: MeasureKind) -> Effect | None:
        """A última mudança aprovada da medida, que é a que ainda pesa na inflação."""
        return next((e for e in reversed(self._effects) if e.kind is kind), None)
