from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.player_history import PlayerHistoryDTO

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


@statistics_router.get("/statistics", response_model=list[PlayerHistoryDTO])
def get_statistics(simulation: ActiveSimulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return stats


@statistics_router.get("/economic-indicators", response_model=EconomicIndicatorsDTO)
def get_economic_indicators(simulation: ActiveSimulation):
    """Return economic indicators."""
    indicators = simulation.get_economic_indicators()
    return indicators
