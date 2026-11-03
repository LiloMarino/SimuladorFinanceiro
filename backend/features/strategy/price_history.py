from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from backend.core import repository
from backend.features.variable_income.price_impact import PriceImpact

PRICE_COLUMNS = ["open", "high", "low", "close"]


@dataclass(frozen=True)
class _Series:
    """O histórico de um ativo em arrays, para fatiar uma janela sem passar pelo pandas."""

    index: pd.DatetimeIndex
    days: np.ndarray
    prices: np.ndarray
    volume: np.ndarray

    @classmethod
    def of(cls, frame: pd.DataFrame) -> _Series:
        index = pd.DatetimeIndex(frame.index)
        return cls(
            index=index,
            days=index.date,
            prices=frame[PRICE_COLUMNS].to_numpy(),
            volume=frame["volume"].to_numpy(),
        )


class PriceHistory:
    """
    Histórico de preços que a estratégia lê, igual ao que o jogador vê nos gráficos.

    Cada ativo é carregado do banco uma vez por partida; a janela devolvida termina
    no dia pedido (o banco guarda o futuro gerado) e leva o impacto das ordens dos
    jogadores nos preços, como as cotações do dia.
    """

    def __init__(
        self, simulation_id: int, end_date: date, price_impact: PriceImpact
    ) -> None:
        self._simulation_id = simulation_id
        self._end_date = end_date
        self._price_impact = price_impact
        self._series: dict[str, _Series] = {}

    def window(self, ticker: str, today: date, days: int) -> pd.DataFrame:
        """Os últimos `days` pregões do ativo até `today`, do mais antigo ao mais novo."""
        series = self._load(ticker)
        end = int(series.index.searchsorted(np.datetime64(today, "ns"), side="right"))
        start = max(0, end - days)
        factors = self._price_impact.factors_on(ticker, series.days[start:end].tolist())
        scaled = (
            series.prices[start:end]
            * np.fromiter(factors.values(), dtype=float, count=end - start)[:, None]
        ).round(2)
        columns = {name: scaled[:, i] for i, name in enumerate(PRICE_COLUMNS)}
        columns["volume"] = series.volume[start:end]
        return pd.DataFrame(columns, index=series.index[start:end])

    def _load(self, ticker: str) -> _Series:
        if ticker not in self._series:
            frames = repository.stock.get_price_frame(
                [ticker], self._end_date, self._simulation_id
            )
            self._series.update({t: _Series.of(f) for t, f in frames.items()})
        return self._series[ticker]
