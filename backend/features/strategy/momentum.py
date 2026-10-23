from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.strategy import (
    AllocationViewDTO,
    RankingRowDTO,
    RankingViewDTO,
    StrategyParamValue,
)
from backend.core.enum import StrategyGroup, StrategyParamKind, StrategyView
from backend.features.strategy.base_strategy import (
    BaseStrategy,
    ParamSpec,
    param_int,
    param_tickers,
)
from backend.features.strategy.context import StrategyContext

# Pregões de um ano de mercado
LOOKBACK_DAYS = 252
RETURN_PLACES = Decimal("0.0001")


class TwelveMonthMomentum(BaseStrategy):
    """
    No primeiro pregão de cada mês, fica com as ações da lista que mais subiram em
    12 meses (só as de retorno positivo), em partes iguais: vende a parte livre das
    que saíram do ranking e compra as que entraram. A parte de quem fica de fora
    do ranking fica em caixa até a próxima troca.
    """

    key = "momentum_12m"
    name = "Momentum de 12 meses"
    summary = "Fica com as que mais subiram no ano."
    description = (
        "Todo mês, no primeiro pregão, ordena as ações da lista pelo retorno dos "
        "últimos 12 meses e fica com as que mais subiram, em partes iguais. Ações que "
        "caíram no ano ficam de fora."
    )
    group = StrategyGroup.TACTIC
    view_kind = StrategyView.RANKING
    term_hint = (
        "Momentum é a tendência de quem subiu continuar subindo. O retorno de 12 meses "
        "compara o preço de hoje com o de 252 pregões atrás. Ex.: de R$ 20 para "
        "R$ 25 é +25%."
    )
    params = (
        ParamSpec(
            key="top",
            label="Quantas ações",
            kind=StrategyParamKind.INT,
            default=3,
            min=1,
            max=10,
            unit="ações",
            hint=(
                "Quantas ações da lista ela mantém, as de maior retorno em 12 meses. "
                "Com 3 e R$ 30.000, cada uma recebe até R$ 10.000. Se menos de 3 "
                "subiram no ano, a parte das que faltam fica em caixa."
            ),
        ),
        ParamSpec(
            key="tickers",
            label="Ações que ela compara",
            kind=StrategyParamKind.TICKERS,
            hint=(
                "O universo do ranking: ela só compra e vende estas ações. O padrão "
                "são as 10 mais negociadas da partida: as de maior volume financeiro "
                "médio nos últimos 60 pregões, calculado ao ligar."
            ),
        ),
    )

    @classmethod
    def needed_days(cls, params: dict[str, StrategyParamValue]) -> int:
        # O preço de hoje e o de 252 pregões atrás
        return LOOKBACK_DAYS + 1

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        tickers = param_tickers(params, "tickers")
        top = param_int(params, "top")
        if not _first_session_of_month(ctx, tickers):
            return

        chosen = _chosen(_returns(ctx, tickers), top)

        # O dinheiro das vendas entra no caixa antes das compras
        cash = ctx.cash
        for ticker in tickers:
            holding = ctx.holdings.get(ticker)
            quote = ctx.quotes.get(ticker)
            if ticker in chosen or holding is None or quote is None:
                continue
            free = holding.size - holding.reserved
            if free > 0:
                ctx.sell(ticker, free, "Saiu do ranking de retorno de 12 meses")
                cash += Decimal(str(quote.close)) * free

        # Partes iguais do caixa mais o que já está nas ações da lista
        invested = Decimal(0)
        for ticker in tickers:
            holding = ctx.holdings.get(ticker)
            quote = ctx.quotes.get(ticker)
            if holding and quote:
                invested += Decimal(str(quote.close)) * holding.size
        share = (ctx.cash + invested) / top
        for ticker in chosen:
            quote = ctx.quotes.get(ticker)
            if quote is None:
                continue
            price = Decimal(str(quote.close))
            holding = ctx.holdings.get(ticker)
            gap = share - (price * holding.size if holding else Decimal(0))
            quantity = int(min(gap, cash) // price)
            if quantity > 0:
                ctx.buy(
                    ticker,
                    quantity,
                    "Entrou no ranking de retorno de 12 meses",
                )
                cash -= price * quantity

    def view(
        self, ctx: StrategyContext, params: dict[str, StrategyParamValue]
    ) -> RankingViewDTO | AllocationViewDTO | None:
        tickers = param_tickers(params, "tickers")
        returns = _returns(ctx, tickers)
        chosen = set(_chosen(returns, param_int(params, "top")))
        # Quem tem retorno vem na frente, do maior ao menor
        ranked = sorted(
            returns, key=lambda t: (returns[t] is None, -(returns[t] or 0), t)
        )
        return RankingViewDTO(
            rows=[
                RankingRowDTO(
                    ticker=ticker,
                    name=quote.name if (quote := ctx.quotes.get(ticker)) else ticker,
                    return_12m=None
                    if returns[ticker] is None
                    else Decimal(str(returns[ticker])).quantize(RETURN_PLACES),
                    selected=ticker in chosen,
                )
                for ticker in ranked
            ],
            next_switch=_next_month(ctx.date),
            needed_days=self.needed_days(params),
        )


def _first_session_of_month(ctx: StrategyContext, tickers: list[str]) -> bool:
    """O pregão anterior do histórico é de outro mês."""
    for ticker in tickers:
        frame = ctx.history(ticker, 2)
        if len(frame) == 2:
            return frame.index[-2].month != ctx.date.month
    return False


def _returns(ctx: StrategyContext, tickers: list[str]) -> dict[str, float | None]:
    """Retorno dos últimos 252 pregões de cada ação; nulo quando o histórico não chega."""
    returns: dict[str, float | None] = {}
    for ticker in tickers:
        close = ctx.history(ticker, LOOKBACK_DAYS + 1)["close"]
        returns[ticker] = (
            float(close.iloc[-1] / close.iloc[0] - 1)
            if len(close) == LOOKBACK_DAYS + 1
            else None
        )
    return returns


def _chosen(returns: dict[str, float | None], top: int) -> list[str]:
    """As `top` ações de maior retorno, só as que subiram, da maior para a menor."""
    rising = [(ret, ticker) for ticker, ret in returns.items() if ret and ret > 0]
    rising.sort(key=lambda pair: (-pair[0], pair[1]))
    return [ticker for _, ticker in rising[:top]]


def _next_month(today: date) -> date:
    if today.month == 12:
        return date(today.year + 1, 1, 1)
    return date(today.year, today.month + 1, 1)
