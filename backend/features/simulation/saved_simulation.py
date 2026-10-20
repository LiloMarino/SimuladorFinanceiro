from datetime import date

from backend.core import repository
from backend.core.dto.simulation import SavedSimulationDTO, SimulationSummaryDTO
from backend.core.dto.statistics_report import OverviewReportDTO
from backend.core.enum import GameType, SimulationStatus
from backend.core.teams import team_name
from backend.core.utils import next_business_day
from backend.features.statistics.report import build_overview_report


def resume_point(simulation_id: int) -> date | None:
    """
    Último dia que a simulação gravou, evento ou snapshot. A retomada parte do dia
    útil seguinte: um dia sem evento nem snapshot não mudou nada persistido.
    """
    last_dates = [
        d
        for d in (
            repository.event.get_last_event_date(simulation_id),
            repository.snapshot.get_last_snapshot_date(simulation_id),
        )
        if d is not None
    ]
    return max(last_dates) if last_dates else None


def is_finished(end_date: date, resume_from: date | None) -> bool:
    """Terminou quando o próximo pregão a simular já passa da data final."""
    return resume_from is not None and next_business_day(resume_from) > end_date


def leader_reached_goal(overview: OverviewReportDTO) -> bool:
    """Fora da Clássica, o valor do líder é a fração da meta: 1 é ter chegado."""
    if overview.game_type is GameType.CLASSIC:
        return False
    leaders = overview.teams or overview.players
    value = leaders[0].criterion_value if leaders else None
    return value is not None and value >= 1


def describe(
    summary: SimulationSummaryDTO, nickname: str | None, room_overflow: list[str]
) -> SavedSimulationDTO:
    """Simulação salva como a lista mostra: onde parou, quantos jogaram, quem venceu,
    em que colocação `nickname` ficou e quem da sala não cabe nela. Em equipes, vence e
    ranqueia a equipe: o vencedor é o nome dela e a colocação é a da equipe de `nickname`."""
    resume_from = resume_point(summary.id)
    overview = build_overview_report([summary.id])
    finished = is_finished(summary.end_date, resume_from) or leader_reached_goal(
        overview
    )
    players = overview.players

    mine = next((p for p in players if p.player_nickname == nickname), None)
    if overview.teams:
        winner = team_name(overview.teams[0].team, overview.team_naming)
        my_position = next(
            (t.position for t in overview.teams if mine and t.team == mine.team), None
        )
    else:
        winner = players[0].player_nickname if players else None
        my_position = mine.position if mine else None

    return SavedSimulationDTO(
        **summary.model_dump(),
        resume_from=resume_from,
        status=SimulationStatus.FINISHED if finished else SimulationStatus.PAUSED,
        players_count=len(players),
        winner_nickname=winner if finished else None,
        my_position=my_position,
        room_overflow=room_overflow,
    )
