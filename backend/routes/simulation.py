from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field, model_validator

from backend import config
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.bot import RoomBotDTO
from backend.core.dto.goal import GoalProgressDTO
from backend.core.dto.life import LifeHistoryPageDTO, LifeStatusDTO
from backend.core.dto.simulation import (
    PriceImpactPointDTO,
    PriceImpactPreviewDTO,
    SavedSimulationDTO,
    SimulationSettingsDTO,
    SimulationStatusResponse,
)
from backend.core.dto.strategy import StrategyInfoDTO, StrategyParamValue
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    GameType,
    LifeHistoryCategory,
    LifeHistorySort,
    PlayerActivity,
    PlayerGrouping,
    TeamNaming,
    VictoryCriterion,
)
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    SimulationDeletedEventDTO,
    SimulationEndedEventDTO,
    SimulationSelectedEventDTO,
)
from backend.features.simulation.life_history import build_history, history_page
from backend.features.simulation.saved_bots import saved_bot_infos, saved_bots
from backend.features.simulation.saved_simulation import describe
from backend.features.simulation.simulation_loader import SimulationLoader
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.strategy import catalog
from backend.features.variable_income.price_impact import decay, impact

simulation_router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class SimulationRulesRequest(BaseModel):
    name: str
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
    withdrawal_rate: Decimal = Field(
        ge=Decimal("0.01"), le=Decimal("0.10"), default=Decimal("0.04")
    )
    inflation_adjusted: bool = False
    player_grouping: PlayerGrouping = PlayerGrouping.INDIVIDUAL
    team_naming: TeamNaming = TeamNaming.COLOR
    show_equivalent_rate: bool = True
    show_maturity_projection: bool = True

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self

    @model_validator(mode="after")
    def validate_goal(self):
        if (
            self.game_type is GameType.GOAL_RACE
            and self.goal_net_worth <= self.starting_cash
        ):
            raise ValueError("A meta precisa ser maior que o saldo inicial.")
        return self

    @model_validator(mode="after")
    def validate_life(self):
        if self.game_type is not GameType.FINANCIAL_INDEPENDENCE:
            return self
        if self.monthly_salary <= 0 or self.monthly_expense <= 0:
            raise ValueError("Salário e despesa mensais precisam ser maiores que zero.")
        goal = 12 * self.monthly_expense / self.withdrawal_rate
        if goal <= self.starting_cash:
            raise ValueError(
                "A meta de independência (12 x a despesa ÷ a taxa de retirada) "
                "precisa ser maior que o saldo inicial."
            )
        return self


class CreateSimulationRequest(SimulationRulesRequest):
    pass


class SelectSimulationRequest(BaseModel):
    id: int


class PlayerColorRequest(BaseModel):
    color: str


class PlayerTeamRequest(BaseModel):
    team: int


class UpdateSettingsRequest(SimulationRulesRequest):
    pass


class JoinMatchRequest(BaseModel):
    color: str
    # Obrigatória quando a partida é em equipes
    team: int | None = None


class PlayerNickname(BaseModel):
    nickname: str
    # Chave da paleta (chart-1 a chart-10)
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes ou enquanto não escolheu
    team: int | None = None
    # O que o jogador está fazendo na sala; só a lista da sala preenche, nulo é "Online"
    activity: PlayerActivity | None = None
    # Presente quando o jogador é um bot: a estratégia que ele joga
    bot: RoomBotDTO | None = None


class RoomBotRequest(BaseModel):
    # Nome do bot na sala; ao configurar, o novo nome (o atual vai na rota)
    nickname: str
    strategy_key: str
    # Os parâmetros que faltarem ficam no padrão do catálogo
    params: dict[str, StrategyParamValue] = Field(default_factory=dict)
    # Sem cor, o bot fica com a próxima livre (ao configurar, com a que já tem)
    color: str | None = None
    # Índice da equipe (1 a 10); só vale no modo em equipes
    team: int | None = None


class SimulationSettingsResponse(BaseModel):
    is_host: bool
    host_nickname: str
    simulation: SimulationSettingsDTO
    # Partida salva que o host escolheu para continuar; None quando é partida nova
    selected_simulation_id: int | None
    # Quem jogou a partida selecionada, com a cor guardada: presentes ou ausentes
    selected_players: list[PlayerNickname]


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
    description="Escolhe a simulação salva a continuar. As cores e as equipes da sala passam a ser as guardadas nela. Apenas o host pode executar.",
)
def select_simulation(payload: SelectSimulationRequest, _: HostVerified):
    """
    Seleciona a simulação salva que o host vai continuar.
    """
    if SimulationManager.has_active_simulation():
        raise ConflictError("Já existe uma partida em andamento.")
    if repository.simulation.get_simulation(payload.id) is None:
        raise NotFoundError("Simulação não encontrada.")

    UserManager.apply_saved_colors(
        repository.simulation_player.colors(payload.id),
        repository.simulation_player.teams(payload.id),
        saved_bots(payload.id),
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
        SimulationManager.has_active_simulation()
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
    teams = UserManager.room_teams()
    activities = UserManager.room_activities()
    return [
        PlayerNickname(
            nickname=p.nickname,
            color=colors[p.id],
            team=teams.get(p.id),
            activity=activities.get(p.id),
            bot=UserManager.room_bot(p),
        )
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
    bots = saved_bot_infos(simulation_id)
    return [
        PlayerNickname(
            nickname=p.nickname,
            color=colors[p.id],
            team=teams.get(p.id),
            bot=bots.get(p.id),
        )
        for p in repository.simulation_player.participants(simulation_id)
    ]


@simulation_router.get(
    "/bots/strategies",
    response_model=list[StrategyInfoDTO],
    summary="Listar as estratégias para os bots",
    description="As estratégias do app com os parâmetros, a faixa de cada um e o padrão calculado para a data de início das regras do lobby, e os nomes sugeridos para o bot. Apenas o host pode executar.",
)
def list_bot_strategies(_: HostVerified):
    """
    Lista as estratégias que um bot da sala pode jogar.
    """
    return catalog.infos(
        SettingsManager.get().start_date, None, catalog.known_tickers()
    )


@simulation_router.get(
    "/bots/tickers",
    response_model=list[str],
    summary="Listar as ações que um bot pode operar",
    description="Os tickers cadastrados, em ordem alfabética, para escolher as ações de uma estratégia antes de a partida começar. Apenas o host pode executar.",
)
def list_bot_tickers(_: HostVerified):
    """
    Lista as ações que um bot da sala pode operar.
    """
    return sorted(catalog.known_tickers())


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
        payload.strategy_key,
        payload.params,
        payload.color,
        payload.team,
    )
    return _room_player(bot)


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
        payload.strategy_key,
        payload.params,
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
    "/life-history",
    response_model=LifeHistoryPageDTO,
    summary="Histórico do viver de renda",
    description="Imprevistos, demissões, entrada e saída do cheque especial e o juro de cada mês, com o caixa do jogador depois de cada um. Paginado: `offset` e `limit` (6 por padrão), filtrável por categoria e ordenável por `sort_by` e `sort_direction`. O padrão é data decrescente; a ordenação considera todo o histórico antes da paginação.",
)
def get_life_history(
    client_id: ClientID,
    category: LifeHistoryCategory | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=6, ge=1, le=100),
    sort_by: LifeHistorySort = LifeHistorySort.DATE,
    sort_direction: Literal["asc", "desc"] = "desc",
):
    """
    Retorna uma página do histórico de quem pede.
    """
    if not SimulationManager.has_active_simulation():
        raise ConflictError("Não há partida em andamento.")
    events = repository.event.get_cashflow_events(
        SimulationManager.get_active_simulation_id(),
        UserManager.get_user_id(client_id),
    )
    return history_page(
        build_history(events), category, offset, limit, sort_by, sort_direction
    )


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
    UserManager.join_match(client_id, payload.color, payload.team)


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

    notify("simulation_settings_update", settings.to_json())
    return settings
