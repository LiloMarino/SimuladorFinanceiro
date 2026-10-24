from __future__ import annotations

from decimal import Decimal
from typing import cast

import pandas as pd

from backend.core.dto.strategy import (
    SignalLevelDTO,
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


class RelativeStrength(BaseStrategy):
    """
    Compra no dia em que o IFR cruza para baixo do nível de compra (o preço caiu
    rápido demais) e vende a parte livre do ativo no dia em que cruza para cima do
    nível de venda. A ordem é a mercado e o ativo sem histórico suficiente fica sem sinal.
    """

    key = "rsi"
    name = "IFR (RSI)"
    bot_names = ("Pé no Freio", "Sobrevendido", "Sr. IFR")
    summary = "Compra quando o preço caiu rápido demais."
    description = (
        "Compra no dia em que o IFR cai abaixo do nível de compra, e vende o que tem "
        "daquele ativo no dia em que ele sobe acima do nível de venda."
    )
    group = StrategyGroup.TACTIC
    view_kind = StrategyView.SIGNAL
    term_hint = (
        "IFR (Índice de Força Relativa) mede de 0 a 100 quanto das variações recentes "
        "foi de alta. Perto de 0, o preço caiu rápido demais e pode reagir; perto de "
        "100, subiu rápido demais. Ex.: IFR de 25 é queda forte (compra); de 75, "
        "alta forte (venda)."
    )
    params = (
        ParamSpec(
            key="period",
            label="Período",
            kind=StrategyParamKind.INT,
            default=14,
            min=2,
            max=50,
            unit="dias",
            hint=(
                "Quantos pregões o IFR olha para trás. Com 14 dias, ele reage a "
                "movimentos de duas semanas. Quanto menor, mais oscila (e mais sinais "
                "falsos)."
            ),
        ),
        ParamSpec(
            key="buy_below",
            label="Comprar abaixo de",
            kind=StrategyParamKind.INT,
            default=30,
            min=5,
            max=50,
            hint=(
                "Nível do IFR que dispara a compra, no dia em que ele cruza para "
                "baixo. Com 30, compra quando o preço caiu rápido demais. Quanto menor, "
                "mais raro e mais extremo o sinal."
            ),
        ),
        ParamSpec(
            key="sell_above",
            label="Vender acima de",
            kind=StrategyParamKind.INT,
            default=70,
            min=50,
            max=95,
            hint=(
                "Nível do IFR que dispara a venda, no dia em que ele cruza para cima. "
                "Precisa ser maior que o de compra. Com 70, vende quando o preço subiu "
                "rápido demais."
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
        buy, sell = params.get("buy_below"), params.get("sell_above")
        if (
            "buy_below" not in errors
            and "sell_above" not in errors
            and isinstance(buy, int)
            and isinstance(sell, int)
            and sell <= buy
        ):
            errors["sell_above"] = "O nível de venda precisa ser maior que o de compra."
        return errors

    @classmethod
    def needed_days(cls, params: dict[str, StrategyParamValue]) -> int:
        # O IFR de hoje e o de ontem
        return param_int(params, "period") + 2

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        period = param_int(params, "period")
        buy_below, sell_above = _levels(params)
        percent = Decimal(param_int(params, "cash_pct"))
        needed = self.needed_days(params)

        # Cada compra parte do caixa que sobrou das anteriores do dia
        cash = ctx.cash
        for ticker in param_tickers(params, "tickers"):
            frame = ctx.history(ticker, needed + CHART_DAYS)
            quote = ctx.quotes.get(ticker)
            if len(frame) < needed or quote is None:
                continue

            _, dipped, rallied = _crossings(
                _close(frame), period, buy_below, sell_above
            )
            if dipped.iloc[-1]:
                price = Decimal(str(quote.close))
                quantity = int(cash * percent / 100 // price)
                if quantity > 0:
                    ctx.buy(ticker, quantity, f"O IFR caiu abaixo de {buy_below}")
                    cash -= price * quantity
            elif rallied.iloc[-1]:
                holding = ctx.holdings.get(ticker)
                free = holding.size - holding.reserved if holding else 0
                if free > 0:
                    ctx.sell(ticker, free, f"O IFR subiu acima de {sell_above}")

    def signal(
        self, history: pd.DataFrame, params: dict[str, StrategyParamValue]
    ) -> Signal | None:
        period = param_int(params, "period")
        buy_below, sell_above = _levels(params)
        if len(history) < self.needed_days(params):
            return None

        close = _close(history)
        rsi, dipped, rallied = _crossings(close, period, buy_below, sell_above)
        shown = slice(-CHART_DAYS, None)

        def line(
            key: str,
            label: str,
            style: SignalLineStyle,
            pane: SignalPane,
            series: pd.Series,
        ) -> SignalLineDTO:
            window = series.iloc[shown].dropna()
            return SignalLineDTO(
                key=key,
                label=label,
                style=style,
                pane=pane,
                points=[
                    SignalPointDTO(date=day.date(), value=round(float(value), 2))
                    for day, value in window.items()
                ],
            )

        markers = [
            SignalMarkerDTO(date=day.date(), side="buy")
            for day in dipped.iloc[shown].index[dipped.iloc[shown]]
        ] + [
            SignalMarkerDTO(date=day.date(), side="sell")
            for day in rallied.iloc[shown].index[rallied.iloc[shown]]
        ]
        return Signal(
            lines=[
                line("price", "Preço", SignalLineStyle.PRICE, SignalPane.PRICE, close),
                line(
                    "rsi",
                    f"IFR de {period} dias",
                    SignalLineStyle.OSCILLATOR,
                    SignalPane.OSCILLATOR,
                    rsi,
                ),
            ],
            markers=sorted(markers, key=lambda m: m.date),
            levels=[
                SignalLevelDTO(value=buy_below, label=f"Compra {buy_below}"),
                SignalLevelDTO(value=sell_above, label=f"Venda {sell_above}"),
            ],
        )


def _close(frame: pd.DataFrame) -> pd.Series:
    return cast(pd.Series, frame["close"])


def _levels(params: dict[str, StrategyParamValue]) -> tuple[int, int]:
    return param_int(params, "buy_below"), param_int(params, "sell_above")


def _crossings(
    close: pd.Series, period: int, buy_below: int, sell_above: int
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """O IFR e os dias em que ele cruzou o nível de compra para baixo e o de venda para cima."""
    rsi = indicators.rsi(close, period)
    before = rsi.shift(1)
    dipped = (before >= buy_below) & (rsi < buy_below)
    rallied = (before <= sell_above) & (rsi > sell_above)
    return rsi, dipped, rallied
