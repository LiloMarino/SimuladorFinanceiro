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
from backend.core.dto.budget import BudgetDTO
from backend.core.dto.campaign import CampaignHistoryDTO, CampaignPanelDTO
from backend.core.dto.candle import CandleDTO
from backend.core.dto.candle_challenge import (
    CandleChallengeStateDTO,
    ChallengeNoticeEventDTO,
)
from backend.core.dto.candle_patterns import CandlePatternsUpdateDTO
from backend.core.dto.credit import CreditOverviewDTO
from backend.core.dto.dividends import AssetCorporateEventsDTO
from backend.core.dto.economy import EconomyPanelDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO, FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import FixedIncomeQuoteDTO
from backend.core.dto.fund import (
    FundAccountDTO,
    FundBuybackPreviewDTO,
    FundDetailsDTO,
    FundDirectedIssuancePreviewDTO,
    FundIssuancePreviewDTO,
    FundIssuanceSubscriptionPreviewDTO,
    FundMergePreviewDTO,
    FundOffersDTO,
    FundRoomItemDTO,
)
from backend.core.dto.goal import GoalProgressDTO
from backend.core.dto.government import (
    CongressBaseDTO,
    ElectionPanelDTO,
    GovernmentPanelDTO,
    GovernmentStatusDTO,
    ImpeachmentDTO,
    MapPanelDTO,
    MapTimelineDTO,
    PromisesPanelDTO,
)
from backend.core.dto.life import LifeEventDTO, LifeStatusDTO
from backend.core.dto.news import NewsDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.order_preview import OrderPreviewDTO, OrderPreviewRequest
from backend.core.dto.patrimonial_history import PortfolioHistoryPointDTO
from backend.core.dto.pending import PendingDTO
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.preparation import PreparationsDTO
from backend.core.dto.presence import PlayerPresenceEventDTO, PlayerRemovedEventDTO
from backend.core.dto.preset import PresetAppliedEventDTO
from backend.core.dto.promises import BalanceDTO
from backend.core.dto.simulation import SimulationSettingsDTO, SimulationStatusResponse
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.dto.sovereign_fund import SovereignFundPanelDTO
from backend.core.dto.state_company import (
    StateCompaniesPanelDTO,
    StateCompanyDetailDTO,
)
from backend.core.dto.strategy import (
    MyStrategyDTO,
    StrategyLogRowDTO,
    StrategyOrderLineDTO,
)
from backend.core.dto.summaries import SummaryDTO
from backend.core.dto.technical_indicators import (
    IndicatorsRequestDTO,
    TechnicalIndicatorsDTO,
)
from backend.core.dto.treasury import (
    TreasuryCatalogDTO,
    TreasuryHistoryPointDTO,
    TreasuryPositionDTO,
)
from backend.core.enum import (
    CampaignActionKind,
    CreditGrade,
    DiceBand,
    GovernmentNoticeKind,
    OrderAction,
    PauseReason,
    VoterGroup,
)
from backend.features.variable_income.corporate_actions import PlayerCorporateActions


class CashUpdateEventDTO(BaseDTO):
    cash: Decimal
    # A gestora dona do caixa, para o gestor que a gere; nulo é o caixa pessoal
    account: int | None


class SpeedUpdateEventDTO(BaseDTO):
    """Nova velocidade da partida; com ela parada (0), o motivo da pausa."""

    speed: int
    pause_reason: PauseReason | None


class SimulationTickUpdateEventDTO(BaseDTO):
    current_date: date


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


class OrderCanceledEventDTO(BaseDTO):
    """O motor cancelou o resto da ordem do jogador, com o motivo."""

    order_id: str
    ticker: str
    action: OrderAction
    quantity: Decimal
    reason: str


class StocksUpdateEventDTO(BaseDTO):
    stocks: list[CandleDTO]


class StockUpdateEventDTO(BaseDTO):
    stock: CandleDTO


class PositionUpdateEventDTO(BaseDTO):
    position: PositionDTO
    # A gestora dona da posição, para o gestor que a gere; nulo é a posição pessoal
    account: int | None


class OrderEventDTO(BaseDTO):
    order: OrderDTO


class OrderBookSnapshotEventDTO(BaseDTO):
    orders: list[OrderDTO]


class OrderPreviewEventDTO(BaseDTO):
    """A prévia recalculada do último pedido do cliente no ativo, só para ele."""

    # O pedido que gerou a prévia: a boleta só aplica a que corresponde ao rascunho dela
    request: OrderPreviewRequest
    # A conta em que o pedido foi feito (id da gestora; nulo é a pessoal)
    account: int | None
    # Nulo quando a ordem não cabe; `refused` traz então o motivo
    preview: OrderPreviewDTO | None
    refused: str | None


class FundIssuancePreviewEventDTO(BaseDTO):
    """A prévia da emissão recalculada para o último pedido do gestor na gestora, só para ele."""

    # A quantidade que gerou a prévia: o diálogo só aplica a que corresponde ao que ele digitou
    quotas: int
    # Nulo quando o pedido não cabe; `refused` traz então o motivo
    preview: FundIssuancePreviewDTO | None
    refused: str | None


class FundSubscriptionPreviewEventDTO(BaseDTO):
    """A prévia da compra na preferência recalculada para o último pedido do cotista, só para ele."""

    quotas: int
    preview: FundIssuanceSubscriptionPreviewDTO | None
    refused: str | None


class FundDirectedPreviewEventDTO(BaseDTO):
    """A prévia da emissão dirigida recalculada para o último pedido de quem gere a gestora, só para ele."""

    quotas: int
    preview: FundDirectedIssuancePreviewDTO | None
    refused: str | None


class FundMergePreviewEventDTO(BaseDTO):
    """A prévia da fusão recalculada para o último pedido do gestor principal, só para ele."""

    # A gestora incorporada que gerou a prévia
    daughter_fund_id: int
    preview: FundMergePreviewDTO | None
    refused: str | None


class FundBuybackPreviewEventDTO(BaseDTO):
    """A prévia da recompra recalculada para o último pedido do gestor na gestora, só para ele."""

    quantity: int
    max_price: Decimal
    preview: FundBuybackPreviewDTO | None
    refused: str | None


class IndicatorsUpdateEventDTO(BaseDTO):
    """O último pregão nos indicadores do último pedido do cliente no ativo, só para ele."""

    request: IndicatorsRequestDTO
    # O pregão anterior ao do aviso: o ponto novo só se soma a séries que terminam nele
    previous_date: date | None
    # `series` traz só o ponto novo de cada série pedida; o resumo vem inteiro
    update: TechnicalIndicatorsDTO


class StateCompanyUpdateEventDTO(BaseDTO):
    """A estatal do ativo como o jogador a vê, entregue a cada dia a quem abre a página."""

    detail: StateCompanyDetailDTO


class FixedAssetsUpdateEventDTO(BaseDTO):
    assets: list[FixedIncomeAssetDTO]


class FixedIncomeProjectionEventDTO(BaseDTO):
    """A cotação da boleta de renda fixa recalculada para o último valor digitado do cliente, só para ele."""

    # O valor que gerou a cotação: a boleta só aplica a que corresponde ao que ela digitou
    amount: Decimal
    # A conta em que a cotação foi pedida (id da gestora; nulo é a pessoal)
    account: int | None
    quote: FixedIncomeQuoteDTO


class CreditUpdateEventDTO(BaseDTO):
    """O crédito de uma conta com parcela em atraso, que multa e mora recalculam a cada dia."""

    overview: CreditOverviewDTO
    # A gestora dona da conta do crédito; nulo é a conta pessoal
    account: int | None


class TreasuryPositionsUpdateEventDTO(BaseDTO):
    """Os títulos do Tesouro de uma conta do jogador, marcados no preço do dia."""

    positions: list[TreasuryPositionDTO]
    # A gestora dona dos títulos; nulo é a conta pessoal
    account: int | None


class TreasuryHistoryUpdateEventDTO(BaseDTO):
    """O ponto do mês que fechou na série do Tesouro; a série já aberta na tela só recebe esse ponto."""

    point: TreasuryHistoryPointDTO


class LifeStatusUpdateEventDTO(BaseDTO):
    """A vida financeira do jogador no viver de renda, entregue a quem a tem aberta."""

    status: LifeStatusDTO


class PendingUpdateEventDTO(BaseDTO):
    """As pendências do jogador, das graves para as de aviso."""

    items: list[PendingDTO]


class FundAccountsUpdateEventDTO(BaseDTO):
    """As contas com que o jogador opera, com o caixa e o congelamento de cada uma."""

    accounts: list[FundAccountDTO]


class FundRoomUpdateEventDTO(BaseDTO):
    """As gestoras da sala como o jogador as vê."""

    funds: list[FundRoomItemDTO]


type ComanagerEventKind = Literal[
    "invited",
    "accepted",
    "declined",
    "left",
    "removed",
    "directed_offered",
    "directed_accepted",
    "directed_declined",
    "directed_cancelled",
]


class ComanagerEventDTO(BaseDTO):
    """O que mudou na co-gestão de uma gestora para o jogador: convite, resposta, saída ou remoção, e a oferta de cotas novas com a resposta a ela."""

    kind: ComanagerEventKind
    fund_id: int
    ticker: str
    # Quem agiu: o principal que convidou ou removeu, ou o co-gestor que respondeu ou saiu
    nickname: str
    # A parte das taxas do convite ou do aceite (0,30 é 30%); nula na oferta de cotas novas
    share: Decimal | None


class PortfolioUpdateEventDTO(BaseDTO):
    portfolio: PortfolioDTO
    # A gestora dona da carteira, para o gestor que a gere; nulo é a carteira pessoal
    account: int | None


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
    # Nulo no consignado, que não tem número
    loan_number: int | None
    installment_number: int
    total_installments: int
    amount: Decimal
    # A gestora dona da conta do empréstimo; nulo na conta pessoal
    account: int | None = None


class AutoRedeemEventDTO(BaseDTO):
    """Um título vendido pelo sistema para cobrir um débito automático."""

    asset_name: str
    net_amount: Decimal
    # A despesa coberta, já em texto: "a despesa do mês", "a parcela do empréstimo"
    reason: str
    # A gestora dona do título vendido; nulo é a carteira pessoal
    account: int | None


class DividendLineDTO(BaseDTO):
    ticker: str
    amount: Decimal


class SplitLineDTO(BaseDTO):
    ticker: str
    # A razão: 2 é 2 para 1; 0,1 é grupamento 10 para 1
    ratio: Decimal
    shares_before: Decimal
    shares_after: Decimal
    # O que a fração que sobrou rendeu na venda; zero sem fração
    fraction_amount: Decimal


class CorporateActionsEventDTO(BaseDTO):
    """O que os proventos e os desdobramentos do pregão fizeram na carteira do jogador."""

    # Do ativo que mais pagou ao que menos pagou
    dividends: list[DividendLineDTO]
    dividends_total: Decimal
    splits: list[SplitLineDTO]

    @staticmethod
    def from_actions(actions: PlayerCorporateActions) -> "CorporateActionsEventDTO":
        dividends = sorted(
            (
                DividendLineDTO(ticker=d.ticker, amount=d.amount)
                for d in actions.dividends
            ),
            key=lambda line: line.amount,
            reverse=True,
        )
        return CorporateActionsEventDTO(
            dividends=dividends,
            dividends_total=sum((d.amount for d in dividends), Decimal(0)),
            splits=[
                SplitLineDTO(
                    ticker=s.ticker,
                    ratio=s.ratio,
                    shares_before=s.size_before,
                    shares_after=s.size_after,
                    fraction_amount=s.fraction_amount,
                )
                for s in actions.splits
            ],
        )


class OvertimeAvailableEventDTO(BaseDTO):
    """O PIB de 12 meses voltou a zero: a hora extra que a recessão desligou pode ser ligada de novo."""

    event_date: date


class CreditMonthlySummaryEventDTO(BaseDTO):
    """O resumo do mês que substitui o aviso de cada parcela nas velocidades altas."""

    month: date
    installments: int
    amount: Decimal
    # A gestora dona da conta do empréstimo; nulo na conta pessoal
    account: int | None = None


class CreditInstallmentLateEventDTO(BaseDTO):
    loan_id: UUID
    loan_number: int
    installment_number: int
    due_date: date
    amount: Decimal
    # A gestora dona da conta do empréstimo; nulo na conta pessoal
    account: int | None = None


class CreditInstallmentWarningEventDTO(BaseDTO):
    """Parcela que vence em até 7 dias sem caixa para cobri-la."""

    loan_number: int
    due_date: date
    amount: Decimal
    shortfall: Decimal
    # A gestora dona da conta do empréstimo; nulo na conta pessoal
    account: int | None = None


class CreditRatingChangedEventDTO(BaseDTO):
    before: CreditGrade
    after: CreditGrade
    points: int
    # Spread e limite da nota nova; o spread é nulo na nota D
    spread: Decimal | None
    debt_limit: Decimal
    # A gestora dona da conta do empréstimo; nulo na conta pessoal
    account: int | None = None


class CreditLoanPaidOffEventDTO(BaseDTO):
    loan_number: int
    amount: Decimal
    # Juro que a quitação antecipada deixou de custar; zero na última parcela
    interest_saved: Decimal
    # A gestora dona da conta do empréstimo; nulo na conta pessoal
    account: int | None = None


class GovernmentUpdateEventDTO(BaseDTO):
    """Um fato do governo ou da eleição: o aviso conta o que houve e carrega o dado que o toast e o diálogo mostram."""

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
    # No resultado: a fatia dos votos válidos do vencedor, as siglas que vão ao 2º turno, as datas da posse e do 2º turno,
    # e os fundadores (apelido por sigla) dos partidos eliminados, que podem declarar apoio
    winner_share: Decimal | None = None
    finalists: list[str] | None = None
    inauguration: date | None = None
    runoff: date | None = None
    endorsers: dict[str, str] | None = None
    # Na resposta ao convite de vice: se aceitou
    accepted: bool | None = None
    # Nas votações da casa: o título da medida, o placar (Sim, Não e quantos desobedeceram), o dia em que passa a valer e os ativos que atinge
    measure_title: str | None = None
    yes: int | None = None
    no: int | None = None
    defected: int | None = None
    effective: date | None = None
    tickers: list[str] | None = None
    # No impeachment: quem saiu (actor) e quem assumiu (target, nulo sem vice); no aviso, os meses abaixo do piso
    months_below_floor: int | None = None
    approval: int | None = None
    # No impeachment: a votação, o fim do mandato, a eleição seguinte e a bancada do computador que assume sem vice
    impeachment: ImpeachmentDTO | None = None
    term_end: date | None = None
    next_election: date | None = None
    heir_abbr: str | None = None
    heir_seats: int | None = None
    heir_name: str | None = None
    # No fechamento do mês: a aprovação do mês anterior e os grupos que aprovaram e reprovaram
    previous_approval: int | None = None
    groups_approved: list[VoterGroup] | None = None
    groups_reproved: list[VoterGroup] | None = None
    # Nos avisos do calendário: o dia em que as chapas fecham e o do 1º turno
    ticket_deadline: date | None = None
    first_round: date | None = None
    # Na ação de campanha: qual, em que grupo (nulo na TV) e contra qual partido (só no ataque)
    campaign_action: CampaignActionKind | None = None
    group: VoterGroup | None = None
    rival_abbr: str | None = None
    # O efeito da ação no grupo e o dado, como o destinatário os vê: quem agiu vê o dado e a rejeição, o atacado só o apoio
    support: Decimal | None = None
    rejection: Decimal | None = None
    band: DiceBand | None = None
    roll: int | None = None
    # Verdadeiro quando o aviso é o ataque que o partido do destinatário sofreu
    received: bool | None = None
    # Nos acordos de apoio: as cadeiras da base antes e depois, e se foi o aliado quem rompeu
    seats_before: int | None = None
    seats_after: int | None = None
    broken_by_ally: bool | None = None
    # Nas federações: o nome dela e a sigla do outro partido (party_abbr é quem agiu)
    federation_name: str | None = None
    partner_abbr: str | None = None
    # Nos pedidos de impeachment: a sigla do partido que pediu; nula quando o piso abriu o pedido
    requested_by: str | None = None


class StrategyUpdateEventDTO(BaseDTO):
    """O automático de uma conta mudou: ligou, trocou, desligou, deu erro ou o painel andou com as ordens."""

    # A gestora dona da conta; nulo é a conta pessoal
    account: int | None
    # O automático da conta já como a tela o mostra
    my_strategy: MyStrategyDTO


class StrategyLogEventDTO(BaseDTO):
    """As linhas do registro da estratégia de uma conta que entraram ou mudaram depois de gravadas."""

    # A gestora dona do registro; nulo é o da conta pessoal
    account: int | None
    # As linhas novas e as alteradas (a ordem limitada que fechou), da mais recente para a mais antiga
    rows: list[StrategyLogRowDTO]
    # O total do registro em cada filtro, já com as linhas novas
    total_all: int
    total_orders: int
    total_modes: int


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
    fixed_income_offer_update: FixedIncomeOfferDTO
    fixed_income_projection: FixedIncomeProjectionEventDTO
    sovereign_fund_update: SovereignFundPanelDTO
    state_companies_update: StateCompaniesPanelDTO
    credit_update: CreditUpdateEventDTO
    treasury_catalog_update: TreasuryCatalogDTO
    treasury_history_update: TreasuryHistoryUpdateEventDTO
    treasury_positions_update: TreasuryPositionsUpdateEventDTO
    life_status_update: LifeStatusUpdateEventDTO
    pending_update: PendingUpdateEventDTO
    fund_accounts_update: FundAccountsUpdateEventDTO
    funds_list_update: FundRoomUpdateEventDTO
    fund_offers_update: FundOffersDTO
    fund_update: FundDetailsDTO
    fund_issuance_preview: FundIssuancePreviewEventDTO
    fund_subscription_preview: FundSubscriptionPreviewEventDTO
    fund_directed_preview: FundDirectedPreviewEventDTO
    fund_merge_preview: FundMergePreviewEventDTO
    fund_buyback_preview: FundBuybackPreviewEventDTO
    corporate_events_update: AssetCorporateEventsDTO
    comanager_update: ComanagerEventDTO
    budget_update: BudgetDTO
    economy_update: EconomyPanelDTO
    base_update: CongressBaseDTO
    election_update: ElectionPanelDTO
    map_update: MapPanelDTO
    map_timeline_update: MapTimelineDTO
    campaign_update: CampaignPanelDTO
    campaign_history_update: CampaignHistoryDTO
    promises_update: PromisesPanelDTO
    balances_update: list[BalanceDTO]
    government_panel_update: GovernmentPanelDTO
    government_status_update: GovernmentStatusDTO
    snapshot_update: SnapshotUpdateEventDTO
    portfolio_update: PortfolioUpdateEventDTO
    statistics_snapshot_update: StatisticsSnapshotUpdateEventDTO
    goal_progress_update: GoalProgressDTO
    life_event: LifeEventDTO
    overtime_available: OvertimeAvailableEventDTO
    auto_redeem: AutoRedeemEventDTO
    corporate_actions: CorporateActionsEventDTO
    order_executed: OrderExecutedEventDTO
    order_partial_executed: OrderPartialExecutedEventDTO
    order_canceled: OrderCanceledEventDTO
    player_join: PlayerPresenceEventDTO
    player_exit: PlayerPresenceEventDTO
    player_removed: PlayerRemovedEventDTO
    player_color: PlayerPresenceEventDTO
    player_team: PlayerPresenceEventDTO
    player_profession: PlayerPresenceEventDTO
    player_activity: PlayerPresenceEventDTO
    player_bot: PlayerPresenceEventDTO
    preparations_update: PreparationsDTO
    simulation_selected: SimulationSelectedEventDTO
    simulation_deleted: SimulationDeletedEventDTO
    simulation_settings_update: SimulationSettingsDTO
    preset_applied_update: PresetAppliedEventDTO
    stock_update: StockUpdateEventDTO
    position_update: PositionUpdateEventDTO
    order_added: OrderEventDTO
    order_updated: OrderEventDTO
    order_book_snapshot: OrderBookSnapshotEventDTO
    order_preview: OrderPreviewEventDTO
    indicators_update: IndicatorsUpdateEventDTO
    candle_patterns_update: CandlePatternsUpdateDTO
    state_company_update: StateCompanyUpdateEventDTO
    future_recording_progress: FutureRecordingProgressEventDTO
    achievement_unlocked: AchievementUnlockedEventDTO
    summary_delivered: SummaryDTO
    news_published: NewsDTO
    credit_installment_paid: CreditInstallmentPaidEventDTO
    credit_monthly_summary: CreditMonthlySummaryEventDTO
    credit_installment_late: CreditInstallmentLateEventDTO
    credit_installment_warning: CreditInstallmentWarningEventDTO
    credit_rating_changed: CreditRatingChangedEventDTO
    credit_loan_paid_off: CreditLoanPaidOffEventDTO
    government_update: GovernmentUpdateEventDTO
    strategy_update: StrategyUpdateEventDTO
    strategy_log_update: StrategyLogEventDTO
    strategy_orders: StrategyOrdersEventDTO
    candle_challenge_state: CandleChallengeStateDTO
    candle_challenge_notice: ChallengeNoticeEventDTO
