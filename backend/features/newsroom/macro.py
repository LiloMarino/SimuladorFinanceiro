"""As manchetes da economia: Copom, inflação do mês e os extremos do Ibovespa."""

import itertools
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import NewsType
from backend.core.indicators import annualize_daily
from backend.features.economy.panel import MIN_COPOM_STEP
from backend.features.newsroom.market import MarketDay
from backend.features.newsroom.text import MONTH_NAMES, grouped, number, pick
from backend.features.notifications.news import Headline

# Queda diária do Ibovespa abaixo da qual ainda não é "a maior queda do ano"
MIN_DROP = 0.02
# O recorde só volta à manchete depois de tantos dias, para uma alta seguida não repetir o aviso
RECORD_COOLDOWN = timedelta(days=30)
IPCA_WINDOW_MONTHS = 12
# A diferença mínima, em pontos de inflação em 12 meses, para a manchete citar as medidas de gasto
MIN_SPENDING_GAP = Decimal("0.05")


def copom_decision(market: MarketDay) -> list[Headline]:
    """O Copom mexeu na SELIC: o nível anual de hoje contra o do pregão anterior."""
    today = market.selic.last_known(market.day)
    before = market.selic.last_known(market.previous)
    if today is None or before is None:
        return []
    level, previous_level = annualize_daily(today), annualize_daily(before)
    step = level - previous_level
    if abs(step) < MIN_COPOM_STEP:
        return []

    points = abs(step) * 100
    unit = "ponto" if points < 2 else "pontos"
    verb = pick(
        ("sobe", "eleva") if step > 0 else ("baixa", "corta"),
        market.simulation_id,
        market.day,
        NewsType.COPOM_DECISION,
    )
    return [
        Headline(
            NewsType.COPOM_DECISION,
            f"Copom {verb} a SELIC em {number(points)} {unit}, para {number(level * 100)}%",
            f"A taxa básica passa de {number(previous_level * 100)}% para "
            f"{number(level * 100)}% ao ano.",
        )
    ]


def monthly_inflation(market: MarketDay) -> list[Headline]:
    """No primeiro pregão do mês, o IPCA do mês que fechou contra o anterior."""
    if market.day.month == market.previous.month:
        return []
    closed = market.previous.replace(day=1)
    before = (closed - timedelta(days=1)).replace(day=1)
    value, prior = market.ipca.value_on(closed), market.ipca.value_on(before)
    if value is None:
        return []

    month, prior_month = MONTH_NAMES[closed.month - 1], MONTH_NAMES[before.month - 1]
    seed = (market.simulation_id, market.day, NewsType.MONTHLY_INFLATION)
    shown = number(value)
    if prior is None or value == prior:
        text = f"IPCA de {month} fica em {shown}%"
    elif value > prior:
        text = pick(
            (
                f"IPCA de {month} acelera e fica em {shown}%",
                f"IPCA de {month} sobe para {shown}%",
            ),
            *seed,
        )
    else:
        text = pick(
            (
                f"IPCA de {month} desacelera e fica em {shown}%",
                f"IPCA de {month} cai para {shown}%",
            ),
            *seed,
        )

    parts = [] if prior is None else [f"Em {prior_month} tinha sido {number(prior)}%."]
    window = market.ipca.values_until(closed, IPCA_WINDOW_MONTHS)
    if len(window) == IPCA_WINDOW_MONTHS:
        accrued = _accumulated(window)
        parts.append(f"Em 12 meses, a inflação acumula {number(accrued)}%.")
        # Sem os pontos das medidas de gasto, o mesmo ano teria fechado em outro número
        days = [d for d in market.ipca.dates if d <= closed][-IPCA_WINDOW_MONTHS:]
        without = _accumulated(
            [
                monthly - Decimal(str(round(market.spending_inflation(day) / 12, 6)))
                for day, monthly in zip(days, window, strict=True)
            ]
        )
        if abs(accrued - without) >= MIN_SPENDING_GAP:
            parts.append(
                f"Sem as medidas de gasto, a inflação em 12 meses estaria em {number(without)}%."
            )
    return [Headline(NewsType.MONTHLY_INFLATION, text, " ".join(parts) or None)]


def _accumulated(monthly: list[Decimal]) -> Decimal:
    """A inflação acumulada, em %, de uma lista de IPCA mensais em %."""
    growth = Decimal(1)
    for value in monthly:
        growth *= 1 + value / 100
    return (growth - 1) * 100


class IbovespaExtremes:
    """
    Recorde e maior queda do ano do Ibovespa. Guarda a máxima de todos os tempos, o pior
    dia de cada ano e o último recorde noticiado; o estado nasce das séries na primeira
    leitura e anda um pregão por vez.
    """

    def __init__(self) -> None:
        self._peak: Decimal | None = None
        self._worst: dict[int, float] = {}
        self._last_record: date | None = None

    def __call__(self, market: MarketDay) -> list[Headline]:
        history = market.ibov
        level = history.value_on(market.day)
        before = history.last_known(market.previous)
        if level is None or before is None or before == 0:
            return []
        if self._peak is None:
            self._start(market)

        change = float(level / before - 1)
        headlines: list[Headline] = []
        year_worst = self._worst.get(market.day.year)
        if change <= -MIN_DROP and (year_worst is None or change < year_worst):
            headlines.append(
                Headline(
                    NewsType.IBOVESPA_EXTREME,
                    f"Ibovespa tem a maior queda do ano: \N{MINUS SIGN}{number(-change * 100, 1)}%",
                    f"O índice fecha em {grouped(level)} pontos.",
                )
            )
        elif (
            self._peak is not None
            and level > self._peak
            and self._record_is_news(market.day)
        ):
            self._last_record = market.day
            headlines.append(
                Headline(
                    NewsType.IBOVESPA_EXTREME,
                    f"Ibovespa fecha no recorde: {grouped(level)} pontos",
                    f"Alta de {number(change * 100, 1)}% no dia.",
                )
            )

        if year_worst is None or change < year_worst:
            self._worst[market.day.year] = change
        if self._peak is not None and level > self._peak:
            self._peak = level
        return headlines

    def _record_is_news(self, day: date) -> bool:
        return self._last_record is None or day - self._last_record >= RECORD_COOLDOWN

    def _start(self, market: MarketDay) -> None:
        """A máxima e o pior dia do ano até o pregão anterior, lidos da série."""
        history = market.ibov
        dates = [d for d in history.dates if d <= market.previous]
        self._peak = max((history.values[d] for d in dates), default=Decimal(0))
        year = market.day.year
        in_year = [d for d in dates if d.year == year]
        for earlier, current in itertools.pairwise(in_year):
            base = history.values[earlier]
            if base:
                change = float(history.values[current] / base - 1)
                if year not in self._worst or change < self._worst[year]:
                    self._worst[year] = change
