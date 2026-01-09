"""
Simulation management routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.simulation import SimulationDTO
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.fastapi_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.simulation_loop import controller
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


# Request models
class CreateSimulationRequest(BaseModel):
    start_date: str  # Format: YYYY-MM-DD
    end_date: str  # Format: YYYY-MM-DD


class ContinueSimulationRequest(BaseModel):
    end_date: str  # Format: YYYY-MM-DD


class UpdateSettingsRequest(BaseModel):
    start_date: str  # Format: YYYY-MM-DD
    end_date: str  # Format: YYYY-MM-DD


@router.get("/status")
async def simulation_status():
    """Get current simulation status."""
    try:
        sim = SimulationManager.get_active_simulation()
        data = sim.settings
        return make_response_data(
            True,
            "Simulation active.",
            data={
                "active": True,
                "simulation": data.to_json(),
            },
        )
    except NoActiveSimulationError:
        return make_response_data(
            True,
            "No active simulation.",
            data={
                "active": False,
            },
        )


@router.post("/create")
async def create_simulation(request: CreateSimulationRequest, _: HostVerified):
    """Create a new simulation (host only)."""
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
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
    controller.trigger_start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": data.to_json(),
        },
    )
    return make_response_data(
        True,
        "Simulation created.",
        data={
            "active": True,
            "simulation": data.to_json(),
        },
    )


@router.post("/continue")
async def continue_simulation(request: ContinueSimulationRequest, _: HostVerified):
    """Continua a simulação a partir do último snapshot (host only)."""

    try:
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
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

    controller.trigger_start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )

    return make_response_data(
        True,
        "Simulation continued from last snapshot.",
        data={
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )


@router.get("/players")
async def get_active_players():
    """Get list of active players."""
    active_players = UserManager.list_active_players()
    return make_response_data(
        True,
        "Players loaded successfully.",
        data=[{"nickname": p.nickname} for p in active_players],
    )


@router.get("/settings")
async def get_simulation_settings(client_id: ClientID):
    """Get simulation settings for current user."""
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("User not found.")
    host_nickname = config.toml.host.nickname

    settings = SimulationManager.get_settings()
    return make_response_data(
        True,
        "Simulation settings loaded.",
        data={
            "is_host": user.nickname == host_nickname,
            "simulation": settings.to_json(),
        },
    )


@router.put("/settings")
async def update_simulation_settings(request: UpdateSettingsRequest, _: HostVerified):
    """Update simulation settings (host only)."""

    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
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

    return make_response_data(
        True,
        "Simulation settings updated.",
        data=settings.to_json(),
    )
