"""
Desafio da vela do lobby: todos veem o mesmo recorte de velas que termina num padrão,
respondem se o preço sobe ou desce nos 5 pregões seguintes e a revelação mostra o que
aconteceu. A rodada tem 10 perguntas e o placar é da sala.
"""

from datetime import date
from typing import Literal

from backend.core.dto.base import BaseDTO
from backend.core.dto.candle_patterns import CandlePatternCode, PatternStatsDTO

type ChallengeDirection = Literal["up", "down"]

# O que o preço fez nos 5 pregões: subiu, desceu ou fechou igual (pergunta anulada)
type ChallengeOutcome = Literal["up", "down", "void"]

# Como o jogador foi numa pergunta: acertou, errou ou não respondeu
type ChallengeMark = Literal["hit", "miss", "none"]

# Sem rodada, rodada rolando ou rodada terminada (com o pódio na tela)
type ChallengeStatus = Literal["idle", "running", "finished"]

# Buscando a pergunta, pergunta aberta ou resultado dela na tela
type ChallengePhase = Literal["loading", "question", "reveal"]

# O que motiva um aviso em toast para a sala
type ChallengeNoticeKind = Literal["joined", "ended_by_match", "unavailable"]

QUESTIONS_PER_ROUND = 10


class CandleBarDTO(BaseDTO):
    """Uma vela em % desde a abertura da primeira vela do recorte: a escala de preço não aparece."""

    open: float
    high: float
    low: float
    close: float


class ChallengeQuestionDTO(BaseDTO):
    """A pergunta aberta: o ativo, a data e o que vem depois ficam escondidos até a revelação."""

    # Muda a cada pergunta aberta, inclusive as anuladas que repetem o número
    id: int
    pattern_code: CandlePatternCode
    bars: list[CandleBarDTO]
    # Quantas vezes o padrão acertou o lado que sugere na base, para a dica do nome
    stats: PatternStatsDTO
    # Tempo que falta para fechar e tempo total, em ms: o relógio é do servidor
    remaining_ms: int
    duration_ms: int


class ChallengeVoteDTO(BaseDTO):
    nickname: str
    direction: ChallengeDirection


class ChallengeRevealDTO(BaseDTO):
    ticker: str
    # Primeiro pregão do recorte e o 5º pregão depois do padrão
    start: date
    end: date
    # As velas da pergunta e as 5 seguintes, na mesma escala
    bars: list[CandleBarDTO]
    bars_after: list[CandleBarDTO]
    outcome: ChallengeOutcome
    # Variação do fechamento do padrão até o 5º pregão depois, em fração (0,043 é +4,3%)
    change: float
    # Só a pergunta que valeu ponto; as anuladas não têm votos
    votes: list[ChallengeVoteDTO]
    # Tempo que falta para a próxima pergunta e tempo total, em ms
    remaining_ms: int
    duration_ms: int


class ChallengePlayerDTO(BaseDTO):
    nickname: str
    color: str
    position: int
    hits: int
    # Perguntas que valeram para ele, entre as já fechadas
    answered: int
    # Número da primeira pergunta que ele jogou; maior que 1 para quem entrou no meio
    joined_at: int
    # Respondeu a pergunta aberta, sem dizer o lado
    replied: bool
    # Como foi na última pergunta fechada; só na revelação
    last: ChallengeMark | None
    # Uma marca por pergunta fechada; nulo antes de ele entrar
    marks: list[ChallengeMark | None]


class ChallengeWinsDTO(BaseDTO):
    nickname: str
    wins: int


class ChallengeFinalDTO(BaseDTO):
    winners: list[str]
    # Sozinho: a sequência desta rodada contra o recorde de antes
    best_streak: int
    new_record: bool
    previous_record: int
    previous_record_on: date | None


class CandleChallengeStateDTO(BaseDTO):
    """O que a sala vê; o lado de cada resposta só aparece na revelação."""

    status: ChallengeStatus
    phase: ChallengePhase | None
    # Muda a cada rodada que começa: a tela guarda por ele o que o jogador já decidiu
    round_id: int
    # Quem começou a rodada, para o convite
    starter: str | None
    solo: bool
    # Número da pergunta que está na tela, de 1 a 10; as anuladas não contam
    number: int
    total: int
    question: ChallengeQuestionDTO | None
    reveal: ChallengeRevealDTO | None
    players: list[ChallengePlayerDTO]
    final: ChallengeFinalDTO | None
    # Vitórias da sala desde que o servidor ligou
    wins: list[ChallengeWinsDTO]
    rounds: int
    # Solo: sequência de acertos em andamento e recorde de antes da rodada
    streak: int
    record: int


class CandleChallengeViewDTO(BaseDTO):
    """O estado da sala visto por quem pergunta, com a resposta dele à pergunta aberta."""

    state: CandleChallengeStateDTO
    direction: ChallengeDirection | None


class AnswerChallengeRequest(BaseDTO):
    direction: ChallengeDirection


class ChallengeNoticeEventDTO(BaseDTO):
    kind: ChallengeNoticeKind
    # Quem entrou, ou a pergunta em que a rodada foi encerrada
    nickname: str | None
    number: int | None
