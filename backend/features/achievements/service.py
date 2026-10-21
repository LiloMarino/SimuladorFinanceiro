from decimal import Decimal

from backend.core import repository
from backend.core.dto.achievements import (
    AchievementDTO,
    AchievementProgressDTO,
    AchievementUnlockDTO,
)
from backend.features.achievements.catalog import CATALOG, Achievement


def list_achievements(user_id: int) -> list[AchievementDTO]:
    """O catálogo inteiro do jogador, na ordem do catálogo, com o que ele já tem."""
    unlocks = {u.code: u for u in repository.achievements.unlocks(user_id)}
    best = repository.achievements.best_progress(user_id)
    return [_describe(a, unlocks.get(a.code), best.get(a.code)) for a in CATALOG]


def mark_seen(user_id: int) -> None:
    repository.achievements.mark_seen(user_id)


def _describe(achievement: Achievement, unlock, best: Decimal | None) -> AchievementDTO:
    # A secreta bloqueada não revela o que pede nem como se chama
    hidden = achievement.secret and unlock is None
    return AchievementDTO(
        code=achievement.code,
        name=None if hidden else achievement.name,
        description=None if hidden else achievement.description,
        icon=achievement.icon,
        category=achievement.category,
        secret=achievement.secret,
        unlock=(
            None
            if unlock is None
            else AchievementUnlockDTO(
                unlocked_at=unlock.unlocked_at,
                game_date=unlock.game_date,
                simulation_id=unlock.simulation_id,
                simulation_name=unlock.simulation_name,
                is_new=unlock.seen_at is None,
            )
        ),
        progress=(
            AchievementProgressDTO(
                current=min(best or Decimal(0), achievement.goal),
                goal=achievement.goal,
                unit=achievement.unit,
            )
            if unlock is None and not hidden and achievement.unit is not None
            else None
        ),
    )
