from typing import Annotated

from fastapi import APIRouter, Query

from backend.core import repository
from backend.core.dependencies import ActiveSimulation
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.player_history import PerformanceReportDTO
from backend.features.statistics.ranking import build_performance_report

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


@statistics_router.get(
    "/statistics",
    response_model=PerformanceReportDTO,
    summary="Obter estatísticas de desempenho",
    description="Retorna o ranking e o histórico de desempenho de todos os jogadores da simulação.",
)
def get_statistics(simulation: ActiveSimulation):
    """
    Retorna as estatísticas de desempenho dos jogadores.
    """
    stats = simulation.get_statistics()
    return stats


@statistics_router.get(
    "/statistics/compare",
    response_model=PerformanceReportDTO,
    summary="Comparar simulações",
    description="Retorna o ranking e o histórico de desempenho de cada jogador em cada simulação salva informada.",
)
def compare_simulations(simulation_ids: Annotated[list[int], Query(min_length=1)]):
    """
    Compara o desempenho dos jogadores entre simulações salvas.
    """
    players = repository.statistics.get_players_history(simulation_ids)
    return build_performance_report(players)


@statistics_router.get(
    "/economic-indicators",
    response_model=EconomicIndicatorsDTO,
    summary="Obter indicadores econômicos",
    description="Retorna os indicadores econômicos da simulação atual.",
)
def get_economic_indicators(simulation: ActiveSimulation):
    """
    Retorna os indicadores econômicos da simulação.
    """
    indicators = simulation.get_economic_indicators()
    return indicators
