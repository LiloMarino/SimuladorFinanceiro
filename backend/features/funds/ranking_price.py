from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

# Pregões da janela do VWAP e a distância máxima ao PL, em fração dele
RANKING_WINDOW = 20
RANKING_BAND = Decimal("0.30")


@dataclass(frozen=True)
class TradedDay:
    """O que negociou num pregão: a quantidade e a soma de preço x quantidade."""

    quantity: Decimal
    value: Decimal


def ranking_price(days: Sequence[TradedDay], nav: Decimal) -> Decimal:
    """O preço da cota no ranking: o VWAP (média dos preços ponderada pela quantidade) dos
    últimos pregões, travado em ±30% do PL por cota do dia.

    Sem negócio na janela, a cota vale o PL. `days` vem em ordem cronológica.
    """
    window = days[-RANKING_WINDOW:]
    quantity = sum((day.quantity for day in window), Decimal(0))
    if quantity == 0:
        return nav
    vwap = sum((day.value for day in window), Decimal(0)) / quantity
    return min(max(vwap, nav * (1 - RANKING_BAND)), nav * (1 + RANKING_BAND))
