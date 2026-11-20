from decimal import Decimal

from backend.core.dto.base import BaseDTO


class GoalRunnerDTO(BaseDTO):
    nickname: str
    # Chave da paleta de jogadores (chart-N)
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes
    team: int | None
    # O nome da gestora da equipe na aquisição hostil em equipes; nulo fora dela
    team_name: str | None
    networth: Decimal


class GoalProgressDTO(BaseDTO):
    """Onde cada jogador está na corrida à meta, no último pregão simulado."""

    goal: Decimal
    players: list[GoalRunnerDTO]
