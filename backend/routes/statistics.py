from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation
from backend.routes.helpers import make_response

statistics_router = APIRouter()


@statistics_router.get("/api/statistics")
def get_statistics(simulation: ActiveSimulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return make_response(
        True,
        "Statistics loaded successfully.",
        data=[stat.to_json() for stat in stats],
    )
