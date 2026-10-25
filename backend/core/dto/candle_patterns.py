"""
Padrões de vela de uma ação: onde cada um apareceu no histórico, o que o preço fez
nos 5 pregões seguintes e quantas vezes ele acertou o lado que sugere.
"""

from datetime import date
from typing import Literal

from backend.core.dto.base import BaseDTO

type CandlePatternCode = Literal[
    "hammer",
    "inverted_hammer",
    "hanging_man",
    "shooting_star",
    "doji",
    "bullish_engulfing",
    "bearish_engulfing",
    "morning_star",
    "evening_star",
    "three_white_soldiers",
    "three_black_crows",
]

# O lado que o padrão sugere para o preço; o doji é indecisão e não sugere lado
type PatternDirection = Literal["up", "down", "neutral"]


class CandlePatternDTO(BaseDTO):
    code: CandlePatternCode
    # Primeira e última vela do padrão (a mesma, nos de uma vela só)
    start: date
    end: date
    direction: PatternDirection
    # Variação do fechamento do 5º pregão depois do fim do padrão (0,028 = +2,8%);
    # None enquanto ainda não houve 5 pregões
    change_5d: float | None
    # Se o preço foi para o lado sugerido; None sem desfecho, sem lado ou sem variação
    hit: bool | None


class PatternStatsDTO(BaseDTO):
    code: CandlePatternCode
    # Ocorrências com desfecho e com variação diferente de zero
    checked: int
    hits: int


class CandlePatternsDTO(BaseDTO):
    """A lista e as estatísticas contam o histórico inteiro até a data da simulação."""

    patterns: list[CandlePatternDTO]
    stats: list[PatternStatsDTO]
