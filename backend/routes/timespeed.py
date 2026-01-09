from fastapi import APIRouter
from pydantic import BaseModel

from backend.fastapi_deps import ActiveSimulation, ClientID
from backend.fastapi_helpers import make_response
from backend.features.realtime import notify

timespeed_router = APIRouter(prefix="/api", tags=["timespeed"])


class SetSpeedRequest(BaseModel):
    speed: int = 0


@timespeed_router.post("/set-speed")
def set_speed(simulation: ActiveSimulation, payload: SetSpeedRequest):
    simulation.set_speed(payload.speed)
    speed = simulation.get_speed()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return make_response(True, "Speed updated", data={"speed": speed})


@timespeed_router.get("/get-simulation-state")
def get_simulation_state(client_id: ClientID, simulation: ActiveSimulation):
    current_date = simulation.get_current_date_formatted()
    speed = simulation.get_speed()
    cash = simulation.get_cash(client_id)
    return make_response(
        True,
        "Simulation state",
        data={"currentDate": current_date, "speed": speed, "cash": cash},
    )
