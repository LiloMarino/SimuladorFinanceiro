from __future__ import annotations

from decimal import Decimal
from typing import cast

import pandas as pd

from backend.core.dto.strategy import (
    SignalLineDTO,
    SignalMarkerDTO,
    SignalPointDTO,
    StrategyParamValue,
)
from backend.core.enum import StrategyGroup, StrategyParamKind
from backend.features.strategy.base_strategy import BaseStrategy, ParamSpec, Signal
from backend.features.strategy.context import StrategyContext

# Pregões desenhados no gráfico do sinal (cerca de um ano)
CHART_DAYS = 252


class MovingAverageCross(BaseStrategy):
    """
    Compra quando a média curta cruza a longa para cima e vende tudo do ativo
    quando cruza para baixo. A ordem é a mercado e o ativo sem histórico
    suficiente fica sem sinal.
    """

    key = "moving_average_cross"
    name = "Cruzamento de médias 50/200"
    summary = "Compra quando a média curta passa a longa."
    description = (
        "Compra quando a média curta passa a longa para cima; vende tudo daquele "
        "ativo quando cruza para baixo."
    )
    group = StrategyGroup.TACTIC
    params = (
        ParamSpec(
            key="short_window",
            label="Média curta",
            kind=StrategyParamKind.INT,
            default=50,
            min=5,
            max=100,
            unit="dias",
            hint=(
                "Média dos preços de fechamento dos últimos dias. Com 50 dias, ela "
                "reage rápido: acompanha o preço de perto. Quanto menor, mais sinais "
                "(e mais falsos)."
            ),
        ),
        ParamSpec(
            key="long_window",
            label="Média longa",
            kind=StrategyParamKind.INT,
            default=200,
            min=50,
            max=400,
            unit="dias",
            hint=(
                "Média de mais dias, que mostra a tendência de fundo. Precisa ser "
                "maior que a curta. Quando a curta passa por cima dela, o preço "
                "começou a subir mais do que a tendência."
            ),
        ),
        ParamSpec(
            key="cash_pct",
            label="Quanto do caixa por compra",
            kind=StrategyParamKind.PERCENT,
            default=20,
            min=5,
            max=100,
            unit="%",
            hint=(
                "Parte do caixa disponível que cada compra usa. Com R$ 10.000 e 20%, "
                "cada compra gasta até R$ 2.000."
            ),
        ),
        ParamSpec(
            key="tickers",
            label="Ações que ela opera",
            kind=StrategyParamKind.TICKERS,
            hint=(
                "A estratégia só compra e vende estas ações. O padrão são as 10 mais "
                "negociadas da partida: as de maior volume financeiro médio nos "
                "últimos 60 pregões, calculado ao ligar."
            ),
        ),
    )

    @classmethod
    def validate(
        cls, params: dict[str, StrategyParamValue], known_tickers: set[str]
    ) -> dict[str, str]:
        errors = super().validate(params, known_tickers)
        short, long_ = params.get("short_window"), params.get("long_window")
        if (
            "short_window" not in errors
            and "long_window" not in errors
            and isinstance(short, int)
            and isinstance(long_, int)
            and long_ <= short
        ):
            errors["long_window"] = "A média longa precisa ser maior que a curta."
        return errors

    @classmethod
    def needed_days(cls, params: dict[str, StrategyParamValue]) -> int:
        # A média longa de hoje e a de ontem
        return _windows(params)[1] + 1

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        short, long_ = _windows(params)
        percent = Decimal(_int(params, "cash_pct"))
        tickers = params["tickers"]
        assert isinstance(tickers, list)

        # Cada compra parte do caixa que sobrou das anteriores do dia
        cash = ctx.cash
        for ticker in tickers:
            frame = ctx.history(ticker, long_ + 1)
            quote = ctx.quotes.get(ticker)
            if len(frame) < long_ + 1 or quote is None:
                continue

            _, _, up, down = _crossings(_close(frame), short, long_)
            if up.iloc[-1]:
                price = Decimal(str(quote.close))
                quantity = int(cash * percent / 100 // price)
                if quantity > 0:
                    ctx.buy(
                        ticker,
                        quantity,
                        f"A média de {short} dias cruzou a de {long_} para cima",
                    )
                    cash -= price * quantity
            elif down.iloc[-1]:
                holding = ctx.holdings.get(ticker)
                free = holding.size - holding.reserved if holding else 0
                if free > 0:
                    ctx.sell(
                        ticker,
                        free,
                        f"A média de {short} dias cruzou a de {long_} para baixo",
                    )

    def signal(
        self, history: pd.DataFrame, params: dict[str, StrategyParamValue]
    ) -> Signal | None:
        short, long_ = _windows(params)
        if len(history) < long_ + 1:
            return None

        close = _close(history)
        short_avg, long_avg, up, down = _crossings(close, short, long_)
        shown = slice(-CHART_DAYS, None)

        def line(key: str, label: str, series: pd.Series) -> SignalLineDTO:
            window = series.iloc[shown].dropna()
            return SignalLineDTO(
                key=key,  # type: ignore[arg-type]
                label=label,
                points=[
                    SignalPointDTO(date=day.date(), value=round(float(value), 2))
                    for day, value in window.items()
                ],
            )

        markers = [
            SignalMarkerDTO(date=day.date(), side="buy")
            for day in up.iloc[shown].index[up.iloc[shown]]
        ] + [
            SignalMarkerDTO(date=day.date(), side="sell")
            for day in down.iloc[shown].index[down.iloc[shown]]
        ]
        return Signal(
            lines=[
                line("price", "Preço", close),
                line("short", f"Média de {short} dias", short_avg),
                line("long", f"Média de {long_} dias", long_avg),
            ],
            markers=sorted(markers, key=lambda m: m.date),
        )


def _close(frame: pd.DataFrame) -> pd.Series:
    return cast(pd.Series, frame["close"])


def _int(params: dict[str, StrategyParamValue], key: str) -> int:
    value = params[key]
    assert isinstance(value, int)
    return value


def _windows(params: dict[str, StrategyParamValue]) -> tuple[int, int]:
    return _int(params, "short_window"), _int(params, "long_window")


def _crossings(
    close: pd.Series, short: int, long_: int
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """As duas médias e os dias em que a curta cruzou a longa para cima e para baixo."""
    short_avg = cast(pd.Series, close.rolling(short).mean())
    long_avg = cast(pd.Series, close.rolling(long_).mean())
    gap = cast(pd.Series, short_avg - long_avg)
    before = gap.shift(1)
    up = (before <= 0) & (gap > 0)
    down = (before >= 0) & (gap < 0)
    return short_avg, long_avg, up, down
