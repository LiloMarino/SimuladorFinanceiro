from __future__ import annotations

from decimal import Decimal

import pandas as pd

from backend.core.dto.strategy import SignalLineDTO, SignalPointDTO, StrategyParamValue
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
    param_ticker,
)
from backend.features.strategy.context import StrategyContext

# ETF que reproduz o Ibovespa
DEFAULT_ASSET = "BOVA11"


class BuyAndHold(BaseStrategy):
    """
    Referência de renda variável: todo o caixa vira cotas inteiras de um único ativo,
    que nunca é vendido. O que sobra do arredondamento fica no caixa até o dia seguinte.
    """

    key = "buy_and_hold"
    name = "Comprar e segurar"
    summary = "Compra um ETF do Ibovespa e não vende mais."
    description = (
        "Põe o caixa em cotas de um ETF do Ibovespa, todo dia, e nunca vende. "
        "É a régua da renda variável: acompanha o mercado sem tentar ganhar dele."
    )
    group = StrategyGroup.REFERENCE
    view_kind = StrategyView.SIGNAL
    term_hint = (
        "ETF é um fundo que reproduz um índice e é negociado como uma ação. O BOVA11 "
        "copia o Ibovespa: se o índice sobe 10%, a cota sobe cerca de 10%."
    )
    params = (
        ParamSpec(
            key="asset",
            label="Ativo",
            kind=StrategyParamKind.TICKER,
            default=DEFAULT_ASSET,
            hint=(
                "A ação ou o ETF que recebe todo o caixa. O padrão é o BOVA11; se a "
                "partida não tem o BOVA11, o padrão é a ação mais negociada dela."
            ),
        ),
    )

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        ticker = param_ticker(params, "asset")
        quote = ctx.quotes.get(ticker)
        if quote is None:
            return

        quantity = int(ctx.cash // Decimal(str(quote.close)))
        if quantity > 0:
            ctx.buy(ticker, quantity, f"Pôs o caixa parado em {ticker}")

    def signal(
        self, history: pd.DataFrame, params: dict[str, StrategyParamValue]
    ) -> Signal | None:
        if history.empty:
            return None

        close = history["close"].iloc[-CHART_DAYS:]
        return Signal(
            lines=[
                SignalLineDTO(
                    key="price",
                    label="Preço",
                    style=SignalLineStyle.PRICE,
                    pane=SignalPane.PRICE,
                    points=[
                        SignalPointDTO(date=day.date(), value=round(float(value), 2))
                        for day, value in close.items()
                    ],
                )
            ],
            markers=[],
        )
