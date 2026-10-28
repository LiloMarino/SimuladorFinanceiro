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
from backend.core.enum import (
    SignalLineStyle,
    SignalPane,
    StrategyGroup,
    StrategyParamKind,
    StrategyView,
)
from backend.features.strategy.base_strategy import (
    CHART_DAYS,
    BaseStrategy,
    ParamSpec,
    Signal,
    param_int,
    param_tickers,
)
from backend.features.strategy.context import StrategyContext
from backend.features.technical_analysis import indicators


class VolumeBreakout(BaseStrategy):
    """
    Compra o ativo que ainda não tem quando o fechamento passa a máxima dos últimos
    pregões com volume acima da média, e vende a parte livre quando o fechamento
    fica abaixo da mínima dos pregões de saída. A ordem é a mercado.
    """

    key = "volume_breakout"
    name = "Rompimento com volume"
    bot_names = ("Rompedor", "Estouro", "Volume Alto")
    summary = "Compra quando o preço passa a máxima recente com volume."
    description = (
        "Compra quando o fechamento passa a máxima dos últimos pregões e o volume do "
        "dia está bem acima da média; vende quando o fechamento cai abaixo da mínima "
        "dos últimos pregões de saída."
    )
    group = StrategyGroup.TACTIC
    view_kind = StrategyView.SIGNAL
    term_hint = (
        "Rompimento é o preço passar a maior cotação de um período. Volume é quantas "
        "ações trocaram de mão no dia: se rompe com o dobro do volume de sempre, mais "
        "gente apostou na alta, e o movimento tende a durar mais. Ex.: máxima de 20 "
        "dias a R$ 30 e fechamento a R$ 31 com volume 150% da média: compra."
    )
    params = (
        ParamSpec(
            key="high_window",
            label="Máxima de",
            kind=StrategyParamKind.INT,
            default=20,
            min=5,
            max=100,
            unit="dias",
            hint=(
                "A máxima dos últimos pregões, sem contar hoje, que o fechamento "
                "precisa passar para comprar. Quanto maior a janela, mais raro e mais "
                "forte o rompimento."
            ),
        ),
        ParamSpec(
            key="volume_pct",
            label="Volume mínimo",
            kind=StrategyParamKind.INT,
            default=150,
            min=100,
            max=500,
            unit="%",
            hint=(
                "Volume do dia, em % da média do mesmo período da máxima. Com 150%, "
                "o dia precisa negociar 1,5 vez o volume de sempre para o rompimento "
                "valer."
            ),
        ),
        ParamSpec(
            key="exit_window",
            label="Mínima de saída",
            kind=StrategyParamKind.INT,
            default=10,
            min=5,
            max=50,
            unit="dias",
            hint=(
                "A mínima dos últimos pregões, sem contar hoje: o fechamento abaixo "
                "dela vende a posição. Janela menor sai mais cedo (e mais vezes por "
                "engano)."
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
    def needed_days(cls, params: dict[str, StrategyParamValue]) -> int:
        # A janela mais longa e o dia de hoje
        return (
            max(param_int(params, "high_window"), param_int(params, "exit_window")) + 1
        )

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        high_window, exit_window, volume_pct = _settings(params)
        percent = Decimal(param_int(params, "cash_pct"))
        needed = self.needed_days(params)

        # Cada compra parte do caixa que sobrou das anteriores do dia
        cash = ctx.cash
        for ticker in param_tickers(params, "tickers"):
            frame = ctx.history(ticker, needed)
            quote = ctx.quotes.get(ticker)
            if len(frame) < needed or quote is None:
                continue

            _, _, broke_out, broke_down = _channel(
                frame, high_window, exit_window, volume_pct
            )
            holding = ctx.holdings.get(ticker)
            if broke_out.iloc[-1] and not holding:
                price = Decimal(str(quote.close))
                quantity = ctx.affordable(ticker, cash * percent / 100)
                if quantity > 0:
                    ctx.buy(
                        ticker,
                        quantity,
                        f"Fechou acima da máxima de {high_window} dias com volume "
                        f"acima de {volume_pct}% da média",
                    )
                    cash -= price * quantity
            elif broke_down.iloc[-1] and holding:
                free = holding.size - holding.reserved
                if free > 0:
                    ctx.sell(
                        ticker,
                        free,
                        f"Fechou abaixo da mínima de {exit_window} dias",
                    )

    def signal(
        self, history: pd.DataFrame, params: dict[str, StrategyParamValue]
    ) -> Signal | None:
        high_window, exit_window, volume_pct = _settings(params)
        if len(history) < self.needed_days(params):
            return None

        upper, lower, broke_out, broke_down = _channel(
            history, high_window, exit_window, volume_pct
        )
        shown = slice(-CHART_DAYS, None)

        def line(
            key: str, label: str, style: SignalLineStyle, series: pd.Series
        ) -> SignalLineDTO:
            window = series.iloc[shown].dropna()
            return SignalLineDTO(
                key=key,
                label=label,
                style=style,
                pane=SignalPane.PRICE,
                points=[
                    SignalPointDTO(date=day.date(), value=round(float(value), 2))
                    for day, value in window.items()
                ],
            )

        # Um marcador por rompimento: o primeiro dia de cada sequência
        first_out = _first_days(broke_out).iloc[shown]
        first_down = _first_days(broke_down).iloc[shown]
        markers = [
            SignalMarkerDTO(date=day.date(), side="buy")
            for day in first_out.index[first_out]
        ] + [
            SignalMarkerDTO(date=day.date(), side="sell")
            for day in first_down.index[first_down]
        ]
        return Signal(
            lines=[
                line("price", "Preço", SignalLineStyle.PRICE, _col(history, "close")),
                line(
                    "upper",
                    f"Máxima de {high_window} dias",
                    SignalLineStyle.CHANNEL,
                    upper,
                ),
                line(
                    "lower",
                    f"Mínima de {exit_window} dias",
                    SignalLineStyle.CHANNEL,
                    lower,
                ),
            ],
            markers=sorted(markers, key=lambda m: m.date),
        )


def _col(frame: pd.DataFrame, name: str) -> pd.Series:
    return cast(pd.Series, frame[name])


def _settings(params: dict[str, StrategyParamValue]) -> tuple[int, int, int]:
    return (
        param_int(params, "high_window"),
        param_int(params, "exit_window"),
        param_int(params, "volume_pct"),
    )


def _first_days(condition: pd.Series) -> pd.Series:
    """Só o primeiro dia de cada sequência de dias em que a condição vale."""
    return condition & ~condition.shift(1, fill_value=False).astype(bool)


def _channel(
    frame: pd.DataFrame, high_window: int, exit_window: int, volume_pct: int
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    A máxima e a mínima dos pregões anteriores a cada dia, e os dias em que o
    fechamento rompeu a máxima com volume e em que caiu abaixo da mínima.
    """
    close = _col(frame, "close")
    upper = cast(pd.Series, _col(frame, "high").rolling(high_window).max().shift(1))
    lower = cast(pd.Series, _col(frame, "low").rolling(exit_window).min().shift(1))
    volume = _col(frame, "volume")
    average_volume = indicators.sma(volume, high_window).shift(1)
    broke_out = (close > upper) & (volume * 100 > average_volume * volume_pct)
    broke_down = close < lower
    return upper, lower, broke_out, broke_down
