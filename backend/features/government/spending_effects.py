"""
O que as medidas de gasto fazem com a economia da partida. Cada medida aprovada é um
efeito que nasce quando ela passa a valer, enche em linha reta até o atraso, vale cheio
e cai pela metade a cada meia-vida; a soma dos efeitos soma pontos ao IPCA, a SELIC reage
com uma vez e meia a inflação a mais e a bolsa cai por ponto de SELIC. Os efeitos saem só
das medidas aprovadas, então a retomada de uma partida reconstrói os mesmos números.
O `SpendingEconomy` aplica isso por cima das séries guardadas, que seguem como estavam.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from itertools import pairwise

from backend.core import repository
from backend.core.enum import EffectPhase, IndicatorSeries, MeasureKind, MeasureStatus
from backend.core.indicators import BUSINESS_DAYS_PER_YEAR, annualize_daily
from backend.core.repository.economic import IndicatorHistory
from backend.core.utils import required
from backend.features.government import spending
from backend.features.government.state import Measure

# Meses até o efeito valer cheio e meia-vida da queda, em meses
DELAY_MONTHS = 6.0
HALF_LIFE_MONTHS = 12.0
DAYS_PER_MONTH = 30.4375
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
}
# Pontos de crescimento do PIB que um passo soma, com a mesma forma do efeito na inflação
GROWTH_PER_STEP: dict[MeasureKind, float] = {MeasureKind.PUBLIC_WORKS: 0.6}
# A SELIC reage com 1,5 ponto por ponto de inflação a mais (Banco Central autônomo)
SELIC_REACTION = 1.5
# A bolsa cai 2,9% por ponto de alta da SELIC, espalhado pelo trimestre
STOCKS_PER_SELIC = 0.029
STOCKS_WINDOW_MONTHS = 3

# Janela do histórico, antes do início da partida, que mede o beta de cada ativo contra o Ibovespa
BETA_WINDOW_DAYS = 730
MIN_BETA_DAYS = 60
MAX_BETA = 3.0


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
    return (day - start).days / DAYS_PER_MONTH


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
    return SELIC_REACTION * inflation_points(effects, day)


def stocks_level(effects: Iterable[Effect], day: date) -> float:
    """O nível da bolsa contra a série guardada: cai pela média da SELIC a mais nos últimos três meses."""
    effects = tuple(effects)
    moves = [
        selic_points(effects, day - timedelta(days=round(DAYS_PER_MONTH * back)))
        for back in range(STOCKS_WINDOW_MONTHS)
    ]
    return math.exp(-STOCKS_PER_SELIC * sum(moves) / STOCKS_WINDOW_MONTHS)


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
    return effect.start + timedelta(days=round(DAYS_PER_MONTH * DELAY_MONTHS))


def faded_on(effect: Effect) -> date:
    """O dia em que o efeito já caiu abaixo do que pesa."""
    months = DELAY_MONTHS + HALF_LIFE_MONTHS * math.log2(1 / FADED)
    return effect.start + timedelta(days=round(DAYS_PER_MONTH * months))


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
        stocks_level(
            (effect,), effect.start + timedelta(days=round(DAYS_PER_MONTH * month))
        )
        - 1
        for month in range(CURVE_MONTHS + 1)
    ]
    return max(levels, key=abs)


def annual_to_daily(annual: float) -> float:
    """Taxa diária em % de uma taxa anual em fração composta por 252 dias úteis."""
    return ((1 + annual) ** (1 / BUSINESS_DAYS_PER_YEAR) - 1) * 100


class SpendingEconomy:
    """
    As séries da partida com o efeito das medidas de gasto: IPCA, SELIC, CDI e Ibovespa
    ganham o efeito por cima da série guardada, e cada ação ganha o nível da bolsa
    elevado ao beta dela. Sem medida aprovada nada muda.
    """

    def __init__(self, simulation_id: int, start: date):
        self._simulation_id = simulation_id
        self._start = start
        self._effects: tuple[Effect, ...] = ()
        self._levels: dict[date, float] = {}
        self._betas: dict[str, float] | None = None

    @property
    def effects(self) -> tuple[Effect, ...]:
        return self._effects

    def update(self, measures: Iterable[Measure]) -> None:
        """Passa a valer o conjunto de medidas aprovadas; as séries lidas de novo já trazem o efeito."""
        self._effects = effects_of(measures)
        self._levels = {}
        repository.economic.refresh_adjusted(self._simulation_id)

    def inflation_points(self, day: date) -> float:
        return inflation_points(self._effects, day)

    def selic_points(self, day: date) -> float:
        return selic_points(self._effects, day)

    def growth_points(self, day: date) -> Decimal:
        """Fração do crescimento do PIB (0.006 é 0,6 ponto) que as medidas somam no dia."""
        return Decimal(str(round(growth_points(self._effects, day) / 100, 6)))

    def level(self, day: date) -> float:
        if not self._effects:
            return 1.0
        if day not in self._levels:
            self._levels = {**self._levels, day: stocks_level(self._effects, day)}
        return self._levels[day]

    def now(self, day: date) -> list[EffectNow]:
        return effects_now(self._effects, day)

    def inflation_of(self, kind: MeasureKind, day: date) -> float:
        """Pontos de IPCA que as mudanças aprovadas de uma medida somam no dia."""
        return inflation_points([e for e in self._effects if e.kind is kind], day)

    def latest_of(self, kind: MeasureKind) -> Effect | None:
        """A última mudança aprovada da medida, que é a que ainda pesa na inflação."""
        return next((e for e in reversed(self._effects) if e.kind is kind), None)

    # Contrato com o repositório das séries

    def adjust(
        self, series: IndicatorSeries, history: IndicatorHistory
    ) -> IndicatorHistory:
        if not self._effects:
            return history
        first = min(e.start for e in self._effects)
        values = dict(history.values)
        for day in history.dates:
            if day < first:
                continue
            values[day] = self._adjusted(series, history.values[day], day)
        return IndicatorHistory(dates=history.dates, values=values)

    def _adjusted(self, series: IndicatorSeries, value: Decimal, day: date) -> Decimal:
        match series:
            case IndicatorSeries.IPCA:
                # Pontos em 12 meses viram uma fração por mês
                return value + Decimal(str(round(self.inflation_points(day) / 12, 6)))
            case IndicatorSeries.SELIC | IndicatorSeries.CDI:
                annual = float(annualize_daily(value)) + self.selic_points(day) / 100
                return Decimal(str(round(annual_to_daily(annual), 6)))
            case IndicatorSeries.IBOV:
                return Decimal(str(round(float(value) * self.level(day), 2)))

    def stock_factor(self, ticker: str, day: date) -> float:
        if not self._effects:
            return 1.0
        level = self.level(day)
        return 1.0 if level == 1.0 else level ** self._beta(ticker)

    def _beta(self, ticker: str) -> float:
        if self._betas is None:
            self._betas = self._measure_betas()
        return self._betas.get(ticker, 1.0)

    def _measure_betas(self) -> dict[str, float]:
        """Beta de cada ação contra o Ibovespa nos dois anos anteriores à partida, nas séries guardadas."""
        end = self._start - timedelta(days=1)
        begin = end - timedelta(days=BETA_WINDOW_DAYS)
        reference = repository.economic.get_history(
            IndicatorSeries.IBOV, self._simulation_id, stored=True
        )
        market = _returns(
            {
                d: float(reference.values[d])
                for d in reference.dates
                if begin <= d <= end
            }
        )
        tickers = [stock.ticker for stock in repository.stock.get_stocks()]
        closes = repository.stock.get_closes_between(
            tickers, begin, end, self._simulation_id
        )
        return {ticker: beta_of(_returns(closes[ticker]), market) for ticker in tickers}


def _returns(levels: dict[date, float]) -> dict[date, float]:
    """Retorno de cada pregão contra o anterior."""
    days = sorted(levels)
    return {
        day: levels[day] / levels[previous] - 1
        for previous, day in pairwise(days)
        if levels[previous]
    }


def beta_of(asset: dict[date, float], market: dict[date, float]) -> float:
    """Quanto o ativo anda por ponto que o mercado anda: covariância ÷ variância do mercado nos dias em comum; 1 quando faltam dias."""
    common = [d for d in asset if d in market]
    if len(common) < MIN_BETA_DAYS:
        return 1.0
    xs = [market[d] for d in common]
    ys = [asset[d] for d in common]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    variance = sum((x - mean_x) ** 2 for x in xs)
    if variance == 0:
        return 1.0
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    return max(0.0, min(MAX_BETA, covariance / variance))
