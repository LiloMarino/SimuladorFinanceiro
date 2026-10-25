"""
Desafio da vela: quando um padrão aparece no último pregão, o jogador responde se o
preço sobe ou desce, e o jogo confere no fechamento do 5º pregão depois do padrão.
"""

from datetime import date
from typing import Literal

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.dto.candle_patterns import CandlePatternCode, PatternStatsDTO

type ChallengeDirection = Literal["up", "down"]

# Como a resposta terminou: acertou, errou ou anulada (o preço fechou igual)
type ChallengeResult = Literal["hit", "miss", "void"]

# `waiting` espera o 5º pregão; `expired` é o padrão que passou sem resposta
type ChallengeStatus = Literal["waiting", "hit", "miss", "void", "expired"]


class OpenChallengeDTO(BaseDTO):
    """A pergunta de hoje: o padrão que fechou no último pregão e ainda não foi respondido."""

    pattern_code: CandlePatternCode
    pattern_date: date
    # Fechamento do dia do padrão, o preço de partida da conferência
    price: float
    # O 5º pregão depois do padrão, contado em dias úteis
    settles_on: date


class ChallengeAnswerDTO(BaseDTO):
    pattern_code: CandlePatternCode
    pattern_date: date
    status: ChallengeStatus
    # O que o jogador respondeu; None no desafio que passou sem resposta
    direction: ChallengeDirection | None
    price: float
    # O dia da conferência: previsto enquanto espera, o do 5º pregão depois de conferido
    settles_on: date
    # Pregões que faltam para a conferência; só na resposta que espera
    sessions_left: int | None
    # O preço de hoje na resposta que espera, o do 5º pregão na conferida
    current_price: float | None
    # Variação de `price` até `current_price`, em fração (0,023 é +2,3%)
    change: float | None
    # A taxa de acerto do padrão no histórico do ativo, para o card lembrar que padrão não é garantia
    stats: PatternStatsDTO


class ChallengeScoreDTO(BaseDTO):
    """Acertos entre as respostas já conferidas; as anuladas e as que esperam ficam fora."""

    hits: int
    answered: int


class CandleChallengeDTO(BaseDTO):
    open: OpenChallengeDTO | None
    last: ChallengeAnswerDTO | None
    score: ChallengeScoreDTO


class AnswerChallengeRequest(BaseDTO):
    direction: ChallengeDirection


class ChallengeRecordDTO(BaseDTO):
    """A resposta como está gravada."""

    simulation_id: int
    user_id: int
    ticker: str
    pattern_date: date
    pattern_code: CandlePatternCode
    direction: ChallengeDirection
    answered_on: date
    result: ChallengeResult | None
    settled_on: date | None


class ChallengeRankEntryDTO(BaseDTO):
    position: int = Field(ge=1)
    player_nickname: str
    hits: int
    answered: int


class CandleChallengeRankingDTO(BaseDTO):
    """O placar da partida, por acertos; no empate decide o percentual de acerto."""

    players: list[ChallengeRankEntryDTO]
