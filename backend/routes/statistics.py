from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.core.dependencies import ActiveSimulation

statistics_router = APIRouter(prefix="/api", tags=["Statistics"])


@statistics_router.get("/statistics")
def get_statistics(simulation: ActiveSimulation):
    """Return performance statistics."""
    stats = simulation.get_statistics()
    return JSONResponse(content={"data": [stat.to_json() for stat in stats]})


@statistics_router.get("/economic-indicators")
def get_economic_indicators(simulation: ActiveSimulation):
    """Return economic indicators."""
    indicators = simulation.get_economic_indicators()
    return JSONResponse(content={"data": indicators})
