"""
Time speed and simulation state routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.features.realtime import notify
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["timespeed"])


class SetSpeedRequest(BaseModel):
    speed: int


@router.post("/set-speed")
async def set_speed(request: SetSpeedRequest, simulation: ActiveSimulation):
    """Set simulation speed."""
    speed = request.speed

    simulation.set_speed(speed)
    speed = simulation.get_speed()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return make_response_data(True, "Speed updated", data={"speed": speed})


@router.get("/get-simulation-state")
async def get_simulation_state(client_id: ClientID, simulation: ActiveSimulation):
    """Get current simulation state."""
    current_date = simulation.get_current_date_formatted()
    speed = simulation.get_speed()
    cash = simulation.get_cash(client_id)
    return make_response_data(
        True,
        "Simulation state",
        data={"currentDate": current_date, "speed": speed, "cash": cash},
    )
