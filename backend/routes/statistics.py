from fastapi import APIRouter

from backend.fastapi_deps import ActiveSimulation
from backend.fastapi_helpers import make_response

statistics_router = APIRouter(prefix="/api", tags=["statistics"])


@statistics_router.get("/statistics")
def get_statistics(simulation: ActiveSimulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return make_response(
        True,
        "Statistics loaded successfully.",
        data=[stat.to_json() for stat in stats],
    )
