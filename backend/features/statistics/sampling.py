"""
Quantos pontos os gráficos de série recebem. Em partida longa, um ponto por pregão
pesa na tela sem mostrar mais nada: a série passa a ter o fechamento de cada semana
ou de cada mês. As métricas saem sempre da série diária, antes de afinar.
"""

from collections.abc import Callable
from datetime import date
from itertools import pairwise
from typing import Literal

type ChartPeriod = Literal["day", "week", "month"]

# Até um ano, um ponto por pregão; até cinco anos, ~52 por ano; acima, 12 por ano
_DAILY_UP_TO_DAYS = 366
_WEEKLY_UP_TO_DAYS = 5 * 366


def chart_period(first: date, last: date) -> ChartPeriod:
    days = (last - first).days
    if days <= _DAILY_UP_TO_DAYS:
        return "day"
    if days <= _WEEKLY_UP_TO_DAYS:
        return "week"
    return "month"


def thin[T](items: list[T], day: Callable[[T], date], period: ChartPeriod) -> list[T]:
    """
    O primeiro item e o último de cada semana (ou mês) do calendário. Séries com as
    mesmas datas ficam com os mesmos pontos, então a média da equipe e a referência
    continuam alinhadas com os jogadores.
    """
    if period == "day" or len(items) < 2:
        return items
    key = _week if period == "week" else _month
    kept = [items[0]]
    for current, following in pairwise(items[1:]):
        if key(day(current)) != key(day(following)):
            kept.append(current)
    kept.append(items[-1])
    return kept


def _week(day: date) -> tuple[int, int]:
    year, week, _ = day.isocalendar()
    return year, week


def _month(day: date) -> tuple[int, int]:
    return day.year, day.month
