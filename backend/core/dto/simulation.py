from datetime import date, datetime
from decimal import Decimal

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
    starting_cash: Decimal
    monthly_contribution: Decimal
    price_impact_enabled: bool
    price_impact_k: float
    price_impact_decay_days: int
    # Só decide a partida na Clássica; nos outros tipos vence quem chega à meta
    victory_criterion: VictoryCriterion
    game_type: GameType
    # Patrimônio-alvo da corrida à meta
    goal_net_worth: Decimal
    # Viver de renda: o salário e a despesa do mês, os imprevistos por ano e a
    # fração retirada por ano que dá a meta (12 x despesa / taxa)
    monthly_salary: Decimal
    monthly_expense: Decimal
    unexpected_per_year: int
    withdrawal_rate: Decimal
    inflation_adjusted: bool
    player_grouping: PlayerGrouping = PlayerGrouping.INDIVIDUAL
    team_naming: TeamNaming = TeamNaming.COLOR
    # Ajudas da renda fixa: desligadas, o servidor omite os campos que dão a resposta
    show_equivalent_rate: bool = True
    show_maturity_projection: bool = True


class SimulationDTO(SimulationSettingsDTO):
    id: int


class SimulationSummaryDTO(SimulationSettingsDTO):
    id: int
    created_at: datetime
    last_simulated_at: datetime


class SavedSimulationDTO(SimulationSummaryDTO):
    resume_from: date | None
    status: SimulationStatus
    players_count: int
    # Apelido do vencedor; em equipes, o nome da equipe vencedora
    winner_nickname: str | None
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
