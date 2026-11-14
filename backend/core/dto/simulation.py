from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, model_validator

from backend.core.dto.backtest import BacktestProgressDTO
from backend.core.dto.base import BaseDTO
from backend.core.dto.life import (
    LifeEventTypes,
    LifeFrequenciesDTO,
    default_life_events,
)
from backend.core.enum import (
    ComputerDifficulty,
    GameType,
    InitialAccount,
    PlayerGrouping,
    SalaryMode,
    SelicControl,
    SimulationStatus,
    TeamNaming,
    VictoryCriterion,
)
from backend.core.periods import MONTHS_PER_YEAR

GOVERNMENT_MIN_YEARS = 5


def validate_government(
    *,
    game_type: GameType,
    player_grouping: PlayerGrouping,
    government_enabled: bool,
    start_date: date,
    end_date: date,
    first_election: date | None,
    selic_control: SelicControl = SelicControl.AUTONOMOUS,
) -> None:
    """As regras da expansão Governo & Política; valem igual para o DTO e para a requisição."""
    if game_type is GameType.POLITICAL and not government_enabled:
        raise ValueError("A vitória política exige a expansão Governo & Política.")
    if selic_control is SelicControl.GOVERNMENT and not government_enabled:
        raise ValueError(
            "A SELIC nas mãos do governo exige a expansão Governo & Política."
        )
    if not government_enabled:
        return
    if game_type is GameType.POLITICAL and player_grouping is PlayerGrouping.TEAMS:
        raise ValueError("A vitória política exige o modo individual.")
    if end_date < _add_years(start_date, GOVERNMENT_MIN_YEARS):
        raise ValueError(
            f"A expansão Governo & Política exige uma partida de {GOVERNMENT_MIN_YEARS} anos ou mais."
        )
    if first_election is None:
        raise ValueError("Escolha a data da primeira eleição.")
    if not start_date < first_election <= end_date:
        raise ValueError("A primeira eleição precisa cair dentro da partida.")


def validate_goal(
    *,
    game_type: GameType,
    goal_net_worth: Decimal,
    starting_cash: Decimal,
) -> None:
    """A regra da corrida à meta; vale igual para o DTO e para a requisição."""
    if game_type is GameType.GOAL_RACE and goal_net_worth <= starting_cash:
        raise ValueError("A meta precisa ser maior que o saldo inicial.")


def validate_independence(
    *,
    game_type: GameType,
    monthly_salary: Decimal,
    monthly_expense: Decimal,
    withdrawal_rate: Decimal,
    starting_cash: Decimal,
) -> None:
    """As regras de viver de renda; valem igual para o DTO e para a requisição."""
    if game_type is not GameType.FINANCIAL_INDEPENDENCE:
        return
    if monthly_salary <= 0 or monthly_expense <= 0:
        raise ValueError("Salário e despesa mensais precisam ser maiores que zero.")
    goal = MONTHS_PER_YEAR * monthly_expense / withdrawal_rate
    if goal <= starting_cash:
        raise ValueError(
            "A meta de independência (12 x a despesa ÷ a taxa de retirada) "
            "precisa ser maior que o saldo inicial."
        )


def _add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        # 29 de fevereiro num ano sem ele
        return day.replace(year=day.year + years, day=28)


class SimulationSettingsDTO(BaseDTO):
    name: str
    start_date: date
    end_date: date
    starting_cash: Decimal = Field(gt=0)
    monthly_contribution: Decimal = Field(ge=0)
    price_impact_enabled: bool
    price_impact_k: float = Field(ge=0)
    price_impact_decay_days: int = Field(ge=1)
    # Só decide a partida na Clássica; nos outros tipos vence quem chega à meta
    victory_criterion: VictoryCriterion
    game_type: GameType
    # Patrimônio-alvo da corrida à meta
    goal_net_worth: Decimal = Field(gt=0)
    # Viver de renda: o salário e a despesa do mês, os imprevistos por ano e a
    # fração retirada por ano que dá a meta (12 x despesa / taxa)
    monthly_salary: Decimal = Field(ge=0)
    monthly_expense: Decimal = Field(ge=0)
    unexpected_per_year: int = Field(ge=0, le=52)
    # Os tipos de imprevisto: valor e liga/desliga de cada um
    life_events: LifeEventTypes = Field(default_factory=default_life_events)
    # O quanto cada família de imprevistos sai; ausente, tudo em Normal
    life_frequencies: LifeFrequenciesDTO = Field(default_factory=LifeFrequenciesDTO)
    withdrawal_rate: Decimal = Field(ge=Decimal("0.01"), le=Decimal("0.10"))
    inflation_adjusted: bool
    # Viver de renda: o mesmo salário para todos ou uma profissão para cada jogador
    salary_mode: SalaryMode = SalaryMode.EQUAL
    player_grouping: PlayerGrouping = PlayerGrouping.INDIVIDUAL
    team_naming: TeamNaming = TeamNaming.COLOR
    # Ajudas da renda fixa: desligadas, o servidor omite os campos que dão a resposta
    show_equivalent_rate: bool = True
    show_maturity_projection: bool = True
    # Dicas de análise técnica no gráfico: padrões de vela e legendas dos indicadores
    show_chart_hints: bool = True
    # Expansão Governo & Política: trava quando a partida começa
    government_enabled: bool = False
    # Expansão Gestoras: trava quando a partida começa
    funds_enabled: bool = False
    # Data do 1º turno da primeira eleição; as seguintes caem a cada 4 anos
    first_election: date | None = None
    computer_difficulty: ComputerDifficulty = ComputerDifficulty.NORMAL
    # A pesquisa eleitoral mostra cada número com a margem de erro, sorteada pela semente
    poll_margin: bool = True
    # A conta do governo na largada: a jogável parte de números redondos, a realista da tabela do ano
    initial_account: InitialAccount = InitialAccount.PLAYABLE
    # Quem decide a SELIC: o Banco Central autônomo ou o presidente, nas reuniões do Copom
    selic_control: SelicControl = SelicControl.AUTONOMOUS

    @property
    def uses_professions(self) -> bool:
        """Cada jogador escolhe a profissão: só no viver de renda com o modo de profissões."""
        return (
            self.game_type is GameType.FINANCIAL_INDEPENDENCE
            and self.salary_mode is SalaryMode.PROFESSIONS
        )

    @property
    def expert_mode(self) -> bool:
        """Modo Especialista: todas as ajudas escondidas."""
        return not (
            self.show_equivalent_rate
            or self.show_maturity_projection
            or self.show_chart_hints
        )

    @model_validator(mode="after")
    def validate_rules(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        validate_government(
            game_type=self.game_type,
            player_grouping=self.player_grouping,
            government_enabled=self.government_enabled,
            start_date=self.start_date,
            end_date=self.end_date,
            first_election=self.first_election,
            selic_control=self.selic_control,
        )
        validate_goal(
            game_type=self.game_type,
            goal_net_worth=self.goal_net_worth,
            starting_cash=self.starting_cash,
        )
        validate_independence(
            game_type=self.game_type,
            monthly_salary=self.monthly_salary,
            monthly_expense=self.monthly_expense,
            withdrawal_rate=self.withdrawal_rate,
            starting_cash=self.starting_cash,
        )
        return self


class SimulationDTO(SimulationSettingsDTO):
    id: int


class SimulationSummaryDTO(SimulationSettingsDTO):
    id: int
    # Partida só de bots, rodada pelo host: a lista de salvas a separa das partidas
    is_backtest: bool
    created_at: datetime
    last_simulated_at: datetime


class SimulationResultDTO(BaseDTO):
    """O ranking de uma simulação até o último dia gravado, guardado para a lista."""

    # Fora da Clássica, o líder chegou na meta e a simulação terminou
    leader_reached_goal: bool
    players_count: int
    # Apelido do líder; em equipes, o nome da equipe líder
    leader_name: str | None
    # Colocação de cada jogador por apelido (a da equipe dele, em equipes)
    positions: dict[str, int]


class SavedSimulationDTO(SimulationSummaryDTO):
    resume_from: date | None
    status: SimulationStatus
    players_count: int
    # Apelido do vencedor; em equipes, o nome da equipe vencedora
    winner_nickname: str | None
    # Quem lidera até o último dia gravado, com a simulação terminada ou não; mesma forma do vencedor
    leader_nickname: str | None
    # Colocação de quem pede a lista (a da equipe dele, em equipes); None quando não jogou essa partida
    my_position: int | None
    # Quem está na sala, nunca jogou essa partida e não cabe nela; vazio quando dá para selecionar
    room_overflow: list[str]


class PriceImpactPointDTO(BaseDTO):
    day: int
    impact: float


class PriceImpactPreviewDTO(BaseDTO):
    volume_share: float
    first_day_impact: float
    curve: list[PriceImpactPointDTO]


class SimulationStatusResponse(BaseDTO):
    active: bool
    simulation: SimulationDTO | None = None
    # O backtest que roda: para a sala não é partida (`active` fica falso), e este
    # campo leva o andamento dele
    backtest: BacktestProgressDTO | None = None
