"""
O noticiário da partida: a cada pregão lê as séries que o jogo já tem e, quando uma regra
dispara, entrega a manchete ao jornal. Sem LLM e sem internet; a mesma lista de regras
vale para o futuro gerado e para a história real.
"""

from collections.abc import Callable, Sequence
from datetime import date
from functools import cached_property

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import DataOrigin, IndicatorSeries
from backend.core.utils import subtract_business_days
from backend.features.newsroom.companies import YEAR_SESSIONS, strong_moves, week_highs
from backend.features.newsroom.history import historical_milestones
from backend.features.newsroom.macro import (
    IbovespaExtremes,
    copom_decision,
    monthly_inflation,
)
from backend.features.newsroom.market import MarketDay, Quote, no_spending
from backend.features.notifications.news import Headline

type Rule = Callable[[MarketDay], list[Headline]]


class Newsroom:
    """
    Guarda os fechamentos dos últimos 52 semanas de cada ativo e passa cada pregão pela
    lista de regras. Regra nova é só mais um item de `self._rules`.
    """

    def __init__(
        self,
        simulation_id: int,
        classification: Callable[[], dict[str, StockSegmentDTO]],
        publish: Callable[[date, Headline], None],
        spending_inflation: Callable[[date], float] = no_spending,
    ) -> None:
        self._simulation_id = simulation_id
        self._classification = classification
        self._publish = publish
        self._spending_inflation = spending_inflation
        # Da mais importante para a menos: é a ordem em que as manchetes saem num pregão
        self._rules: tuple[Rule, ...] = (
            copom_decision,
            monthly_inflation,
            IbovespaExtremes(),
            strong_moves,
            week_highs,
            historical_milestones,
        )
        self._closes: dict[str, list[float]] | None = None

    def on_tick(self, day: date, candles: Sequence[CandleDTO]) -> None:
        """O pregão de `day`: roda as regras e só depois soma os fechamentos de hoje à janela."""
        previous = subtract_business_days(day, 1)
        closes = self._window(previous)
        market = self._market(day, previous, candles, closes)
        for rule in self._rules:
            for headline in rule(market):
                self._publish(day, headline)
        self._append(day, candles)

    def _market(
        self,
        day: date,
        previous: date,
        candles: Sequence[CandleDTO],
        closes: dict[str, list[float]],
    ) -> MarketDay:
        classification = self._classification()
        quotes = [
            Quote(
                candle.ticker,
                candle.name,
                candle.asset_class,
                segment.sector
                if (segment := classification.get(candle.ticker))
                else None,
                candle.close,
            )
            for candle in candles
            if candle.price_date == day
        ]
        economic = repository.economic
        return MarketDay(
            day=day,
            previous=previous,
            quotes=quotes,
            closes=closes,
            selic=economic.get_history(IndicatorSeries.SELIC),
            ipca=economic.get_history(IndicatorSeries.IPCA),
            ibov=economic.get_history(IndicatorSeries.IBOV),
            real_until=self._real_end,
            simulation_id=self._simulation_id,
            spending_inflation=self._spending_inflation,
        )

    def _window(self, previous: date) -> dict[str, list[float]]:
        """Os fechamentos até o pregão anterior; na primeira vez nascem do histórico gravado."""
        if self._closes is None:
            recent = repository.stock.get_recent_closes(
                previous, YEAR_SESSIONS, self._simulation_id
            )
            self._closes = {
                ticker: values[-YEAR_SESSIONS:] for ticker, values in recent.items()
            }
        return self._closes

    def _append(self, day: date, candles: Sequence[CandleDTO]) -> None:
        """Soma o fechamento de cada ativo que negociou hoje à janela de 52 semanas."""
        if self._closes is None:
            return
        for candle in candles:
            if candle.price_date != day:
                continue
            window = self._closes.setdefault(candle.ticker, [])
            window.append(candle.close)
            del window[:-YEAR_SESSIONS]

    @cached_property
    def _real_end(self) -> date | None:
        """O último dia com dado real do Ibovespa, lido uma vez; nulo sem dado real."""
        real = [
            c.end
            for c in repository.economic.get_coverage()
            if c.key == IndicatorSeries.IBOV.value and c.origin is DataOrigin.REAL
        ]
        return max(real, default=None)
