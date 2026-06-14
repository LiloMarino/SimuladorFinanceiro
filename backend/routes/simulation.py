from datetime import date

from fastapi import APIRouter, status
from pydantic import BaseModel, Field, model_validator

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.simulation import (
    SimulationDTO,
    SimulationSettingsDTO,
    SimulationSummaryDTO,
)
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.simulation.simulation_loop import simulation_controller

simulation_router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class SimulationStatusResponse(BaseModel):
    active: bool
    simulation: SimulationDTO | None = None


class CreateSimulationRequest(BaseModel):
    name: str
    start_date: date
    end_date: date
    starting_cash: float = Field(gt=0)
    monthly_contribution: float = Field(ge=0, default=0.0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class LoadSimulationRequest(BaseModel):
    id: int


class UpdateSettingsRequest(BaseModel):
    name: str
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
    simulation: SimulationSettingsDTO


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
    settings = SimulationSettingsDTO(
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        starting_cash=payload.starting_cash,
        monthly_contribution=payload.monthly_contribution,
    )
    sim_dto = SimulationLoader.create(settings)
    return SimulationStatusResponse(active=True, simulation=sim_dto)


@simulation_router.post(
    "/continue",
    status_code=201,
    response_model=SimulationStatusResponse,
    summary="Continuar última simulação",
    description="Continua a simulação jogada mais recentemente, a partir do último snapshot salvo.",
)
def continue_simulation(_: HostVerified):
    """
    Continua a última simulação jogada.
    """
    summary = repository.simulation.get_last_simulated()
    if summary is None:
        raise NotFoundError("Nenhuma simulação encontrada para continuar.")

    sim_dto = SimulationLoader.load(summary)
    return SimulationStatusResponse(active=True, simulation=sim_dto)


@simulation_router.post(
    "/load",
    status_code=201,
    response_model=SimulationStatusResponse,
    summary="Carregar e iniciar simulação",
    description="Carrega uma simulação específica pelo id e a retoma a partir de onde parou.",
)
def load_simulation(payload: LoadSimulationRequest, _: HostVerified):
    """
    Carrega uma simulação salva e a inicia de onde parou.
    """
    summary = repository.simulation.get_simulation(payload.id)
    if summary is None:
        raise NotFoundError("Simulação não encontrada.")

    sim_dto = SimulationLoader.load(summary)
    return SimulationStatusResponse(active=True, simulation=sim_dto)


@simulation_router.get(
    "/list",
    response_model=list[SimulationSummaryDTO],
    summary="Listar simulações salvas",
    description="Retorna o histórico de simulações, ordenado pela última vez jogada.",
)
def list_simulations(search: str | None = None):
    """
    Lista as simulações persistidas (histórico).
    """
    return repository.simulation.list_simulations(search)


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

    settings = SettingsManager.get()
    return SimulationSettingsResponse(
        is_host=user.nickname == host_nickname,
        simulation=settings,
    )


@simulation_router.put(
    "/settings",
    response_model=SimulationSettingsDTO,
    summary="Atualizar configurações da simulação",
    description="Atualiza os parâmetros da simulação (datas, capital, contribuição mensal). Apenas o host pode executar.",
)
def update_simulation_settings(payload: UpdateSettingsRequest, _: HostVerified):
    """
    Atualiza as configurações da simulação.
    """
    settings = SettingsManager.update(
        SimulationSettingsDTO(
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            starting_cash=payload.starting_cash,
            monthly_contribution=payload.monthly_contribution,
        )
    )

    notify("simulation_settings_update", settings.to_json())
    return settings
