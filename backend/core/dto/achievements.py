from datetime import date, datetime
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import AchievementCategory, AchievementIcon, AchievementUnit


class AchievementProgressDTO(BaseDTO):
    """Onde a conquista com meta numérica está: `current` de `goal`, na unidade `unit`."""

    current: Decimal
    goal: Decimal
    unit: AchievementUnit


class AchievementUnlockDTO(BaseDTO):
    unlocked_at: datetime
    game_date: date
    # Vazios quando a partida em que a conquista saiu foi excluída
    simulation_id: int | None
    simulation_name: str | None
    # Ainda não vista: o jogador não abriu a tela depois que ela saiu
    is_new: bool


class AchievementDTO(BaseDTO):
    code: str
    # Secreta e bloqueada: sem nome nem descrição, o servidor não os revela
    name: str | None
    description: str | None
    icon: AchievementIcon
    category: AchievementCategory
    secret: bool
    unlock: AchievementUnlockDTO | None
    progress: AchievementProgressDTO | None


class UnlockedAchievementDTO(BaseDTO):
    code: str
    name: str
    description: str
    icon: AchievementIcon
    secret: bool


class AchievementUnlockedEventDTO(BaseDTO):
    """As conquistas que saíram no último tick, de uma vez, para um toast só."""

    achievements: list[UnlockedAchievementDTO]
