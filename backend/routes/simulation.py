from datetime import date

from fastapi import APIRouter, status
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


class SimulationStatusResponse(BaseModel):
    active: bool
    simulation: SimulationDTO | None = None


class CreateSimulationRequest(BaseModel):
    start_date: date
    end_date: date
    starting_cash: float = Field(gt=0)
    monthly_contribution: float = Field(ge=0, default=0.0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class ContinueSimulationRequest(BaseModel):
    end_date: date
    starting_cash: float = Field(gt=0)
    monthly_contribution: float = Field(ge=0, default=0.0)


class UpdateSettingsRequest(BaseModel):
    start_date: date
    end_date: date
    starting_cash: float = Field(gt=0)
    monthly_contribution: float = Field(ge=0, default=0.0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class PlayerNickname(BaseModel):
    nickname: str


class SimulationSettingsResponse(BaseModel):
    is_host: bool
    simulation: SimulationDTO


@simulation_router.get(
    "/status",
    response_model=SimulationStatusResponse,
    summary="Obter status da simulação",
    description="Retorna o status atual da simulação (ativa ou inativa) e seus parâmetros.",
)
def simulation_status():
    """
    Retorna o status atual da simulação.
    """
    try:
        sim = SimulationManager.get_active_simulation()
        data = sim.settings
        return SimulationStatusResponse(active=True, simulation=data)
    except NoActiveSimulationError:
        return SimulationStatusResponse(active=False, simulation=None)


@simulation_router.post(
    "/create",
    status_code=201,
    response_model=SimulationStatusResponse,
    summary="Criar nova simulação",
    description="Cria e inicia uma nova simulação com os parâmetros fornecidos (datas, capital inicial, contribuição mensal).",
)
def create_simulation(payload: CreateSimulationRequest, _: HostVerified):
    """
    Cria uma nova simulação financeira.
    """
    repository.user.reset_users_data(payload.start_date, payload.starting_cash)

    sim = SimulationManager.create_simulation(
        SimulationDTO(
            start_date=payload.start_date,
            end_date=payload.end_date,
            starting_cash=payload.starting_cash,
            monthly_contribution=payload.monthly_contribution,
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

    return SimulationStatusResponse(active=True, simulation=sim.settings)


@simulation_router.post(
    "/continue",
    status_code=201,
    response_model=SimulationStatusResponse,
    summary="Continuar simulação",
    description="Continua uma simulação anterior a partir do último snapshot salvo até a nova data de término.",
)
def continue_simulation(payload: ContinueSimulationRequest, _: HostVerified):
    """
    Continua uma simulação anterior.
    """
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
            monthly_contribution=payload.monthly_contribution,
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

    return SimulationStatusResponse(active=True, simulation=sim.settings)


@simulation_router.post(
    "/stop",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Parar simulação",
    description="Encerra a simulação atual manualmente.",
)
def stop_simulation(_: HostVerified):
    """
    Encerra a simulação atual.
    """
    simulation_controller.stop()

    notify(
        "simulation_ended",
        {
            "reason": "stopped_by_host",
        },
    )


@simulation_router.get(
    "/players",
    response_model=list[PlayerNickname],
    summary="Listar jogadores ativos",
    description="Retorna a lista de todos os usuários ativos na simulação atual.",
)
def get_active_players():
    """
    Lista todos os jogadores ativos na simulação.
    """
    active_players = UserManager.list_active_players()
    return [PlayerNickname(nickname=p.nickname) for p in active_players]


@simulation_router.get(
    "/settings",
    response_model=SimulationSettingsResponse,
    summary="Obter configurações da simulação",
    description="Retorna as configurações da simulação atual e indica se o usuário é o host.",
)
def get_simulation_settings(client_id: ClientID):
    """
    Retorna as configurações da simulação.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("User not found.")
    host_nickname = config.toml.host.nickname

    settings = SimulationManager.get_settings()
    return SimulationSettingsResponse(
        is_host=user.nickname == host_nickname,
        simulation=settings,
    )


@simulation_router.put(
    "/settings",
    response_model=SimulationDTO,
    summary="Atualizar configurações da simulação",
    description="Atualiza os parâmetros da simulação (datas, capital, contribuição mensal). Apenas o host pode executar.",
)
def update_simulation_settings(payload: UpdateSettingsRequest, _: HostVerified):
    """
    Atualiza as configurações da simulação.
    """
    settings = SimulationManager.update_settings(
        SimulationDTO(
            start_date=payload.start_date,
            end_date=payload.end_date,
            starting_cash=payload.starting_cash,
            monthly_contribution=payload.monthly_contribution,
        )
    )

    notify("simulation_settings_update", settings.to_json())
    return settings
