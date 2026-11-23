"""
O relatório da casa do Corretor no dia: quem entra no sorteio, o desfecho de cada
recomendação em aberto e a política do bot. Só funções do dia e do que o motor entrega.
"""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from backend.core.clt import cents
from backend.core.dto.candle import CandleDTO
from backend.core.dto.house_report import HousePickDTO, HouseRecommendationDTO
from backend.core.enum import AssetClass, OrderAction
from backend.core.house_report import (
    BOT_BUDGET_SHARE,
    MAX_HORIZON_MONTHS,
    Candidate,
    Verdict,
    deadline_of,
    judge,
)


def tradable_today(candles: Sequence[CandleDTO], day: date) -> list[CandleDTO]:
    """As ações negociadas no pregão de hoje: só a classe ação, com vela do dia."""
    return [
        candle
        for candle in candles
        if candle.asset_class is AssetClass.STOCK and candle.price_date == day
    ]


def candidates_of(
    candles: Sequence[CandleDTO],
    future: dict[str, list[tuple[date, Decimal, Decimal]]],
) -> list[Candidate]:
    """Cada ação negociável com o preço de hoje e o futuro guardado dela."""
    return [
        Candidate(candle.ticker, Decimal(str(candle.close)), future[candle.ticker])
        for candle in candles
        if future.get(candle.ticker)
    ]


def horizon_end(day: date, end_date: date) -> date:
    """O maior prazo que um relatório de `day` pode ter."""
    return deadline_of(day, MAX_HORIZON_MONTHS, end_date)


def verdicts_of(
    open_ones: Sequence[HouseRecommendationDTO],
    candles: Sequence[CandleDTO],
    day: date,
    next_day: date,
) -> dict[int, Verdict]:
    """O desfecho das recomendações em aberto que o pregão `day` decide, com a máxima, a mínima e o fechamento de cada ação."""
    by_ticker = {candle.ticker: candle for candle in candles}
    verdicts: dict[int, Verdict] = {}
    for recommendation in open_ones:
        candle = by_ticker.get(recommendation.ticker)
        if candle is None or candle.price_date != day:
            continue
        verdict = judge(
            recommendation.side,
            recommendation.target,
            recommendation.deadline,
            next_day,
            Decimal(str(candle.high)),
            Decimal(str(candle.low)),
            Decimal(str(candle.close)),
        )
        if verdict is not None:
            verdicts[recommendation.id] = verdict
    return verdicts


def picks_of(items: Sequence[HouseRecommendationDTO]) -> list[HousePickDTO]:
    """A ação e o lado de cada recomendação do relatório."""
    return [HousePickDTO(ticker=item.ticker, side=item.side) for item in items]


def bot_buys(items: Sequence[HouseRecommendationDTO]) -> list[HouseRecommendationDTO]:
    """As recomendações de compra do relatório; o bot ignora as de venda."""
    return [item for item in items if item.side is OrderAction.BUY]


def bot_budget_each(wealth: Decimal, cash: Decimal, buys: int) -> Decimal:
    """O valor de cada compra do bot: a fração do patrimônio, até o caixa livre, dividida em partes iguais entre as recomendações de compra; sem caixa, zero."""
    if buys <= 0 or cash <= 0:
        return Decimal(0)
    return cents(min(wealth * BOT_BUDGET_SHARE, cash) / buys)
