"""
Nota geral de desempenho (D10): quatro eixos de peso igual, cada um a média das
suas métricas, e cada métrica convertida em pontos por faixas fixas, iguais em
toda partida, para que a nota compare partidas diferentes.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import get_args

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.statistics_report import (
    ScoreAxis,
    ScoreAxisDTO,
    ScoreDTO,
    ScoreMetric,
    ScoreMetricDTO,
    SeriesPointDTO,
)
from backend.core.enum import IndicatorSeries
from backend.core.indicators import last_known_value
from backend.features.statistics import returns, risk

# Abaixo de ~3 meses, anualizar engana: 10 dias com +2% viram ~64% ao ano
MIN_SCORE_DAYS = risk.ROLLING_WINDOW


@dataclass(frozen=True)
class Band:
    """A reta que leva o valor da métrica a pontos: `zero` vale 0 e `hundred` vale 100."""

    metric: ScoreMetric
    axis: ScoreAxis
    zero: Decimal
    hundred: Decimal

    def points(self, value: Decimal) -> Decimal:
        """Pontos na reta, com chão 0 e sem teto."""
        return max(Decimal(0), 100 * (value - self.zero) / (self.hundred - self.zero))


BANDS = [
    Band("return_over_cdi", "return", Decimal("-0.10"), Decimal("0.10")),
    Band("return_over_ibov", "return", Decimal("-0.15"), Decimal("0.15")),
    Band("max_drawdown", "risk", Decimal("0.50"), Decimal(0)),
    Band("annual_volatility", "risk", Decimal("0.40"), Decimal(0)),
    Band("time_underwater", "risk", Decimal(252), Decimal(0)),
    Band("worst_month", "risk", Decimal("-0.20"), Decimal(0)),
    Band("months_above_cdi", "consistency", Decimal(0), Decimal(1)),
    Band("positive_months", "consistency", Decimal(0), Decimal(1)),
    Band("sharpe_ratio", "efficiency", Decimal(-1), Decimal(2)),
    Band("sortino_ratio", "efficiency", Decimal(-1), Decimal(3)),
]


def build_score(values: Mapping[ScoreMetric, Decimal | None]) -> ScoreDTO:
    """
    Decomposição completa da nota: cada métrica com o valor e os pontos, cada eixo
    com a média das métricas medidas (a que falta sai da média), e o total como a
    soma dos eixos que têm alguma métrica.
    """
    axes = []
    for axis in get_args(ScoreAxis.__value__):
        metrics = [
            ScoreMetricDTO(
                metric=band.metric,
                value=values.get(band.metric),
                points=_points(band, values.get(band.metric)),
            )
            for band in BANDS
            if band.axis == axis
        ]
        measured = [m.points for m in metrics if m.points is not None]
        axes.append(
            ScoreAxisDTO(
                axis=axis,
                points=sum(measured, Decimal(0)) / len(measured) if measured else None,
                metrics=metrics,
            )
        )
    total = sum((a.points for a in axes if a.points is not None), Decimal(0))
    return ScoreDTO(total=total, axes=axes)


class _ScoreWalk:
    """
    As métricas da nota andando um snapshot por vez: `score` dá a nota sobre os
    snapshots vistos até ali, a mesma de `player_score` sobre esse começo do histórico.
    """

    def __init__(self, first: PatrimonialHistoryDTO) -> None:
        self._previous = first
        self._periods = 0
        self._ibov_base = last_known_value(IndicatorSeries.IBOV, first.snapshot_date)
        self._ibov_level = self._ibov_base
        self._cdi_growth = Decimal(1)
        # Os retornos do dia: quantos, a cota, o pico dela e as somas da volatilidade
        self._returns = 0
        self._quota = self._peak = Decimal(1)
        self._max_drawdown = Decimal(0)
        self._underwater = self._longest_underwater = 0
        self._sum = self._squares = Decimal(0)
        # O excesso sobre o CDI de cada dia, para o Sharpe e o Sortino
        self._excess = self._downside = Decimal(0)
        # Os meses fechados resumidos; o mês corrente fica em aberto
        self._worst_month: Decimal | None = None
        self._months = self._months_above_cdi = self._positive_months = 0
        self._month: date | None = None
        self._month_value = self._month_cdi = Decimal(1)

    def add(self, snapshot: PatrimonialHistoryDTO) -> None:
        day = snapshot.snapshot_date
        self._periods += 1
        cdi = risk.cdi_return(day)
        self._cdi_growth *= 1 + cdi
        if self._ibov_base:
            self._ibov_level = last_known_value(IndicatorSeries.IBOV, day)

        previous, self._previous = self._previous, snapshot
        if previous.total_networth <= 0:
            return
        contribution = snapshot.total_contribution - previous.total_contribution
        gain = snapshot.total_networth - contribution - previous.total_networth
        daily = gain / previous.total_networth

        self._returns += 1
        self._quota *= 1 + daily
        self._peak = max(self._peak, self._quota)
        drawdown = (self._peak - self._quota) / self._peak
        self._max_drawdown = max(self._max_drawdown, drawdown)
        self._underwater = self._underwater + 1 if drawdown > 0 else 0
        self._longest_underwater = max(self._longest_underwater, self._underwater)
        self._sum += daily
        self._squares += daily * daily

        excess = daily - cdi
        self._excess += excess
        self._downside += min(excess, Decimal(0)) ** 2

        month = day.replace(day=1)
        if month != self._month:
            self._close_month()
            self._month = month
            self._month_value = self._month_cdi = Decimal(1)
        self._month_value *= 1 + daily
        self._month_cdi *= 1 + cdi

    def score(self) -> ScoreDTO | None:
        """None com menos de 63 retornos."""
        n = self._returns
        if n < MIN_SCORE_DAYS:
            return None

        annual = (
            self._quota ** (risk.DAYS_PER_YEAR / n) - 1
            if self._quota > 0
            else Decimal(-1)
        )
        cdi = returns.annualize_growth(self._cdi_growth - 1, self._periods)
        ibov = (
            returns.annualize_growth(
                self._ibov_level / self._ibov_base - 1
                if self._ibov_level
                else Decimal(0),
                self._periods,
            )
            if self._ibov_base
            else None
        )
        variance = max(
            (self._squares - self._sum * self._sum / n) / (n - 1), Decimal(0)
        )
        volatility = variance.sqrt() * risk.DAYS_PER_YEAR.sqrt()
        mean_excess = self._excess / n
        downside = (self._downside / n).sqrt() * risk.DAYS_PER_YEAR.sqrt()

        # O mês corrente entra como na amostra: composto até o último dia visto
        month_value, month_cdi = self._month_value - 1, self._month_cdi - 1
        months = self._months + 1
        worst = (
            month_value
            if self._worst_month is None
            else min(self._worst_month, month_value)
        )
        above_cdi = self._months_above_cdi + (month_value > month_cdi)
        positive = self._positive_months + (month_value > 0)

        return build_score(
            {
                "return_over_cdi": _excess(annual, cdi),
                "return_over_ibov": _excess(annual, ibov),
                "max_drawdown": self._max_drawdown,
                "annual_volatility": volatility,
                "time_underwater": Decimal(self._longest_underwater),
                "worst_month": worst,
                "months_above_cdi": Decimal(above_cdi) / months,
                "positive_months": Decimal(positive) / months,
                "sharpe_ratio": mean_excess * risk.DAYS_PER_YEAR / volatility
                if volatility
                else None,
                "sortino_ratio": mean_excess * risk.DAYS_PER_YEAR / downside
                if downside
                else None,
            }
        )

    def _close_month(self) -> None:
        if self._month is None:
            return
        value, cdi = self._month_value - 1, self._month_cdi - 1
        self._worst_month = (
            value if self._worst_month is None else min(self._worst_month, value)
        )
        self._months += 1
        self._months_above_cdi += value > cdi
        self._positive_months += value > 0


def player_score(history: list[PatrimonialHistoryDTO]) -> ScoreDTO | None:
    """Nota de um jogador sobre os snapshots dele; None com menos de 63 retornos."""
    if not history:
        return None
    walk = _ScoreWalk(history[0])
    for snapshot in history[1:]:
        walk.add(snapshot)
    return walk.score()


def score_history(history: list[PatrimonialHistoryDTO]) -> list[SeriesPointDTO]:
    """
    A nota total no último snapshot de cada mês, calculada só com os snapshots até
    ele; o último ponto é o último snapshot, então é a nota de `player_score` hoje.
    Os meses antes de 63 retornos ficam de fora.
    """
    if not history:
        return []
    walk = _ScoreWalk(history[0])
    last = len(history) - 1
    points = []
    for i, h in enumerate(history):
        if i > 0:
            walk.add(h)
        day = h.snapshot_date
        if i < last and (day.year, day.month) == (
            history[i + 1].snapshot_date.year,
            history[i + 1].snapshot_date.month,
        ):
            continue
        score = walk.score()
        if score is not None:
            points.append(SeriesPointDTO(date=day, value=score.total))
    return points


def _points(band: Band, value: Decimal | None) -> Decimal | None:
    return None if value is None else band.points(value)


def _excess(value: Decimal | None, reference: Decimal | None) -> Decimal | None:
    return None if value is None or reference is None else value - reference
