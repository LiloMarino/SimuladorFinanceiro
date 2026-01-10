from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation
from backend.routes.helpers import make_response

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


@statistics_router.get("/statistics")
def get_statistics(simulation: ActiveSimulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return make_response(
        True,
        "Statistics loaded successfully.",
        data=[stat.to_json() for stat in stats],
    )


@statistics_router.get("/economic-indicators")
def get_economic_indicators(simulation: ActiveSimulation):
    """Return economic indicators."""
    indicators = simulation.get_economic_indicators()
    return make_response(
        True, "Economic indicators loaded successfully.", data=indicators
    )
