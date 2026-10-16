from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field, model_validator

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.simulation import (
    PriceImpactPointDTO,
    PriceImpactPreviewDTO,
    SavedSimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
)
from backend.core.enum import VictoryCriterion
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    SimulationEndedEventDTO,
    SimulationSelectedEventDTO,
)
from backend.features.simulation.saved_simulation import describe
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.variable_income.price_impact import decay, impact

simulation_router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class CreateSimulationRequest(BaseModel):
    name: str
    start_date: date
    end_date: date
    starting_cash: Decimal = Field(gt=0)
    monthly_contribution: Decimal = Field(ge=0, default=Decimal(0))
    price_impact_enabled: bool = False
    price_impact_k: float = Field(ge=0)
    price_impact_decay_days: int = Field(ge=1)
    victory_criterion: VictoryCriterion = VictoryCriterion.SCORE

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class SelectSimulationRequest(BaseModel):
    id: int


class PlayerColorRequest(BaseModel):
    color: str


class UpdateSettingsRequest(BaseModel):
    name: str
    start_date: date
    end_date: date
    starting_cash: Decimal = Field(gt=0)
    monthly_contribution: Decimal = Field(ge=0, default=Decimal(0))
    price_impact_enabled: bool = False
    price_impact_k: float = Field(ge=0)
    price_impact_decay_days: int = Field(ge=1)
    victory_criterion: VictoryCriterion = VictoryCriterion.SCORE

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class PlayerNickname(BaseModel):
    nickname: str
    # Chave da paleta (chart-1 a chart-10)
    color: str


class SimulationSettingsResponse(BaseModel):
    is_host: bool
    host_nickname: str
    simulation: SimulationSettingsDTO
    # Partida salva que o host escolheu para continuar; None quando é partida nova
    selected_simulation_id: int | None


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
    settings = SimulationSettingsDTO(**payload.model_dump())
    sim_dto = SimulationLoader.create(settings)
    return SimulationStatusResponse(active=True, simulation=sim_dto)


@simulation_router.post(
    "/continue",
    status_code=201,
    response_model=SimulationStatusResponse,
    summary="Continuar a simulação selecionada",
    description="Retoma a simulação salva que o host selecionou, a partir do dia seguinte ao último evento registrado.",
)
def continue_simulation(_: HostVerified):
    """
    Continua a simulação selecionada no lobby.
    """
    simulation_id = SettingsManager.get_selected_simulation_id()
    if simulation_id is None:
        raise ConflictError("Selecione uma partida salva para continuar.")

    summary = repository.simulation.get_simulation(simulation_id)
    if summary is None:
        raise NotFoundError("Simulação não encontrada.")

    sim_dto = SimulationLoader.load(summary)
    return SimulationStatusResponse(active=True, simulation=sim_dto)


@simulation_router.put(
    "/selection",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Selecionar simulação salva",
    description="Escolhe a simulação salva a continuar. As cores da sala passam a ser as guardadas nela. Apenas o host pode executar.",
)
def select_simulation(payload: SelectSimulationRequest, _: HostVerified):
    """
    Seleciona a simulação salva que o host vai continuar.
    """
    if SimulationManager.has_active_simulation():
        raise ConflictError("Já existe uma partida em andamento.")
    if repository.simulation.get_simulation(payload.id) is None:
        raise NotFoundError("Simulação não encontrada.")

    UserManager.apply_saved_colors(repository.simulation_player.colors(payload.id))
    SettingsManager.select_simulation(payload.id)
    notify(
        "simulation_selected",
        SimulationSelectedEventDTO(simulation_id=payload.id).to_json(),
    )


@simulation_router.delete(
    "/selection",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover a seleção da simulação salva",
    description="Volta ao lobby de partida nova; as cores da sala ficam como estão e podem ser trocadas. Apenas o host pode executar.",
)
def clear_selection(_: HostVerified):
    """
    Remove a seleção da simulação salva.
    """
    UserManager.release_saved_colors()
    SettingsManager.select_simulation(None)
    notify(
        "simulation_selected",
        SimulationSelectedEventDTO(simulation_id=None).to_json(),
    )


@simulation_router.get(
    "/list",
    response_model=list[SavedSimulationDTO],
    summary="Listar simulações salvas",
    description="Retorna o histórico de simulações, ordenado pela última vez jogada, com onde cada uma parou e quem venceu as terminadas.",
)
def list_simulations(client_id: ClientID, search: str | None = None):
    """
    Lista as simulações persistidas (histórico).
    """
    user = UserManager.get_user(client_id)
    nickname = user.nickname if user else None
    return [
        describe(s, nickname) for s in repository.simulation.list_simulations(search)
    ]


# Fração do volume médio diário usada no exemplo da prévia
PREVIEW_VOLUME_SHARE = 0.10


@simulation_router.get(
    "/price-impact-preview",
    response_model=PriceImpactPreviewDTO,
    summary="Prévia do impacto de preço",
    description="Quanto uma compra de 10% do volume médio diário move o preço no pregão seguinte e como o efeito some até voltar ao histórico.",
)
def price_impact_preview(
    k: float = Query(ge=0), decay_days: int = Query(ge=1, le=250)
) -> PriceImpactPreviewDTO:
    first_day = impact(round(PREVIEW_VOLUME_SHARE * 1_000_000), 1_000_000, k)
    return PriceImpactPreviewDTO(
        volume_share=PREVIEW_VOLUME_SHARE,
        first_day_impact=first_day,
        curve=[
            PriceImpactPointDTO(day=age + 1, impact=first_day * decay(age, decay_days))
            for age in range(decay_days + 1)
        ],
    )


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
    simulation_id = SimulationManager.get_active_simulation_id()
    simulation_controller.stop()

    notify(
        "simulation_ended",
        SimulationEndedEventDTO(
            reason="stopped_by_host", simulation_id=simulation_id
        ).to_json(),
    )


@simulation_router.get(
    "/players",
    response_model=list[PlayerNickname],
    summary="Listar jogadores ativos",
    description="Retorna a lista de todos os usuários ativos na simulação atual, cada um com a sua cor.",
)
def get_active_players():
    """
    Lista todos os jogadores ativos na simulação.
    """
    colors = UserManager.room_colors()
    return [
        PlayerNickname(nickname=p.nickname, color=colors[p.id])
        for p in UserManager.list_active_players()
        if p.id in colors
    ]


@simulation_router.put(
    "/players/me/color",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Escolher a cor do jogador",
    description="Troca a cor do jogador na sala. Vale o primeiro pedido: se a cor já tem dono, a resposta é 409 e o jogador fica com a que tinha.",
)
def set_player_color(payload: PlayerColorRequest, client_id: ClientID):
    """
    Troca a cor do jogador na sala.
    """
    UserManager.set_color(client_id, payload.color)


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
        raise NotFoundError("Usuário não encontrado.")
    host_nickname = config.toml.host.nickname

    settings = SettingsManager.get()
    return SimulationSettingsResponse(
        is_host=user.nickname == host_nickname,
        host_nickname=host_nickname,
        simulation=settings,
        selected_simulation_id=SettingsManager.get_selected_simulation_id(),
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
    settings = SettingsManager.update(SimulationSettingsDTO(**payload.model_dump()))

    notify("simulation_settings_update", settings.to_json())
    return settings
