"""
A pergunta do desafio da vela: um recorte aleatório da base, de 30 velas, que termina
num padrão com lado, seguido das 5 velas que o desafio esconde até a revelação.

Os padrões são os mesmos que marcam o gráfico (`technical_analysis/patterns.py`), então
o padrão perguntado é o padrão que o gráfico da partida marcaria.
"""

from __future__ import annotations

import random
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol, cast

import pandas as pd

from backend.core import repository
from backend.core.dto.candle_challenge import CandleBarDTO, ChallengeOutcome
from backend.core.dto.candle_patterns import CandlePatternCode, PatternStatsDTO
from backend.core.enum import AssetClass
from backend.features.technical_analysis.patterns import (
    OUTCOME_SESSIONS,
    PATTERNS,
    Occurrence,
    build_candle_patterns,
    detect,
    outcome,
)
from backend.features.technical_analysis.summary import price_frame

# Velas que o jogador vê, contando a última do padrão
WINDOW = 30
# Quantos ativos a busca tenta antes de desistir de um lado
ATTEMPTS = 60
# Históricos mantidos em memória entre uma pergunta e outra
CACHED_FRAMES = 24


class NoQuestionError(Exception):
    """A base não tem nenhum recorte que sirva de pergunta."""


class Market(Protocol):
    """De onde saem os históricos: a base inteira, sem relógio de partida."""

    def tickers(self) -> list[str]: ...

    def frame(self, ticker: str) -> pd.DataFrame: ...


class DatabaseMarket:
    """Os pregões reais da série comum de cada ação, sem o impacto de preço de uma partida."""

    def __init__(self) -> None:
        self._stocks: dict[str, int] | None = None
        self._frames: OrderedDict[str, pd.DataFrame] = OrderedDict()

    def tickers(self) -> list[str]:
        return list(self._ids())

    def frame(self, ticker: str) -> pd.DataFrame:
        if ticker in self._frames:
            self._frames.move_to_end(ticker)
            return self._frames[ticker]
        frame = price_frame(repository.stock.get_real_history(self._ids()[ticker]))
        self._frames[ticker] = frame
        if len(self._frames) > CACHED_FRAMES:
            self._frames.popitem(last=False)
        return frame

    def _ids(self) -> dict[str, int]:
        if self._stocks is None:
            self._stocks = {
                s.ticker: s.id
                for s in repository.stock.get_stocks()
                if s.asset_class == AssetClass.STOCK
            }
        return self._stocks


@dataclass(frozen=True)
class Question:
    ticker: str
    pattern_code: CandlePatternCode
    bars: list[CandleBarDTO]
    bars_after: list[CandleBarDTO]
    start: date
    # Último pregão do padrão, que identifica a pergunta na rodada
    pattern_end: date
    end: date
    # Fechamento do padrão até o do 5º pregão depois, em fração
    change: float
    outcome: ChallengeOutcome

    @property
    def key(self) -> tuple[str, date]:
        return self.ticker, self.pattern_end


class QuestionSource:
    """Sorteia as perguntas, equilibrando padrões de alta e de baixa."""

    def __init__(
        self, market: Market | None = None, rng: random.Random | None = None
    ) -> None:
        self._market = market or DatabaseMarket()
        self._rng = rng or random.Random()
        self._stats: dict[CandlePatternCode, PatternStatsDTO] | None = None

    def draw(self, exclude: Sequence[tuple[str, date]] = ()) -> Question:
        """Uma pergunta nova, fora as que já saíram na rodada."""
        tickers = self._market.tickers()
        if not tickers:
            raise NoQuestionError("Sem ações na base")
        sides = ["up", "down"]
        self._rng.shuffle(sides)
        for side in sides:
            for ticker in self._rng.sample(tickers, min(ATTEMPTS, len(tickers))):
                if question := self._from(ticker, side, exclude):
                    return question
        raise NoQuestionError("Nenhum recorte da base termina num padrão com lado")

    def stats(self, code: CandlePatternCode) -> PatternStatsDTO:
        """Acertos do padrão na base inteira, calculados uma vez por processo."""
        if self._stats is None:
            checked = dict.fromkeys(PATTERNS, 0)
            hits = dict.fromkeys(PATTERNS, 0)
            for ticker in self._market.tickers():
                for stat in build_candle_patterns(self._market.frame(ticker)).stats:
                    checked[stat.code] += stat.checked
                    hits[stat.code] += stat.hits
            self._stats = {
                c: PatternStatsDTO(code=c, checked=checked[c], hits=hits[c])
                for c in PATTERNS
            }
        return self._stats[code]

    def _from(
        self, ticker: str, side: str, exclude: Sequence[tuple[str, date]]
    ) -> Question | None:
        frame = self._market.frame(ticker)
        fits = [
            o
            for o in detect(frame)
            if PATTERNS[o.code].direction == side
            and o.end_pos >= WINDOW - 1
            and o.end_pos + OUTCOME_SESSIONS < len(frame)
            and (ticker, o.end.date()) not in exclude
        ]
        if not fits:
            return None
        return _question(ticker, frame, self._rng.choice(fits))


def _question(ticker: str, frame: pd.DataFrame, occurrence: Occurrence) -> Question:
    end = occurrence.end_pos
    shown = frame.iloc[end - WINDOW + 1 : end + 1]
    after = frame.iloc[end + 1 : end + 1 + OUTCOME_SESSIONS]
    base = float(shown["open"].iloc[0])
    change = cast(float, outcome(frame, occurrence))
    return Question(
        ticker=ticker,
        pattern_code=occurrence.code,
        bars=_bars(shown, base),
        bars_after=_bars(after, base),
        start=cast(pd.Timestamp, shown.index[0]).date(),
        pattern_end=occurrence.end.date(),
        end=cast(pd.Timestamp, after.index[-1]).date(),
        change=change,
        outcome="void" if change == 0 else ("up" if change > 0 else "down"),
    )


def _bars(frame: pd.DataFrame, base: float) -> list[CandleBarDTO]:
    """As velas em % desde a abertura da primeira, arredondadas ao centésimo."""

    def pct(value: float) -> float:
        return round((float(value) / base - 1) * 100, 2)

    opens, highs, lows, closes = (
        frame[column].to_numpy(dtype=float)
        for column in ("open", "high", "low", "close")
    )
    return [
        CandleBarDTO(open=pct(o), high=pct(h), low=pct(low), close=pct(c))
        for o, h, low, c in zip(opens, highs, lows, closes, strict=True)
    ]
