from datetime import date

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

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

simulation_router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class CreateSimulationRequest(BaseModel):
    start_date: date
    end_date: date
    starting_cash: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class ContinueSimulationRequest(BaseModel):
    end_date: date
    starting_cash: float = Field(gt=0)


class UpdateSettingsRequest(BaseModel):
    start_date: date
    end_date: date
    starting_cash: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


@simulation_router.get("/status")
def simulation_status():
    try:
        sim = SimulationManager.get_active_simulation()
        data = sim.settings
        return JSONResponse(content={"active": True, "simulation": data.to_json()})
    except NoActiveSimulationError:
        return JSONResponse(content={"active": False})


@simulation_router.post("/create", status_code=201)
def create_simulation(payload: CreateSimulationRequest, _: HostVerified):
    repository.user.reset_users_data(payload.start_date, payload.starting_cash)

    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=payload.start_date,
            end_date=payload.end_date,
            starting_cash=payload.starting_cash,
        )
    )

    simulation_controller.start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )

    return {
        "active": True,
        "simulation": sim.settings.to_json(),
    }


@simulation_router.post("/continue", status_code=201)
def continue_simulation(payload: ContinueSimulationRequest, _: HostVerified):
    last_snapshot_date = repository.snapshot.get_last_snapshot_date()
    if not last_snapshot_date:
        raise NotFoundError("No snapshots found to continue simulation.")

    if last_snapshot_date >= payload.end_date:
        raise UnprocessableEntityError(
            "Last snapshot date is after or equal to the target end date."
        )

    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=last_snapshot_date,
            end_date=payload.end_date,
            starting_cash=payload.starting_cash,
        )
    )

    simulation_controller.start()

    notify(
        "simulation_started",
        {
            "active": True,
            "simulation": sim.settings.to_json(),
        },
    )

    return {
        "active": True,
        "simulation": sim.settings.to_json(),
    }


@simulation_router.post("/stop", status_code=204)
def stop_simulation(_: HostVerified):
    """Encerra a simulação manualmente"""
    simulation_controller.stop()

    notify(
        "simulation_ended",
        {
            "reason": "stopped_by_host",
        },
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@simulation_router.get("/players")
def get_active_players():
    active_players = UserManager.list_active_players()
    return JSONResponse(content=[{"nickname": p.nickname} for p in active_players])


@simulation_router.get("/settings")
def get_simulation_settings(client_id: ClientID):
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("User not found.")
    host_nickname = config.toml.host.nickname

    settings = SimulationManager.get_settings()
    return JSONResponse(
        content={
            "is_host": user.nickname == host_nickname,
            "simulation": settings.to_json(),
        }
    )


@simulation_router.put("/settings")
def update_simulation_settings(payload: UpdateSettingsRequest, _: HostVerified):
    settings = SimulationManager.update_settings(
        SimulationDTO(
            start_date=payload.start_date,
            end_date=payload.end_date,
            starting_cash=payload.starting_cash,
        )
    )

    notify("simulation_settings_update", settings.to_json())
    return settings.to_json()
