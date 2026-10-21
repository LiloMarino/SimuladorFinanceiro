from backend.core import repository
from backend.core.dto.achievements import (
    AchievementUnlockedEventDTO,
    UnlockedAchievementDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.dto.user import UserDTO
from backend.core.runtime.event_manager import EventManager
from backend.features.achievements.catalog import CATALOG, Achievement
from backend.features.achievements.metrics import (
    METRICS,
    Context,
    MatchResult,
    Trigger,
)
from backend.features.statistics.report import build_overview_report

ALL_TRIGGERS = frozenset(Trigger)


class AchievementEvaluator:
    """
    Avalia o catálogo para os jogadores de uma partida. Só as conquistas ainda
    bloqueadas são testadas, e cada métrica é calculada uma vez por jogador e pregão.
    """

    def __init__(self, settings: SimulationDTO):
        self._settings = settings
        # Conquistas já desbloqueadas de cada jogador, lidas do banco uma vez por partida
        self._unlocked: dict[int, set[str]] = {}

    def on_tick(
        self, snapshots: dict[int, SnapshotDTO], month_changed: bool
    ) -> dict[int, list[Achievement]]:
        """
        Roda as métricas do pregão: as do snapshot sempre, as de ordens para quem
        deu ordens e as do histórico na virada do mês, quando o progresso também é guardado.
        """
        touched = EventManager.pop_touched_users()
        unlocked = {}
        for user_id, snapshot in snapshots.items():
            triggers = {Trigger.TICK}
            if user_id in touched:
                triggers.add(Trigger.ORDER)
            if month_changed:
                triggers.add(Trigger.MONTH)
            context = Context(user_id, self._settings, snapshot)
            if new := self._evaluate(context, triggers, track_progress=month_changed):
                unlocked[user_id] = new
        return unlocked

    def on_match_end(
        self, snapshots: dict[int, SnapshotDTO], result: MatchResult
    ) -> dict[int, list[Achievement]]:
        """Roda todas as métricas com o resultado da partida na mão."""
        unlocked = {}
        for user_id, snapshot in snapshots.items():
            context = Context(user_id, self._settings, snapshot, result)
            if new := self._evaluate(context, ALL_TRIGGERS, track_progress=True):
                unlocked[user_id] = new
        return unlocked

    def _evaluate(
        self,
        context: Context,
        triggers: set[Trigger] | frozenset[Trigger],
        *,
        track_progress: bool,
    ) -> list[Achievement]:
        unlocked = self._unlocked_by(context.user_id)
        locked = [a for a in CATALOG if a.code not in unlocked]

        if track_progress:
            repository.achievements.save_progress(
                context.user_id,
                {a.code: context.value(a.metric) for a in locked if a.unit is not None},
            )

        reached = [
            a
            for a in locked
            if METRICS[a.metric].when in triggers and context.value(a.metric) >= a.goal
        ]
        new_codes = repository.achievements.unlock(
            context.user_id,
            [a.code for a in reached],
            self._settings.id,
            context.today,
        )
        unlocked.update(new_codes)
        return [a for a in reached if a.code in new_codes]

    def _unlocked_by(self, user_id: int) -> set[str]:
        if user_id not in self._unlocked:
            self._unlocked[user_id] = repository.achievements.unlocked_codes(user_id)
        return self._unlocked[user_id]


def match_result(
    simulation_id: int, participants: list[UserDTO], ended_by_goal: bool
) -> MatchResult:
    """Quem venceu a partida, pelo mesmo ranking do fechamento; em equipes, a equipe toda."""
    overview = build_overview_report([simulation_id])
    if overview.teams:
        winning_team = overview.teams[0].team
        names = {p.player_nickname for p in overview.players if p.team == winning_team}
    else:
        names = {p.player_nickname for p in overview.players[:1]}
    return MatchResult(
        winners=frozenset(u.id for u in participants if u.nickname in names),
        players_count=len(participants),
        ended_by_goal=ended_by_goal,
    )


def unlocked_event(achievements: list[Achievement]) -> AchievementUnlockedEventDTO:
    return AchievementUnlockedEventDTO(
        achievements=[
            UnlockedAchievementDTO(
                code=a.code,
                name=a.name,
                description=a.description,
                icon=a.icon,
                secret=a.secret,
            )
            for a in achievements
        ]
    )
