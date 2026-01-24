from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.player_history import PlayerHistoryDTO

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


@statistics_router.get(
    "/statistics",
    response_model=list[PlayerHistoryDTO],
    summary="Obter estatísticas de desempenho",
    description="Retorna o histórico de desempenho de todos os jogadores da simulação.",
)
def get_statistics(simulation: ActiveSimulation):
    """
    Retorna as estatísticas de desempenho dos jogadores.
    """
    stats = simulation.get_statistics()
    return stats


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
