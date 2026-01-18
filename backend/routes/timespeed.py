from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.features.realtime import notify
from backend.features.simulation.simulation_loop import simulation_controller

timespeed_router = APIRouter(prefix="/api", tags=["Simulation Control"])


class SetSpeedRequest(BaseModel):
    speed: int = 0


@timespeed_router.post("/set-speed")
def set_speed(simulation: ActiveSimulation, payload: SetSpeedRequest):
    speed = payload.speed

    simulation.set_speed(speed)
    speed = simulation.get_speed()
    simulation.set_speed(speed)
    if speed <= 0:
        simulation_controller.pause()
    else:
        simulation_controller.unpause()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return JSONResponse(content={"speed": speed})


@timespeed_router.get("/get-simulation-state")
def get_simulation_state(client_id: ClientID, simulation: ActiveSimulation):
    current_date = simulation.get_current_date_formatted()
    speed = simulation.get_speed()
    cash = simulation.get_cash(client_id)
    return JSONResponse(
        content={"currentDate": current_date, "speed": speed, "cash": cash}
    )
