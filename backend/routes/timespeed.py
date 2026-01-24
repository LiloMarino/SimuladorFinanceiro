from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.features.realtime import notify
from backend.features.simulation.simulation_loop import simulation_controller

timespeed_router = APIRouter(prefix="/api", tags=["Simulation Control"])


class SetSpeedRequest(BaseModel):
    speed: int = 0


class SetSpeedResponse(BaseModel):
    speed: int


class SimulationStateResponse(BaseModel):
    current_date: str
    speed: int
    cash: float


@timespeed_router.post(
    "/set-speed",
    response_model=SetSpeedResponse,
    summary="Definir velocidade da simulação",
    description="Ajusta a velocidade de execução da simulação (0 para pausar, valores maiores para acelerar).",
)
def set_speed(simulation: ActiveSimulation, payload: SetSpeedRequest):
    """
    Define a velocidade de simulação.
    """
    speed = payload.speed
    simulation.set_speed(speed)
    speed = simulation.get_speed()
    if speed <= 0:
        simulation_controller.pause()
    else:
        simulation_controller.unpause()

    # Envia a atualização de velocidade para todos os clientes
    notify("speed_update", {"speed": speed})
    return SetSpeedResponse(speed=speed)


@timespeed_router.get(
    "/get-simulation-state",
    response_model=SimulationStateResponse,
    summary="Obter estado da simulação",
    description="Retorna o estado atual da simulação incluindo data, velocidade e saldo do cliente.",
)
def get_simulation_state(client_id: ClientID, simulation: ActiveSimulation):
    """
    Retorna o estado atual da simulação.
    """
    current_date = simulation.get_current_date_formatted()
    speed = simulation.get_speed()
    cash = simulation.get_cash(client_id)
    return SimulationStateResponse(
        current_date=current_date,
        speed=speed,
        cash=cash,
    )
