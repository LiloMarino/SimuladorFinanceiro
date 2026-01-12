from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.simulation import SimulationDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.simulation_loop import simulation_controller
from backend.routes.helpers import make_response

simulation_router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class CreateSimulationRequest(BaseModel):
    start_date: str
    end_date: str


class ContinueSimulationRequest(BaseModel):
    end_date: str


class UpdateSettingsRequest(BaseModel):
    start_date: str
    end_date: str


@simulation_router.get("/status")
def simulation_status():
    try:
        sim = SimulationManager.get_active_simulation()
        data = sim.settings
        return make_response(
            True,
            "Simulation active.",
            data={
                "active": True,
                "simulation": data.to_json(),
            },
        )
    except NoActiveSimulationError:
        return make_response(
            True,
            "No active simulation.",
            data={
                "active": False,
            },
        )


@simulation_router.post("/create", status_code=201)
def create_simulation(payload: CreateSimulationRequest, _: HostVerified):
    try:
        start_date = datetime.strptime(payload.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(payload.end_date, "%Y-%m-%d").date()
    except Exception as e:
        raise UnprocessableEntityError("Invalid start_date or end_date.") from e

    repository.user.reset_users_data(start_date)
    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=start_date,
            end_date=end_date,
        )
    )
    data = sim.settings
    simulation_controller.trigger_start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": data.to_json(),
        },
    )
    return make_response(
        True,
        "Simulation created.",
        status_code=201,
        data={
            "active": True,
            "simulation": data.to_json(),
        },
    )


@simulation_router.post("/continue", status_code=201)
def continue_simulation(payload: ContinueSimulationRequest, _: HostVerified):
    """Continua a simulação a partir do último snapshot"""

    try:
        end_date = datetime.strptime(payload.end_date, "%Y-%m-%d").date()
    except Exception as e:
        raise UnprocessableEntityError("Invalid end_date.") from e

    last_snapshot_date = repository.snapshot.get_last_snapshot_date()
    if not last_snapshot_date:
        raise NotFoundError("No snapshots found to continue simulation.")

    if last_snapshot_date >= end_date:
        raise UnprocessableEntityError(
            "Last snapshot date is after or equal to the target end date."
        )

    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=last_snapshot_date,
            end_date=end_date,
        )
    )

    simulation_controller.trigger_start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )

    return make_response(
        True,
        "Simulation continued from last snapshot.",
        status_code=201,
        data={
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )


@simulation_router.get("/players")
def get_active_players():
    active_players = UserManager.list_active_players()
    return make_response(
        True,
        "Players loaded successfully.",
        data=[{"nickname": p.nickname} for p in active_players],
    )


@simulation_router.get("/settings")
def get_simulation_settings(client_id: ClientID):
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("User not found.")
    host_nickname = config.toml.host.nickname

    settings = SimulationManager.get_settings()
    return make_response(
        True,
        "Simulation settings loaded.",
        data={
            "is_host": user.nickname == host_nickname,
            "simulation": settings.to_json(),
        },
    )


@simulation_router.put("/settings")
def update_simulation_settings(payload: UpdateSettingsRequest, _: HostVerified):
    try:
        start_date = datetime.strptime(payload.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(payload.end_date, "%Y-%m-%d").date()
    except Exception as e:
        raise UnprocessableEntityError("Invalid payload.") from e

    if start_date > end_date:
        raise UnprocessableEntityError("start_date must be before end_date.")

    settings = SimulationManager.update_settings(
        SimulationDTO(
            start_date=start_date,
            end_date=end_date,
        )
    )

    notify("simulation_settings_update", settings.to_json())

    return make_response(
        True,
        "Simulation settings updated.",
        data=settings.to_json(),
    )
