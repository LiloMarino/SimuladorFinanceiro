from datetime import date

from backend.core import repository
from backend.core.dto.simulation import SavedSimulationDTO, SimulationSummaryDTO
from backend.core.enum import SimulationStatus
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


def describe(
    summary: SimulationSummaryDTO, nickname: str | None, room_overflow: list[str]
) -> SavedSimulationDTO:
    """Simulação salva como a lista mostra: onde parou, quantos jogaram, quem venceu,
    em que colocação `nickname` ficou e quem da sala não cabe nela."""
    resume_from = resume_point(summary.id)
    finished = is_finished(summary.end_date, resume_from)
    players = build_overview_report([summary.id]).players

    return SavedSimulationDTO(
        **summary.model_dump(),
        resume_from=resume_from,
        status=SimulationStatus.FINISHED if finished else SimulationStatus.PAUSED,
        players_count=len(players),
        winner_nickname=players[0].player_nickname if finished and players else None,
        my_position=next(
            (p.position for p in players if p.player_nickname == nickname), None
        ),
        room_overflow=room_overflow,
    )
