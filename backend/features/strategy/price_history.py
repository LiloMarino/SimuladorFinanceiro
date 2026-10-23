from __future__ import annotations

from datetime import date

import pandas as pd

from backend.core import repository
from backend.features.variable_income.price_impact import PriceImpact

PRICE_COLUMNS = ["open", "high", "low", "close"]


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
        self._frames: dict[str, pd.DataFrame] = {}

    def window(self, ticker: str, today: date, days: int) -> pd.DataFrame:
        """Os últimos `days` pregões do ativo até `today`, do mais antigo ao mais novo."""
        frame = self._frame(ticker)
        end = int((frame.index <= pd.Timestamp(today)).sum())
        window = frame.iloc[max(0, end - days) : end]
        if not self._price_impact.enabled or window.empty:
            return window
        factors = self._price_impact.factors_on(
            ticker, [day.date() for day in window.index]
        )
        scaled = window.copy()
        scaled[PRICE_COLUMNS] = (
            window[PRICE_COLUMNS]
            .mul(pd.Series(list(factors.values()), index=window.index), axis=0)
            .round(2)
        )
        return scaled

    def _frame(self, ticker: str) -> pd.DataFrame:
        if ticker not in self._frames:
            self._frames.update(
                repository.stock.get_price_frame(
                    [ticker], self._end_date, self._simulation_id
                )
            )
        return self._frames[ticker]
