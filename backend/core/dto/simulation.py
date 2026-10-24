from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, model_validator

from backend.core.dto.backtest import BacktestProgressDTO
from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    GameType,
    PlayerGrouping,
    SimulationStatus,
    TeamNaming,
    VictoryCriterion,
)


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
    withdrawal_rate: Decimal = Field(ge=Decimal("0.01"), le=Decimal("0.10"))
    inflation_adjusted: bool
    player_grouping: PlayerGrouping = PlayerGrouping.INDIVIDUAL
    team_naming: TeamNaming = TeamNaming.COLOR
    # Ajudas da renda fixa: desligadas, o servidor omite os campos que dão a resposta
    show_equivalent_rate: bool = True
    show_maturity_projection: bool = True

    @model_validator(mode="after")
    def validate_rules(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        if (
            self.game_type is GameType.GOAL_RACE
            and self.goal_net_worth <= self.starting_cash
        ):
            raise ValueError("A meta precisa ser maior que o saldo inicial.")
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
