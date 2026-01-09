"""
Statistics routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from fastapi import APIRouter

from backend.core.dependencies import ActiveSimulation
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["statistics"])


@router.get("/statistics")
async def get_statistics(simulation: ActiveSimulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return make_response_data(
        True,
        "Statistics loaded successfully.",
        data=[stat.to_json() for stat in stats],
    )
