from decimal import Decimal

from backend.core.dto.base import BaseDTO


class GoalRunnerDTO(BaseDTO):
    nickname: str
    # Chave da paleta (chart-1 a chart-10)
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes
    team: int | None
    networth: Decimal


class GoalProgressDTO(BaseDTO):
    """Onde cada jogador está na corrida à meta, no último pregão simulado."""

    goal: Decimal
    players: list[GoalRunnerDTO]
