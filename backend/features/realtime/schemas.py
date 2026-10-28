"""
DTOs dos payloads emitidos via `notify(...)` (WebSocket).

Servem para dois propósitos:
1. Tipar os call sites de `notify(...)` em vez de dicts soltos.
2. Compor `RealtimeEventCatalog`, exposto via rota dev-only para que
   `openapi-typescript` gere `types/events.ts` a partir destes schemas.
"""

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from backend.core.dto.achievements import AchievementUnlockedEventDTO
from backend.core.dto.backtest import (
    BacktestEndedEventDTO,
    BacktestProgressEventDTO,
    BacktestStatusDTO,
)
from backend.core.dto.base import BaseDTO
from backend.core.dto.bot import RoomBotDTO
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.goal import GoalProgressDTO
from backend.core.dto.inbox import InboxEntryDTO
from backend.core.dto.life import LifeEventDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.patrimonial_history import PortfolioHistoryPointDTO
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.preset import PresetAppliedEventDTO
from backend.core.dto.simulation import SimulationSettingsDTO, SimulationStatusResponse
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.dto.strategy import StrategyOrderLineDTO
from backend.core.enum import (
    CreditGrade,
    GovernmentNoticeKind,
    OrderAction,
    PauseReason,
    PlayerActivity,
    VoterGroup,
)


class CashUpdateEventDTO(BaseDTO):
    cash: Decimal


class SpeedUpdateEventDTO(BaseDTO):
    """Nova velocidade da partida; com ela parada (0), o motivo da pausa."""

    speed: int
    pause_reason: PauseReason | None


class SimulationTickUpdateEventDTO(BaseDTO):
    current_date: date


class PlayerPresenceEventDTO(BaseDTO):
    """Entrada, saída e troca de cor, equipe ou atividade de um jogador: a cor é a chave da paleta."""

    nickname: str
    color: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes ou enquanto não escolheu
    team: int | None = None
    # O que o jogador está fazendo; nulo é "Online" (partida em andamento ou sem aviso ainda)
    activity: PlayerActivity | None = None
    # Presente quando o jogador é um bot da sala: a estratégia que ele joga
    bot: RoomBotDTO | None = None
    # Só no evento de configurar o bot, que pode renomeá-lo: o nome de antes
    previous_nickname: str | None = None


class PlayerRemovedEventDTO(BaseDTO):
    """Só para quem o host tirou da sala: a página encerra a sessão e conta o motivo."""

    nickname: str


class SimulationSelectedEventDTO(BaseDTO):
    simulation_id: int | None


class SimulationDeletedEventDTO(BaseDTO):
    simulation_id: int


class SimulationEndedEventDTO(BaseDTO):
    reason: Literal["completed", "stopped_by_host", "error"]
    simulation_id: int


class OrderExecutedEventDTO(BaseDTO):
    order_id: str
    ticker: str
    action: OrderAction
    price: Decimal
    quantity: Decimal


class OrderPartialExecutedEventDTO(OrderExecutedEventDTO):
    remaining: Decimal


class StocksUpdateEventDTO(BaseDTO):
    stocks: list[CandleDTO]


class StockUpdateEventDTO(BaseDTO):
    stock: CandleDTO


class PositionUpdateEventDTO(BaseDTO):
    position: PositionDTO


class OrderEventDTO(BaseDTO):
    order: OrderDTO


class OrderBookSnapshotEventDTO(BaseDTO):
    orders: list[OrderDTO]


class FixedAssetsUpdateEventDTO(BaseDTO):
    assets: list[FixedIncomeAssetDTO]


class PortfolioUpdateEventDTO(BaseDTO):
    portfolio: PortfolioDTO


class SnapshotUpdateEventDTO(BaseDTO):
    snapshot: PortfolioHistoryPointDTO


class StatisticsSnapshotEntryDTO(BaseDTO):
    player_nickname: str
    snapshot: SnapshotDTO


class StatisticsSnapshotUpdateEventDTO(BaseDTO):
    snapshots: list[StatisticsSnapshotEntryDTO]


class FutureRecordingProgressEventDTO(BaseDTO):
    """A série que começou a ser gravada e quantas já foram, de quantas."""

    series: str
    done: int
    total: int


class CreditInstallmentPaidEventDTO(BaseDTO):
    loan_number: int
    installment_number: int
    total_installments: int
    amount: Decimal


class CreditMonthlySummaryEventDTO(BaseDTO):
    """O resumo do mês que substitui o aviso de cada parcela nas velocidades altas."""

    month: date
    installments: int
    amount: Decimal


class CreditInstallmentLateEventDTO(BaseDTO):
    loan_id: UUID
    loan_number: int
    installment_number: int
    due_date: date
    amount: Decimal


class CreditInstallmentWarningEventDTO(BaseDTO):
    """Parcela que vence em até 7 dias sem caixa para cobri-la."""

    loan_number: int
    due_date: date
    amount: Decimal
    shortfall: Decimal


class CreditRatingChangedEventDTO(BaseDTO):
    before: CreditGrade
    after: CreditGrade
    points: int
    # Spread e limite da nota nova; o spread é nulo na nota D
    spread: Decimal | None
    debt_limit: Decimal


class CreditLoanPaidOffEventDTO(BaseDTO):
    loan_number: int
    amount: Decimal
    # Juro que a quitação antecipada deixou de custar; zero na última parcela
    interest_saved: Decimal


class GovernmentUpdateEventDTO(BaseDTO):
    """A eleição mudou: a página renova e, conforme o tipo, o aviso conta o que houve."""

    kind: GovernmentNoticeKind
    # Quem fez e quem sofreu a ação, pelo apelido
    actor: str | None = None
    target: str | None = None
    party_abbr: str | None = None
    amount: Decimal | None = None
    # No resultado: o turno e o vencedor (sigla), se já houver; na posse, a sigla e o nome do presidente
    round: int | None = None
    winner_abbr: str | None = None
    winner_name: str | None = None
    # Na resposta ao convite de vice: se aceitou
    accepted: bool | None = None
    # Nas medidas: o título, a chance no voto, o dia em que passa a valer e os ativos que atinge
    measure_title: str | None = None
    chance: int | None = None
    effective: date | None = None
    tickers: list[str] | None = None
    # No impeachment: quem saiu (actor) e quem assumiu (target, nulo sem vice); no aviso, os meses abaixo do piso
    months_below_floor: int | None = None
    approval: int | None = None
    # No fechamento do mês: a aprovação do mês anterior e os grupos que aprovaram e reprovaram
    previous_approval: int | None = None
    groups_approved: list[VoterGroup] | None = None
    groups_reproved: list[VoterGroup] | None = None
    # Nos avisos do calendário: o dia em que as chapas fecham e o do 1º turno
    ticket_deadline: date | None = None
    first_round: date | None = None


class StrategyUpdateEventDTO(BaseDTO):
    """O modo do jogador mudou: ligou, trocou, desligou ou a estratégia deu erro."""

    active: bool
    # A causa, quando a estratégia deu erro e devolveu o jogador ao manual
    error: str | None = None


class StrategyOrdersEventDTO(BaseDTO):
    """O que a estratégia do jogador fez no dia."""

    orders: list[StrategyOrderLineDTO]


class RealtimeEventCatalog(BaseDTO):
    """
    Um campo por nome de evento realtime, tipado para o DTO do payload
    correspondente. Nunca é instanciado de verdade — só existe para que seu
    schema apareça em `/openapi.json` via a rota dev-only em `routes/realtime.py`.
    """

    simulation_started: SimulationStatusResponse
    simulation_ended: SimulationEndedEventDTO
    backtest_started: BacktestStatusDTO
    backtest_progress: BacktestProgressEventDTO
    backtest_ended: BacktestEndedEventDTO
    simulation_update: SimulationTickUpdateEventDTO
    speed_update: SpeedUpdateEventDTO
    cash_update: CashUpdateEventDTO
    stocks_update: StocksUpdateEventDTO
    fixed_assets_update: FixedAssetsUpdateEventDTO
    snapshot_update: SnapshotUpdateEventDTO
    portfolio_update: PortfolioUpdateEventDTO
    statistics_snapshot_update: StatisticsSnapshotUpdateEventDTO
    goal_progress_update: GoalProgressDTO
    life_event: LifeEventDTO
    order_executed: OrderExecutedEventDTO
    order_partial_executed: OrderPartialExecutedEventDTO
    player_join: PlayerPresenceEventDTO
    player_exit: PlayerPresenceEventDTO
    player_removed: PlayerRemovedEventDTO
    player_color: PlayerPresenceEventDTO
    player_team: PlayerPresenceEventDTO
    player_activity: PlayerPresenceEventDTO
    player_bot: PlayerPresenceEventDTO
    simulation_selected: SimulationSelectedEventDTO
    simulation_deleted: SimulationDeletedEventDTO
    simulation_settings_update: SimulationSettingsDTO
    preset_applied_update: PresetAppliedEventDTO
    stock_update: StockUpdateEventDTO
    position_update: PositionUpdateEventDTO
    order_added: OrderEventDTO
    order_updated: OrderEventDTO
    order_book_snapshot: OrderBookSnapshotEventDTO
    future_recording_progress: FutureRecordingProgressEventDTO
    achievement_unlocked: AchievementUnlockedEventDTO
    inbox_entry: InboxEntryDTO
    credit_installment_paid: CreditInstallmentPaidEventDTO
    credit_monthly_summary: CreditMonthlySummaryEventDTO
    credit_installment_late: CreditInstallmentLateEventDTO
    credit_installment_warning: CreditInstallmentWarningEventDTO
    credit_rating_changed: CreditRatingChangedEventDTO
    credit_loan_paid_off: CreditLoanPaidOffEventDTO
    government_update: GovernmentUpdateEventDTO
    strategy_update: StrategyUpdateEventDTO
    strategy_orders: StrategyOrdersEventDTO
