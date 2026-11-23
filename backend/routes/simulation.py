from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend import config
from backend.core import repository
from backend.core.dto.base import NAME_MAX_LENGTH
from backend.core.dto.bot import RoomBotDTO
from backend.core.dto.goal import GoalProgressDTO
from backend.core.dto.house_report import HousePickDTO
from backend.core.dto.life import (
    LifeEventTypes,
    LifeFrequenciesDTO,
    LifeHistoryPageDTO,
    LifeStatusDTO,
    default_life_events,
)
from backend.core.dto.preparation import (
    FederationAnswerRequest,
    FederationOfferRequest,
    FundComanagerAnswerRequest,
    FundComanagerPreparationRequest,
    FundPreparationRequest,
    MyPreparationDTO,
    PreparationRequest,
    PreparationsDTO,
    PreparationViceAnswerRequest,
)
from backend.core.dto.preset import AppliedPresetDTO, PresetAppliedEventDTO
from backend.core.dto.profession import (
    OVERTIME_OFF,
    OVERTIME_ON,
    ProfessionStateDTO,
    SetOvertime,
)
from backend.core.dto.profession_page import ProfessionPageDTO
from backend.core.dto.simulation import (
    PriceImpactPointDTO,
    PriceImpactPreviewDTO,
    SavedSimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
    validate_funds,
    validate_goal,
    validate_government,
    validate_independence,
)
from backend.core.dto.strategy import (
    BotTickerDTO,
    StrategyInfoDTO,
    StrategyParamValue,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    AcademicStep,
    ComputerDifficulty,
    FundPreparationKind,
    GameType,
    InitialAccount,
    LifeHistoryCategory,
    LifeHistorySort,
    PlayerActivity,
    PlayerGrouping,
    PreparationKind,
    Profession,
    PropertySize,
    SalaryMode,
    SelicControl,
    TeamNaming,
    VictoryCriterion,
)
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.life_budget import LifeBudget
from backend.core.player_colors import MAX_PLAYERS
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.backtest import service as backtest_service
from backend.features.government.room_preparation import RoomPreparation
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    SimulationDeletedEventDTO,
    SimulationEndedEventDTO,
    SimulationSelectedEventDTO,
)
from backend.features.simulation.life_history import history_page
from backend.features.simulation.room_fund_preparation import RoomFundPreparation
from backend.features.simulation.saved_bots import saved_bot_infos, saved_bots
from backend.features.simulation.saved_simulation import describe, resume_point
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.strategy import catalog
from backend.features.strategy.bots import resolve_bot
from backend.features.variable_income.price_impact import (
    PREVIEW_VOLUME_SHARE,
    preview_curve,
)
from backend.routes.dependencies import ClientID, HostVerified

simulation_router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class SimulationRulesRequest(BaseModel):
    name: str = Field(min_length=1, max_length=NAME_MAX_LENGTH)
    start_date: date
    end_date: date
    starting_cash: Decimal = Field(gt=0)
    monthly_contribution: Decimal = Field(ge=0, default=Decimal(0))
    price_impact_enabled: bool = False
    price_impact_k: float = Field(ge=0)
    price_impact_decay_days: int = Field(ge=1)
    victory_criterion: VictoryCriterion = VictoryCriterion.SCORE
    game_type: GameType = GameType.CLASSIC
    goal_net_worth: Decimal = Field(gt=0)
    monthly_salary: Decimal = Field(ge=0, default=Decimal(0))
    monthly_expense: Decimal = Field(ge=0, default=Decimal(0))
    unexpected_per_year: int = Field(ge=0, le=52, default=0)
    life_events: LifeEventTypes = Field(default_factory=default_life_events)
    life_frequencies: LifeFrequenciesDTO = Field(default_factory=LifeFrequenciesDTO)
    withdrawal_rate: Decimal = Field(
        ge=Decimal("0.01"), le=Decimal("0.10"), default=Decimal("0.04")
    )
    inflation_adjusted: bool = False
    salary_mode: SalaryMode = SalaryMode.EQUAL
    player_grouping: PlayerGrouping = PlayerGrouping.INDIVIDUAL
    team_naming: TeamNaming = TeamNaming.COLOR
    show_equivalent_rate: bool = True
    show_maturity_projection: bool = True
    show_chart_hints: bool = True
    government_enabled: bool = False
    funds_enabled: bool = False
    fund_max_management_fee: Decimal = Field(
        default=Decimal("0.02"), ge=0, le=1, decimal_places=4
    )
    fund_max_performance_fee: Decimal = Field(
        default=Decimal("0.20"), ge=0, le=1, decimal_places=4
    )
    fund_grace_months: int = Field(default=12, ge=1, le=120)
    fund_min_market_share: Decimal = Field(
        default=Decimal("0.50"),
        ge=Decimal("0.10"),
        le=Decimal("0.90"),
        decimal_places=4,
    )
    first_election: date | None = None
    computer_difficulty: ComputerDifficulty = ComputerDifficulty.NORMAL
    poll_margin: bool = True
    initial_account: InitialAccount = InitialAccount.PLAYABLE
    selic_control: SelicControl = SelicControl.AUTONOMOUS

    @model_validator(mode="after")
    def validate_government_rules(self):
        validate_government(
            game_type=self.game_type,
            player_grouping=self.player_grouping,
            government_enabled=self.government_enabled,
            start_date=self.start_date,
            end_date=self.end_date,
            first_election=self.first_election,
            selic_control=self.selic_control,
        )
        return self

    @model_validator(mode="after")
    def validate_fund_rules(self):
        validate_funds(
            game_type=self.game_type,
            funds_enabled=self.funds_enabled,
        )
        return self

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self

    @model_validator(mode="after")
    def validate_goal(self):
        validate_goal(
            game_type=self.game_type,
            goal_net_worth=self.goal_net_worth,
            starting_cash=self.starting_cash,
        )
        return self

    @model_validator(mode="after")
    def validate_life(self):
        validate_independence(
            game_type=self.game_type,
            monthly_salary=self.monthly_salary,
            monthly_expense=self.monthly_expense,
            withdrawal_rate=self.withdrawal_rate,
            starting_cash=self.starting_cash,
        )
        return self


def notify_settings_changed(settings: SimulationSettingsDTO) -> None:
    """Avisa a sala das regras novas e de qual preset elas vêm (ou o que mudou nele)."""
    notify("simulation_settings_update", settings.to_json())
    notify_preset_changed()


def notify_preset_changed() -> None:
    applied = SettingsManager.applied_preset()
    notify("preset_applied_update", PresetAppliedEventDTO(applied=applied).to_json())


class CreateSimulationRequest(SimulationRulesRequest):
    pass


class SelectSimulationRequest(BaseModel):
    id: int


class PlayerColorRequest(BaseModel):
    color: str


class PlayerTeamRequest(BaseModel):
    team: int


class OvertimeRequest(BaseModel):
    enabled: bool


class ExchangeLockRequest(BaseModel):
    # A fração da receita exportada que a trava cobre (0.5 = metade) e o prazo em meses
    share: Decimal
    months: int


class ExportMixRequest(BaseModel):
    # A fração da receita que é exportada (1 = tudo)
    share: Decimal


class FreelancerPriceRequest(BaseModel):
    # O preço por atendimento, em reais
    price: Decimal


class ReinvestShareRequest(BaseModel):
    # A fração do lucro que volta para a empresa (1 = tudo)
    share: Decimal


class CapitalSaleRequest(BaseModel):
    # A fração do capital da empresa que a venda tira (1 = tudo)
    share: Decimal


class BuyPropertyRequest(BaseModel):
    # O tamanho da oferta do mês que a compra leva
    size: PropertySize


class SellPropertyRequest(BaseModel):
    # O imóvel da carteira do Locador que entra em venda
    property_id: int


class EnrollStepRequest(BaseModel):
    # O degrau da escada acadêmica; só o seguinte ao último concluído é aceito
    step: AcademicStep


class PensionAmountRequest(BaseModel):
    # O valor do saldo da previdência que a ação usa, em reais
    amount: Decimal


class PlayerProfessionRequest(BaseModel):
    profession: Profession
    # Sigla do partido; obrigatória para o Comissionado e ignorada nas demais profissões
    party: str | None = None


class UpdateSettingsRequest(SimulationRulesRequest):
    pass


class JoinMatchRequest(BaseModel):
    color: str
    # Obrigatória quando a partida é em equipes
    team: int | None = None
    # Obrigatória quando a partida é com profissões
    profession: Profession | None = None
    # Obrigatória para o Comissionado: a sigla de um partido da partida
    party: str | None = None


class HeirCapitalDTO(BaseModel):
    # Só sai em respostas: o schema de saída traz todos os campos como obrigatórios
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    # O caixa com que o Herdeiro entra: o da sala mais a herança que cobre os salários até o fim
    starting_capital: Decimal


class PlayerNickname(BaseModel):
    # Só sai em respostas: o schema de saída traz todos os campos como obrigatórios
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    nickname: str
    # Chave da paleta de jogadores (chart-N)
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes ou enquanto não escolheu
    team: int | None = None
    # Profissão no viver de renda com profissões; nula nos outros modos
    profession: Profession | None = None
    # Sigla do partido do Comissionado; nula nas outras profissões
    party: str | None = None
    # O que o jogador está fazendo na sala; só a lista da sala preenche, nulo é "Online"
    activity: PlayerActivity | None = None
    # Presente quando o jogador é um bot: a estratégia que ele joga
    bot: RoomBotDTO | None = None


class RoomBotRequest(BaseModel):
    # Nome do bot na sala; ao configurar, o novo nome (o atual vai na rota)
    nickname: str = Field(min_length=1, max_length=NAME_MAX_LENGTH)
    strategy_key: str
    # Os parâmetros que faltarem ficam no padrão do catálogo
    params: dict[str, StrategyParamValue] = Field(default_factory=dict)
    # Sem cor, o bot fica com a próxima livre (ao configurar, com a que já tem)
    color: str | None = None
    # Índice da equipe (1 a 10); só vale no modo em equipes
    team: int | None = None
    # Profissão do bot em sala de profissões; sem ela, é sorteada (ao configurar, fica a que tem)
    profession: Profession | None = None


class RoomBotsRequest(BaseModel):
    # Cada bot fica com a próxima cor livre e sem equipe: `color` e `team` dos itens não valem aqui
    bots: list[RoomBotRequest] = Field(min_length=1, max_length=MAX_PLAYERS)


class SimulationSettingsResponse(BaseModel):
    is_host: bool
    host_nickname: str
    simulation: SimulationSettingsDTO
    # Partida salva que o host escolheu para continuar; None quando é partida nova
    selected_simulation_id: int | None
    # Quem jogou a partida selecionada, com a cor guardada: presentes ou ausentes
    selected_players: list[PlayerNickname]
    # O preset de onde vieram as regras da nova partida; None quando foram montadas à mão
    applied_preset: AppliedPresetDTO | None


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
    if SimulationManager.has_backtest():
        return SimulationStatusResponse(
            active=False, simulation=None, backtest=backtest_service.status().progress
        )
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
    description="Escolhe a simulação salva a continuar. As cores e as equipes da sala passam a ser as guardadas nela. Apenas o host pode executar.",
)
def select_simulation(payload: SelectSimulationRequest, _: HostVerified):
    """
    Seleciona a simulação salva que o host vai continuar.
    """
    if SimulationManager.has_active_simulation():
        raise ConflictError("Já existe uma partida em andamento.")
    if SimulationManager.has_backtest():
        raise ConflictError("Há um backtest em andamento.")
    selected = repository.simulation.get_simulation(payload.id)
    if selected is None:
        raise NotFoundError("Simulação não encontrada.")
    if selected.is_backtest:
        raise ConflictError("Backtest não se continua: rode de novo.")

    UserManager.apply_saved_colors(
        repository.simulation_player.colors(payload.id),
        repository.simulation_player.teams(payload.id),
        saved_bots(payload.id),
        repository.simulation_player.professions(payload.id),
        repository.simulation_player.parties(payload.id),
    )
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


@simulation_router.delete(
    "/settings",
    response_model=SimulationSettingsDTO,
    summary="Restaurar configurações da simulação",
    description="Apaga as regras lembradas da próxima partida e volta aos padrões do config.toml. Recusa com 409 enquanto uma partida salva está selecionada. Apenas o host pode executar.",
)
def restore_simulation_settings(_: HostVerified):
    """Volta a sala para as regras de fábrica da próxima partida."""
    if SettingsManager.get_selected_simulation_id() is not None:
        raise ConflictError(
            "As regras de uma partida salva não mudam. Remova a seleção para restaurar as de uma nova partida."
        )

    settings = SettingsManager.restore_defaults()
    notify_settings_changed(settings)
    return settings


@simulation_router.delete(
    "/{simulation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir simulação salva",
    description="Apaga a partida salva e tudo o que ela guarda; não dá para desfazer. Recusa a partida em andamento e a selecionada no lobby. Apenas o host pode executar.",
)
def delete_simulation(simulation_id: int, _: HostVerified):
    """
    Exclui uma simulação salva e avisa a sala para atualizar a lista.
    """
    if (
        SimulationManager.has_running_simulation()
        and SimulationManager.get_active_simulation_id() == simulation_id
    ):
        raise ConflictError("Esta partida está em andamento.")
    if SettingsManager.get_selected_simulation_id() == simulation_id:
        raise ConflictError("Esta partida está selecionada no lobby.")
    if not repository.simulation.delete(simulation_id):
        raise NotFoundError("Simulação não encontrada.")

    notify(
        "simulation_deleted",
        SimulationDeletedEventDTO(simulation_id=simulation_id).to_json(),
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
        describe(
            s,
            nickname,
            UserManager.room_overflow(repository.simulation_player.colors(s.id)),
        )
        for s in repository.simulation.list_simulations(search)
    ]


@simulation_router.get(
    "/price-impact-preview",
    summary="Prévia do impacto de preço",
    description="Quanto uma compra de 10% do volume médio diário move o preço no pregão seguinte e como o efeito some até voltar ao histórico.",
)
def price_impact_preview(
    k: Annotated[float, Query(ge=0)], decay_days: Annotated[int, Query(ge=1, le=250)]
) -> PriceImpactPreviewDTO:
    curve = preview_curve(k, decay_days)
    return PriceImpactPreviewDTO(
        volume_share=PREVIEW_VOLUME_SHARE,
        first_day_impact=curve[0],
        curve=[
            PriceImpactPointDTO(day=age + 1, impact=value)
            for age, value in enumerate(curve)
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
    teams = UserManager.room_teams()
    professions = UserManager.room_professions()
    parties = UserManager.room_parties()
    activities = UserManager.room_activities()
    return [
        PlayerNickname(
            nickname=p.nickname,
            color=colors[p.id],
            team=teams.get(p.id),
            profession=professions.get(p.id),
            party=parties.get(p.id),
            activity=activities.get(p.id),
            bot=UserManager.room_bot(p),
        )
        for p in UserManager.list_active_players()
        if p.id in colors
    ]


@simulation_router.delete(
    "/players/{nickname}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover um jogador da sala",
    description="Tira a pessoa da sala no lobby: a vaga e a cor ficam livres e a página dela encerra a sessão com o aviso de que o host a removeu. Recusa com 409 o host e a partida em andamento; com 404, quem não está na sala (para bots, use a rota de bots). Apenas o host pode executar.",
)
def remove_player(nickname: str, _: HostVerified):
    """
    Remove uma pessoa da sala.
    """
    removed = next(
        (p for p in UserManager.list_active_players() if p.nickname == nickname), None
    )
    UserManager.remove_player(nickname)
    if removed is not None:
        RoomPreparation.drop(removed.id)
        RoomFundPreparation.drop(removed.id)
        _notify_preparations()


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


@simulation_router.put(
    "/players/me/team",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Escolher a equipe do jogador",
    description="Escolhe a equipe do jogador na sala, quando a partida é em equipes. Equipe não tem dono nem limite de membros; quem já jogou a partida salva selecionada não troca.",
)
def set_player_team(payload: PlayerTeamRequest, client_id: ClientID):
    """
    Escolhe a equipe do jogador na sala.
    """
    UserManager.set_team(client_id, payload.team)


@simulation_router.put(
    "/players/me/profession",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Escolher a profissão do jogador",
    description="Escolhe a profissão do jogador na sala, quando o viver de renda joga com profissões. Profissão não tem dono nem limite de jogadores; responde 409 fora desse modo, com a partida em andamento e para quem já jogou a partida salva selecionada.",
)
def set_player_profession(payload: PlayerProfessionRequest, client_id: ClientID):
    """
    Escolhe a profissão do jogador na sala.
    """
    UserManager.set_profession(
        client_id,
        payload.profession,
        payload.party,
        RoomPreparation.party_abbrs(_room_humans()),
    )


def _room_humans() -> list[UserDTO]:
    return [p for p in UserManager.list_active_players() if not p.is_bot]


def _preparations() -> PreparationsDTO:
    """A preparação do partido com as gestoras e os conflitos de ambos."""
    humans = _room_humans()
    return RoomFundPreparation.apply(RoomPreparation.snapshot(humans), humans)


def _notify_preparations() -> PreparationsDTO:
    snapshot = _preparations()
    notify("preparations_update", snapshot.to_json())
    return snapshot


@simulation_router.get(
    "/heir-capital",
    response_model=HeirCapitalDTO,
    summary="Capital inicial do Herdeiro",
    description="O caixa com que o Herdeiro entra na sala: o da sala mais a herança, pelas regras da partida salva selecionada ou, sem seleção, pelas da nova partida.",
)
def get_heir_capital():
    """
    Capital inicial do Herdeiro pelas regras que valem para a sala.
    """
    selected_id = SettingsManager.get_selected_simulation_id()
    summary = (
        repository.simulation.get_simulation(selected_id)
        if selected_id is not None
        else None
    )
    rules = summary or SettingsManager.get()
    # Na partida salva o jogador novo entra no último dia processado
    joined = (resume_point(summary.id) if summary else None) or rules.start_date
    capital = (
        LifeBudget.of(rules)
        .for_profession(Profession.HEIR)
        .starting_capital(rules.starting_cash, joined, rules.end_date)
    )
    return HeirCapitalDTO(starting_capital=capital)


@simulation_router.get(
    "/preparations",
    response_model=PreparationsDTO,
    summary="Preparação dos jogadores no lobby",
    description="O que cada jogador da sala preparou para a partida (fundar partido, filiar-se, chapa e vice, e fundar gestora com a expansão Gestoras ligada), os conflitos de sigla, nome e cor e o motivo da trava, quando há.",
)
def get_preparations():
    """
    Lista a preparação da sala.
    """
    return _preparations()


@simulation_router.get(
    "/players/me/preparation",
    response_model=MyPreparationDTO,
    summary="O que da preparação só o jogador vê",
    description="O convite de vice que o jogador recebeu e o que ele enviou, enquanto sem resposta, e o partido em que ele entrou e que saiu da preparação. Quem fundou na última sala e chega a uma sala nova volta fundando o Meu partido.",
)
def get_my_preparation(client_id: ClientID):
    """
    Lê a preparação privada do jogador, recriando a fundação da última sala.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    humans = _room_humans()
    identity = repository.settings.get_my_party(user.id)
    founds = (
        repository.settings.get_preparation_choice(user.id) is PreparationKind.FOUND
    )
    fund = repository.settings.get_my_fund(user.id)
    fund_founds = (
        repository.settings.get_fund_choice(user.id) is FundPreparationKind.FOUND
    )
    restored_party = (
        founds
        and identity is not None
        and RoomPreparation.restore(user, humans, identity)
    )
    restored_fund = (
        fund_founds and fund is not None and RoomFundPreparation.restore(user, fund)
    )
    if restored_party or restored_fund:
        _notify_preparations()
    return RoomFundPreparation.with_mine(
        RoomPreparation.mine(user, humans), user, humans
    )


@simulation_router.put(
    "/players/me/preparation",
    response_model=PreparationsDTO,
    summary="Preparar a campanha do jogador",
    description="Escolhe o que o jogador faz no começo da partida: fundar o Meu partido (com a chapa), convidar ou retirar o vice da chapa que fundou, entrar no partido que outro jogador preparou ou nada. Salvar a fundação não convida ninguém. Só vale em partida nova com a expansão ligada; recusa com 409 fora disso.",
)
def set_player_preparation(payload: PreparationRequest, client_id: ClientID):
    """
    Troca a preparação do jogador na sala.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    identity = repository.settings.get_my_party(user.id)
    RoomPreparation.choose(
        user,
        payload.kind,
        _room_humans(),
        identity=identity,
        founder=payload.founder,
        candidate=payload.candidate,
        vice=payload.vice,
    )
    # Entrar no partido de outro volta, na próxima sala, como sem partido; convidar ou retirar o vice mexe na chapa de quem já funda
    remembered = (
        PreparationKind.FOUND
        if payload.kind
        in (
            PreparationKind.FOUND,
            PreparationKind.INVITE_VICE,
            PreparationKind.WITHDRAW_VICE,
        )
        else PreparationKind.NONE
    )
    repository.settings.set_preparation_choice(user.id, remembered)
    return _notify_preparations()


@simulation_router.put(
    "/players/me/fund-preparation",
    response_model=PreparationsDTO,
    summary="Preparar a gestora do jogador",
    description="Escolhe se o jogador funda a Minha gestora no 1º dia da partida ou fica sem gestora; sem escolha salva, é sem gestora. Fundar exige a Minha gestora salva no perfil. Recusa com 409 com a partida em andamento ou salva selecionada; com a expansão Gestoras desligada a escolha fica guardada e é ignorada.",
)
def set_player_fund_preparation(payload: FundPreparationRequest, client_id: ClientID):
    """
    Troca a escolha da gestora do jogador na sala.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    RoomFundPreparation.choose(
        user, payload.kind, repository.settings.get_my_fund(user.id)
    )
    repository.settings.set_fund_choice(user.id, payload.kind)
    return _notify_preparations()


@simulation_router.put(
    "/players/me/fund-preparation/comanagers",
    response_model=PreparationsDTO,
    summary="Convidar um co-gestor no lobby",
    description="Quem funda a gestora convida um jogador da sala a co-gestor, com a parte das taxas (fração entre 0 e 1). Sem `share`, retira o convite, tira o co-gestor que aceitou ou limpa a marca de recusa. A gestora aceita até 3 co-gestores, contando os convites sem resposta, e as partes deixam ao menos 1% ao principal; recusa com 409 acima do teto. Quem aceitou entra ativo na gestora no 1º dia da partida.",
)
def set_fund_comanager_preparation(
    payload: FundComanagerPreparationRequest, client_id: ClientID
):
    """
    Convida ou retira um co-gestor da gestora que o jogador funda.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    if payload.share is None:
        RoomFundPreparation.withdraw_comanager(user, _room_humans(), payload.nickname)
    else:
        RoomFundPreparation.invite_comanager(
            user, _room_humans(), payload.nickname, payload.share
        )
    return _notify_preparations()


@simulation_router.put(
    "/players/me/fund-preparation/comanagers/answer",
    response_model=PreparationsDTO,
    summary="Responder ao convite de co-gestão do lobby",
    description="O jogador convidado a co-gestor da gestora de um fundador (`owner`) aceita ou recusa. Aceitar uma gestora não recusa os convites das outras. Recusa com 404 se não há esse convite.",
)
def answer_fund_comanager_preparation(
    payload: FundComanagerAnswerRequest, client_id: ClientID
):
    """
    Aceita ou recusa o convite de co-gestão do lobby.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    RoomFundPreparation.answer_comanager(
        user, _room_humans(), payload.owner, payload.accept
    )
    return _notify_preparations()


@simulation_router.put(
    "/players/me/preparation/vice",
    response_model=PreparationsDTO,
    summary="Responder ao convite de vice",
    description="O jogador convidado para vice na chapa de um fundador (`owner`) aceita ou recusa. Aceitar recusa os outros convites abertos dele. Recusa com 404 se não há esse convite.",
)
def answer_preparation_vice(payload: PreparationViceAnswerRequest, client_id: ClientID):
    """
    Aceita ou recusa o convite de vice do lobby.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    RoomPreparation.answer_vice(user, _room_humans(), payload.owner, payload.accept)
    return _notify_preparations()


@simulation_router.put(
    "/players/me/preparation/federation",
    response_model=PreparationsDTO,
    summary="Propor federação no lobby",
    description="O fundador propõe federação ao fundador de outro partido preparado, nomeando a federação e o candidato da chapa. Sem `partner`, retira a proposta ou desfaz a federação combinada. Cada fundador envia uma proposta por vez e pode receber várias. Recusa com 409 se o proponente já tem proposta enviada ou um dos dois já tem federação combinada.",
)
def propose_preparation_federation(
    payload: FederationOfferRequest, client_id: ClientID
):
    """
    Propõe ou retira a federação do lobby.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    RoomPreparation.propose_federation(
        user, _room_humans(), payload.partner, payload.name, payload.candidate
    )
    return _notify_preparations()


@simulation_router.put(
    "/players/me/preparation/federation/answer",
    response_model=PreparationsDTO,
    summary="Responder à proposta de federação do lobby",
    description="O fundador convidado aceita ou recusa a federação que um fundador (`owner`) propôs. Aceitar derruba as outras propostas que envolvem um dos dois. Recusa com 404 se não há essa proposta.",
)
def answer_preparation_federation(
    payload: FederationAnswerRequest, client_id: ClientID
):
    """
    Aceita ou recusa a proposta de federação do lobby.
    """
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    RoomPreparation.answer_federation(
        user, _room_humans(), payload.owner, payload.accept
    )
    return _notify_preparations()


@simulation_router.post(
    "/teams/distribute",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Distribuir quem falta nas equipes",
    description="Põe cada jogador sem equipe na equipe com menos gente. Apenas o host pode executar.",
)
def distribute_teams(_: HostVerified):
    """
    Distribui os jogadores sem equipe.
    """
    UserManager.distribute_teams()


@simulation_router.get(
    "/match-players",
    response_model=list[PlayerNickname],
    summary="Listar jogadores da partida em andamento",
    description="Retorna todos que jogam a partida ativa, online ou não, cada um com a sua cor. Serve a quem chega e escolhe uma cor que sobrou.",
)
def get_match_players():
    """
    Lista os participantes da partida ativa.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    simulation_id = SimulationManager.get_active_simulation_id()
    colors = repository.simulation_player.colors(simulation_id)
    teams = repository.simulation_player.teams(simulation_id)
    uses_professions = (
        SimulationManager.get_active_simulation().settings.uses_professions
    )
    professions = repository.simulation_player.professions(simulation_id)
    parties = repository.simulation_player.parties(simulation_id)
    bots = saved_bot_infos(simulation_id)
    return [
        PlayerNickname(
            nickname=p.nickname,
            color=colors[p.id],
            team=teams.get(p.id),
            profession=professions.get(p.id, Profession.CLT)
            if uses_professions
            else None,
            party=parties.get(p.id),
            bot=bots.get(p.id),
        )
        for p in repository.simulation_player.participants(simulation_id)
    ]


@simulation_router.get(
    "/match-parties",
    response_model=list[str],
    summary="Listar os partidos da partida em andamento",
    description="Retorna a sigla de cada partido da partida ativa, em ordem alfabética; vazia sem a expansão Governo & Política. Serve a quem chega e escolhe o partido do Comissionado.",
)
def get_match_parties():
    """
    Lista as siglas dos partidos da partida ativa.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    return sorted(SimulationManager.get_active_simulation().party_abbrs())


@simulation_router.get(
    "/bots/strategies",
    response_model=list[StrategyInfoDTO],
    summary="Listar as estratégias para os bots",
    description="As estratégias do app com os parâmetros, a faixa de cada um e o padrão calculado para a data de início (a informada em `start_date` ou, sem ela, a das regras do lobby), e os nomes sugeridos para o bot. A estratégia que exige uma expansão só vem quando a sala a tem: `funds_enabled` (Gestoras) e `government_enabled` (Governo) informados mandam (o backtest passa falso nos dois), e sem eles valem as regras da sala. Serve também à preparação de cada jogador no lobby.",
)
def list_bot_strategies(
    start_date: date | None = None,
    funds_enabled: bool | None = None,
    government_enabled: bool | None = None,
):
    """
    Lista as estratégias que um bot pode jogar.
    """
    return catalog.infos(
        start_date or SettingsManager.get().start_date,
        None,
        catalog.known_tickers(),
        funds_enabled=SettingsManager.effective_funds_enabled()
        if funds_enabled is None
        else funds_enabled,
        government_enabled=SettingsManager.effective_government_enabled()
        if government_enabled is None
        else government_enabled,
    )


@simulation_router.get(
    "/bots/tickers",
    response_model=list[BotTickerDTO],
    summary="Listar as ações que um bot pode operar",
    description="Os tickers cadastrados com o nome da empresa, em ordem alfabética de ticker, para escolher as ações de uma estratégia antes de a partida começar.",
)
def list_bot_tickers():
    """
    Lista as ações que um bot da sala pode operar.
    """
    return [
        BotTickerDTO(ticker=stock.ticker, name=stock.name)
        for stock in repository.stock.get_stocks()
    ]


@simulation_router.post(
    "/bots",
    status_code=status.HTTP_201_CREATED,
    response_model=PlayerNickname,
    summary="Adicionar um bot à sala",
    description="Cria um jogador sem pessoa por trás, com a estratégia, a cor e a equipe escolhidas, e o põe na primeira vaga livre. Recusa com 409 o nome repetido na sala, a cor com dono e a partida salva selecionada; com 423, a sala cheia. Apenas o host pode executar.",
)
def add_bot(payload: RoomBotRequest, _: HostVerified):
    """
    Adiciona um bot à sala.
    """
    bot = UserManager.add_bot(
        payload.nickname,
        resolve_bot(
            payload.strategy_key, payload.params, profession=payload.profession
        ),
        payload.color,
        payload.team,
    )
    return _room_player(bot)


@simulation_router.post(
    "/bots/batch",
    status_code=status.HTTP_201_CREATED,
    response_model=list[PlayerNickname],
    summary="Adicionar vários bots à sala",
    description="Cria de uma vez um bot por item, cada um com a próxima cor livre e sem equipe. Ou entram todos ou nenhum: recusa com 409 o nome repetido na sala ou no próprio lote e a partida salva selecionada; com 423, o lote que passa das vagas livres. Apenas o host pode executar.",
)
def add_bots(payload: RoomBotsRequest, _: HostVerified):
    """
    Adiciona vários bots à sala.
    """
    bots = UserManager.add_bots(
        [
            (
                item.nickname,
                resolve_bot(item.strategy_key, item.params, profession=item.profession),
            )
            for item in payload.bots
        ]
    )
    return [_room_player(bot) for bot in bots]


@simulation_router.put(
    "/bots/{nickname}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Configurar um bot da sala",
    description="Troca a estratégia, os parâmetros, o nome, a cor e a equipe do bot. Recusa com 409 o bot da partida salva selecionada e a partida em andamento. Apenas o host pode executar.",
)
def update_bot(nickname: str, payload: RoomBotRequest, _: HostVerified):
    """
    Configura um bot da sala.
    """
    UserManager.update_bot(
        nickname,
        payload.nickname,
        resolve_bot(
            payload.strategy_key, payload.params, profession=payload.profession
        ),
        payload.color,
        payload.team,
    )


@simulation_router.delete(
    "/bots/{nickname}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover um bot da sala",
    description="Tira o bot da sala: a vaga e a cor ficam livres. Recusa com 409 o bot da partida salva selecionada e a partida em andamento. Apenas o host pode executar.",
)
def remove_bot(nickname: str, _: HostVerified):
    """
    Remove um bot da sala.
    """
    UserManager.remove_bot(nickname)


def _room_player(player: UserDTO) -> PlayerNickname:
    """O jogador na sala, como a lista o mostra."""
    return PlayerNickname(
        nickname=player.nickname,
        color=UserManager.room_colors()[player.id],
        team=UserManager.room_teams().get(player.id),
        profession=UserManager.room_professions().get(player.id),
        party=UserManager.room_parties().get(player.id),
        activity=UserManager.room_activities().get(player.id),
        bot=UserManager.room_bot(player),
    )


@simulation_router.get(
    "/goal-progress",
    response_model=GoalProgressDTO,
    summary="Progresso da corrida à meta",
    description="A meta e o patrimônio de cada jogador no último pregão simulado, para a trilha da corrida. Depois disso, o evento `goal_progress_update` traz cada dia. Só existe fora da partida Clássica.",
)
def get_goal_progress():
    """
    Retorna onde cada jogador está na meta.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    progress = SimulationManager.get_active_simulation().get_goal_progress()
    if progress is None:
        raise ConflictError("A partida em andamento não tem meta.")
    return progress


@simulation_router.get(
    "/life",
    response_model=LifeStatusDTO,
    summary="Vida financeira do jogador",
    description="No viver de renda: o salário e a despesa do mês, as demissões que tiram salário, a meta do dia, o juro que o caixa negativo paga por pregão e quantos meses de despesa o caixa cobre.",
)
def get_life_status(client_id: ClientID):
    """
    Retorna a vida financeira de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    status_ = SimulationManager.get_active_simulation().get_life_status(client_id)
    if status_ is None:
        raise ConflictError("A partida em andamento não é de viver de renda.")
    return status_


@simulation_router.get(
    "/profession-state",
    response_model=ProfessionStateDTO,
    summary="Estado da mecânica da profissão do jogador",
    description="A profissão de quem pede na partida e o estado da mecânica dela. A profissão sem mecânica devolve o estado vazio.",
)
def get_profession_state(client_id: ClientID):
    """
    Retorna o estado da mecânica de profissão de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    return SimulationManager.get_active_simulation().get_profession_state(client_id)


@simulation_router.get(
    "/profession",
    response_model=ProfessionPageDTO,
    summary="Página Profissão do jogador",
    description="O que a página Profissão mostra: o cabeçalho com a renda do mês, o reajuste acima do IPCA, a chance de demissão e o imprevisto de saúde; os indicadores que mexem na renda, com os 12 últimos meses; e o bloco da mecânica da profissão (FGTS e hora extra do CLT, margem do consignado do Servidor, CDBs da casa do Bancário, herança, partido e comissões). Responde 409 sem partida ou com salário igual para todos.",
)
def get_profession_page(client_id: ClientID):
    """
    Retorna a página Profissão de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    return SimulationManager.get_active_simulation().get_profession_page(client_id)


@simulation_router.get(
    "/house-picks",
    response_model=list[HousePickDTO],
    summary="Ações do relatório da casa do Corretor",
    description="A ação e o lado (compra ou venda) de cada recomendação do relatório vigente da casa, para o selo na Renda variável. Só o Corretor vê: para as demais profissões, e antes do primeiro relatório, a lista vem vazia. Não traz preço-alvo nem preço futuro. Responde 409 sem partida.",
)
def get_house_picks(client_id: ClientID):
    """
    Retorna as ações do relatório vigente da casa para quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    return SimulationManager.get_active_simulation().get_house_picks(client_id)


@simulation_router.post(
    "/overtime",
    response_model=ProfessionStateDTO,
    summary="Ligar ou desligar a hora extra do CLT",
    description="Liga (`enabled: true`) ou desliga a hora extra de quem é CLT na partida com profissões: ligada, a renda bruta sobe 25% e o imprevisto de saúde custa o dobro. Só existe com o PIB de 12 meses a partir de zero: ligar com PIB negativo responde 409, e a hora extra ligada desliga sozinha na virada do mês em que o PIB fica negativo. Responde 409 para outra profissão e para o estado que já é o pedido.",
)
def set_overtime(payload: OvertimeRequest, client_id: ClientID):
    """
    Liga ou desliga a hora extra de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.apply_profession_action(
        user, SetOvertime(kind=OVERTIME_ON if payload.enabled else OVERTIME_OFF)
    )
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/exchange-lock",
    response_model=ProfessionStateDTO,
    summary="Contratar a trava de câmbio do Exportador",
    description="Contrata um câmbio futuro para `share` (de 1% a 100%) da receita exportada por `months` (6 ou 12) meses: a parte travada recebe pelo dólar do dia corrigido pelo CDI contra os Fed Funds, suba ou caia o dólar. Vale a partir do próximo pagamento, não se desfaz antes do vencimento e não ajusta o caixa. Responde 409 para outra profissão, para fração ou prazo fora do permitido e com outra trava ativa.",
)
def lock_exchange(payload: ExchangeLockRequest, client_id: ClientID):
    """
    Contrata a trava de câmbio de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.lock_exchange(user, payload.share, payload.months)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/export-mix",
    response_model=ProfessionStateDTO,
    summary="Mudar o mix de exportação do Exportador",
    description="Muda a fração exportada da receita (de 0% a 100%): a parte exportada segue o dólar e a vendida no Brasil segue o PIB. Vale a partir do próximo pagamento. A mudança é livre na primeira vez e depois só no 1º dia do trimestre seguinte: antes disso responde 409, assim como para outra profissão e para a fração que já é a atual.",
)
def set_export_mix(payload: ExportMixRequest, client_id: ClientID):
    """
    Muda o mix de exportação de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.set_export_mix(user, payload.share)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/price",
    response_model=ProfessionStateDTO,
    summary="Salvar o preço do Autônomo",
    description="Salva o preço por atendimento, em reais, de 20% abaixo a 50% acima da referência do mercado do dia. Vale a partir do próximo pagamento. O primeiro ajuste é livre e depois o preço muda uma vez por mês, no 1º dia do mês seguinte ao último ajuste: antes disso responde 409, assim como para o preço fora da faixa e para outra profissão.",
)
def set_price(payload: FreelancerPriceRequest, client_id: ClientID):
    """
    Salva o preço de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.set_price(user, payload.price)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/reinvest-share",
    response_model=ProfessionStateDTO,
    summary="Salvar a fração reinvestida do Empreendedor",
    description="Salva a fração do lucro do mês que volta para a empresa e vira capital, de 0 a 1 em passos de 0,01. Vale a partir do próximo pagamento e pode mudar quando quiser. Responde 409 para a fração fora da faixa e para outra profissão.",
)
def set_reinvest_share(payload: ReinvestShareRequest, client_id: ClientID):
    """
    Salva a fração reinvestida de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.set_reinvest_share(user, payload.share)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/sell-capital",
    response_model=ProfessionStateDTO,
    summary="Vender parte da empresa do Empreendedor",
    description="Vende 10%, 25%, 50% ou 100% do capital da empresa a qualquer momento: a parte vendida sai do capital e entra no caixa com o desconto de 20%. Responde 409 para a fração fora dessas opções, para a empresa sem capital e para outra profissão.",
)
def sell_capital(payload: CapitalSaleRequest, client_id: ClientID):
    """
    Vende a fração do capital de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.sell_capital(user, payload.share)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/buy-property",
    response_model=ProfessionStateDTO,
    summary="Comprar a oferta do mês de imóvel do Locador",
    description="Compra a oferta do mês do tamanho pedido pelo preço do IVG-R do dia: o caixa paga o preço mais 5% de ITBI e corretagem e o imóvel entra alugado a 0,5% do preço ao mês. Cada oferta se compra uma vez. Responde 409 para o caixa que não cobre a compra, para a oferta já comprada e para outra profissão.",
)
def buy_property(payload: BuyPropertyRequest, client_id: ClientID):
    """
    Compra o imóvel da oferta de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.buy_property(user, payload.size)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/sell-property",
    response_model=ProfessionStateDTO,
    summary="Vender um imóvel do Locador",
    description="Põe o imóvel à venda: a venda conclui em 1 mês, pelo valor do dia da conclusão menos 5% de ITBI e corretagem, e até lá o imóvel segue rendendo. Não se desfaz. Responde 404 para o imóvel que não é do jogador, 409 para o imóvel já à venda e para outra profissão.",
)
def sell_property(payload: SellPropertyRequest, client_id: ClientID):
    """
    Põe à venda o imóvel de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.sell_property(user, payload.property_id)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/convert-pension",
    response_model=ProfessionStateDTO,
    summary="Converter parte da previdência do Aposentado em renda",
    description="Converte parte do saldo da previdência em renda vitalícia: o valor sai do saldo e do patrimônio e passa a render todo mês, para sempre, ao juro real do dia. Responde 409 para o valor fora de R$ 0,01 até o saldo, para o juro real zerado ou negativo e para outra profissão.",
)
def convert_pension(payload: PensionAmountRequest, client_id: ClientID):
    """
    Converte em renda a parte da previdência de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.convert_pension(user, payload.amount)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/redeem-pension",
    response_model=ProfessionStateDTO,
    summary="Resgatar parte da previdência do Aposentado",
    description="Resgata parte do saldo da previdência: o valor sai do saldo e cai no caixa depois do IR regressivo da faixa do tempo no plano (35% até 2 anos, 10% depois de 10). Responde 409 para o valor fora de R$ 0,01 até o saldo e para outra profissão.",
)
def redeem_pension(payload: PensionAmountRequest, client_id: ClientID):
    """
    Resgata a parte da previdência de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.redeem_pension(user, payload.amount)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/enroll-step",
    response_model=ProfessionStateDTO,
    summary="Matricular o Recém-formado num degrau da escada acadêmica",
    description="Matricula o Recém-formado na especialização (1 ano, trabalha junto e paga mensalidade de 10% da renda base), no mestrado (2 anos, bolsa de 35% da renda base no lugar do salário) ou no doutorado (4 anos, bolsa de 50%). Os degraus se sobem na ordem, um por vez: cada um exige o anterior concluído. Matricular com o desemprego acima do neutro fixa, até o degrau acabar, a mensalidade 30% menor e a bolsa 20% maior. Na virada do mês em que o degrau conclui, a curva de carreira ganha um trecho novo até o múltiplo do degrau. Responde 409 para a graduação, para o degrau fora de ordem, para quem já está matriculado e para outra profissão.",
)
def enroll_step(payload: EnrollStepRequest, client_id: ClientID):
    """
    Matricula no degrau quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.enroll_step(user, payload.step)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/leave-home",
    response_model=ProfessionStateDTO,
    summary="Sair da casa dos pais",
    description="O Recém-formado sai da casa dos pais: a despesa paga deixa de ter o desconto de 40% dos 3 primeiros anos na profissão e volta ao normal, sem volta. Responde 409 para quem já saiu, para quem passou dos 3 anos (o desconto já acabou sozinho) e para outra profissão.",
)
def leave_home(client_id: ClientID):
    """
    Tira da casa dos pais quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.leave_home(user)
    return simulation.get_profession_state(client_id)


@simulation_router.post(
    "/enroll-course",
    response_model=ProfessionStateDTO,
    summary="Matricular o Auxílio no curso técnico",
    description="Matricula quem vive do Auxílio no curso técnico de 12 meses: a renda do bico cai pela metade e o benefício fica inteiro. Na virada do mês em que o curso conclui, o jogador vira CLT, perde a tarifa social e o benefício, e o saldo do Pé-de-Meia cai inteiro no caixa. Responde 409 para quem já está matriculado e para outra profissão.",
)
def enroll_course(client_id: ClientID):
    """
    Matricula no curso técnico quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    user = UserManager.get_user(client_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado.")
    simulation = SimulationManager.get_active_simulation()
    simulation.enroll_course(user)
    return simulation.get_profession_state(client_id)


@simulation_router.get(
    "/life-history",
    response_model=LifeHistoryPageDTO,
    summary="Histórico do viver de renda",
    description="Imprevistos, demissões, entrada e saída do cheque especial, o juro de cada mês e as mudanças de salário, despesa e juro com a origem na economia da partida, com o caixa do jogador depois de cada um. Paginado: `offset` e `limit` (6 por padrão), filtrável por categoria e ordenável por `sort_by` e `sort_direction`. O padrão é data decrescente; a ordenação considera todo o histórico antes da paginação.",
)
def get_life_history(
    client_id: ClientID,
    category: LifeHistoryCategory | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 6,
    sort_by: LifeHistorySort = LifeHistorySort.DATE,
    sort_direction: Literal["asc", "desc"] = "desc",
):
    """
    Retorna uma página do histórico de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    rows = SimulationManager.get_active_simulation().get_life_history(client_id)
    return history_page(rows, category, offset, limit, sort_by, sort_direction)


@simulation_router.post(
    "/join",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Entrar na partida em andamento",
    description="Quem chegou depois do início escolhe uma cor livre (e a equipe, em partida em equipes) e passa a jogar: recebe o depósito inicial no dia corrente e entra nas estatísticas e no ranking. Se a cor já tem dono, a resposta é 409.",
)
def join_match(payload: JoinMatchRequest, client_id: ClientID):
    """
    Entra na partida em andamento com a cor escolhida.
    """
    UserManager.join_match(
        client_id, payload.color, payload.team, payload.profession, payload.party
    )


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
    selected_id = SettingsManager.get_selected_simulation_id()
    selected_players = []
    if selected_id is not None:
        colors = repository.simulation_player.colors(selected_id)
        teams = repository.simulation_player.teams(selected_id)
        bots = saved_bot_infos(selected_id)
        selected_players = [
            PlayerNickname(
                nickname=p.nickname,
                color=colors[p.id],
                team=teams.get(p.id),
                bot=bots.get(p.id),
            )
            for p in repository.simulation_player.participants(selected_id)
        ]
    return SimulationSettingsResponse(
        is_host=user.nickname == host_nickname,
        host_nickname=host_nickname,
        simulation=settings,
        selected_simulation_id=selected_id,
        selected_players=selected_players,
        applied_preset=SettingsManager.applied_preset(),
    )


@simulation_router.put(
    "/settings",
    response_model=SimulationSettingsDTO,
    summary="Atualizar configurações da simulação",
    description="Atualiza os parâmetros da simulação (datas, capital, contribuição mensal). Recusa com 409 enquanto uma partida salva está selecionada: continuar usa as regras gravadas nela. Apenas o host pode executar.",
)
def update_simulation_settings(payload: UpdateSettingsRequest, _: HostVerified):
    """
    Atualiza as configurações da simulação.
    """
    # As regras de uma partida salva são as gravadas nela: com seleção ativa elas não mudam
    if SettingsManager.get_selected_simulation_id() is not None:
        raise ConflictError(
            "As regras de uma partida salva não mudam. Remova a seleção para editar as de uma nova partida."
        )
    regrouped = SettingsManager.get().player_grouping != payload.player_grouping
    settings = SettingsManager.update(SimulationSettingsDTO(**payload.model_dump()))
    if regrouped:
        UserManager.reset_teams()

    notify_settings_changed(settings)
    return settings
