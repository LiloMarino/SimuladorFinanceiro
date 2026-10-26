"""
Nota geral de desempenho (D10): quatro eixos de peso igual, cada um a média das
suas métricas, e cada métrica convertida em pontos por faixas fixas, iguais em
toda partida, para que a nota compare partidas diferentes.
"""

from collections.abc import Mapping, MutableMapping
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


def player_score(history: list[PatrimonialHistoryDTO]) -> ScoreDTO | None:
    """Nota de um jogador sobre os snapshots dele; None com menos de 63 retornos."""
    days = risk.daily_returns(history)
    if len(days) < MIN_SCORE_DAYS:
        return None

    dates = [h.snapshot_date for h in history]
    annual = risk.annual_return(days)
    cdi = returns.annualize(returns.cdi_cumulative(dates))
    ibov = returns.annualize(returns.ibov_cumulative(dates))
    volatility = risk.annual_volatility([r for _, r in days])
    months = risk.monthly_returns(days)

    return build_score(
        {
            "return_over_cdi": _excess(annual, cdi),
            "return_over_ibov": _excess(annual, ibov),
            "max_drawdown": risk.max_drawdown(days),
            "annual_volatility": volatility,
            "time_underwater": _decimal(risk.time_underwater(days)),
            "worst_month": min((m.value for m in months), default=None),
            "months_above_cdi": _share(
                sum(1 for m in months if m.value > m.cdi), months
            ),
            "positive_months": _share(sum(1 for m in months if m.value > 0), months),
            "sharpe_ratio": risk.sharpe_ratio(days, volatility),
            "sortino_ratio": risk.sortino_ratio(days),
        }
    )


def score_history(
    history: list[PatrimonialHistoryDTO],
    closed: MutableMapping[date, Decimal | None] | None = None,
) -> list[SeriesPointDTO]:
    """
    A nota total no último snapshot de cada mês, calculada só com os snapshots até
    ele; o último ponto é o último snapshot, então é a nota de `player_score` hoje.
    Os meses antes de 63 retornos ficam de fora.

    `closed` guarda a nota de cada mês que já acabou (todo corte menos o último):
    ela só depende dos snapshots até o corte, então quem passa o mesmo `closed` a
    cada virada calcula só o mês novo e o dia de hoje.
    """
    memo: MutableMapping[date, Decimal | None] = {} if closed is None else closed
    last = len(history) - 1
    points = []
    for i, h in enumerate(history):
        day = h.snapshot_date
        if i < last and (day.year, day.month) == (
            history[i + 1].snapshot_date.year,
            history[i + 1].snapshot_date.month,
        ):
            continue
        if i < last and day in memo:
            total = memo[day]
        else:
            score = player_score(history[: i + 1])
            total = score.total if score else None
            if i < last:
                memo[day] = total
        if total is not None:
            points.append(SeriesPointDTO(date=day, value=total))
    return points


def _points(band: Band, value: Decimal | None) -> Decimal | None:
    return None if value is None else band.points(value)


def _excess(value: Decimal | None, reference: Decimal | None) -> Decimal | None:
    return None if value is None or reference is None else value - reference


def _share(count: int, months: list[risk.MonthlyReturn]) -> Decimal | None:
    return Decimal(count) / len(months) if months else None


def _decimal(value: int | None) -> Decimal | None:
    return None if value is None else Decimal(value)
