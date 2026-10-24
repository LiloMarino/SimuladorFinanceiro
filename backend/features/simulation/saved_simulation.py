from datetime import date

from backend.core import repository
from backend.core.dto.simulation import (
    SavedSimulationDTO,
    SimulationResultDTO,
    SimulationSummaryDTO,
)
from backend.core.dto.statistics_report import OverviewReportDTO
from backend.core.enum import GameType, SimulationStatus
from backend.core.runtime.simulation_manager import SimulationManager
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
    if not overview.game_type.has_goal:
        return False
    leaders = overview.teams or overview.players
    value = leaders[0].criterion_value if leaders else None
    return value is not None and value >= 1


def compute_result(simulation_id: int) -> SimulationResultDTO:
    """Refaz o ranking da simulação pelos snapshots gravados."""
    overview = build_overview_report([simulation_id])
    players = overview.players
    if overview.game_type is GameType.POLITICAL:
        return _political_result(overview)
    if overview.teams:
        leader = team_name(overview.teams[0].team, overview.team_naming)
        team_position = {t.team: t.position for t in overview.teams}
        positions = {
            p.player_nickname: team_position[p.team]
            for p in players
            if p.team in team_position
        }
    else:
        leader = players[0].player_nickname if players else None
        positions = {p.player_nickname: p.position for p in players}
    return SimulationResultDTO(
        leader_reached_goal=leader_reached_goal(overview),
        players_count=len(players),
        leader_name=leader,
        positions=positions,
    )


def _political_result(overview: OverviewReportDTO) -> SimulationResultDTO:
    """Vence o partido com a maior soma de patrimônio; quem está fora de partido fica sem colocação."""
    parties = overview.parties
    return SimulationResultDTO(
        leader_reached_goal=False,
        players_count=len(overview.players),
        leader_name=parties[0].name if parties else None,
        positions={
            member: party.position for party in parties for member in party.members
        },
    )


def saved_result(simulation_id: int, resume_from: date | None) -> SimulationResultDTO:
    """
    O ranking até `resume_from`. O guardado vale enquanto a simulação não grava um
    dia novo; a que está rodando agora muda a cada pregão e não é guardada.
    """
    stored = repository.simulation.get_result(simulation_id)
    if stored is not None and stored[0] == resume_from:
        return stored[1]

    result = compute_result(simulation_id)
    if SimulationManager.find_active_simulation_id() != simulation_id:
        repository.simulation.save_result(simulation_id, resume_from, result)
    return result


def describe(
    summary: SimulationSummaryDTO, nickname: str | None, room_overflow: list[str]
) -> SavedSimulationDTO:
    """Simulação salva como a lista mostra: onde parou, quantos jogaram, quem venceu,
    em que colocação `nickname` ficou e quem da sala não cabe nela. Em equipes, vence e
    ranqueia a equipe: o vencedor é o nome dela e a colocação é a da equipe de `nickname`."""
    resume_from = resume_point(summary.id)
    result = saved_result(summary.id, resume_from)
    finished = is_finished(summary.end_date, resume_from) or result.leader_reached_goal

    return SavedSimulationDTO(
        **summary.model_dump(),
        resume_from=resume_from,
        status=SimulationStatus.FINISHED if finished else SimulationStatus.PAUSED,
        players_count=result.players_count,
        winner_nickname=result.leader_name if finished else None,
        leader_nickname=result.leader_name,
        my_position=result.positions.get(nickname) if nickname else None,
        room_overflow=room_overflow,
    )
