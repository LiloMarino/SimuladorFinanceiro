from __future__ import annotations

import logging
import re
import threading
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_FLOOR, Decimal
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar
from uuid import UUID

from backend import config
from backend.core import repository
from backend.core.dates import MONTHS_PER_QUARTER, add_months
from backend.core.dto.budget import BudgetDTO
from backend.core.dto.campaign import (
    CampaignActionRequest,
    CampaignHistoryDTO,
    CampaignPanelDTO,
    CampaignRollDTO,
)
from backend.core.dto.candle import CandleDTO, MarketQuoteDTO
from backend.core.dto.credit import (
    CreditOverviewDTO,
    LoanQuoteDTO,
    PayrollLoanDTO,
    PayrollQuoteDTO,
    PrepaymentPreviewDTO,
)
from backend.core.dto.dividends import AssetCorporateEventsDTO, PortfolioDividendsDTO
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.economy import EconomyPanelDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO, FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import (
    FixedIncomeQuoteDTO,
    FixedIncomeRedemptionQuoteDTO,
    NextTaxDropDTO,
)
from backend.core.dto.fund import (
    FUND_TICKER_PATTERN,
    FundAccountDTO,
    FundAssemblyConveneRequest,
    FundAssemblyDTO,
    FundAssemblyFeeProposalRequest,
    FundAssemblyVoteRequest,
    FundBuybackDTO,
    FundBuybackPreviewDTO,
    FundBuybackRequest,
    FundComanagerInviteRequest,
    FundComanagerShareRequest,
    FundContributionRequest,
    FundContributionResponse,
    FundDetailsDTO,
    FundDirectedIssuanceDTO,
    FundDirectedIssuancePreviewDTO,
    FundDirectedIssuanceRequest,
    FundDistributionRequest,
    FundFeesRequest,
    FundFoundRequest,
    FundIssuanceDTO,
    FundIssuancePreviewDTO,
    FundIssuanceRequest,
    FundIssuanceSubscriptionPreviewDTO,
    FundIssuanceSubscriptionRequest,
    FundMergePreviewDTO,
    FundMergeProposalRequest,
    FundMonthlyReportDTO,
    FundOffersDTO,
    FundRoomItemDTO,
    FundSummaryDTO,
    FundTickerCheckDTO,
)
from backend.core.dto.goal import GoalProgressDTO, GoalRunnerDTO
from backend.core.dto.government import (
    CongressBaseDTO,
    DealPreviewDTO,
    ElectionPanelDTO,
    FederationPreviewDTO,
    FoundPartyRequest,
    GovernmentPanelDTO,
    GovernmentStatusDTO,
    MapPanelDTO,
    MapTimelineDTO,
    MeasurePreviewDTO,
    PromisesPanelDTO,
    ProposeMeasureRequest,
)
from backend.core.dto.house_report import HousePickDTO, HouseRecommendationDTO
from backend.core.dto.life import (
    LifeEventDTO,
    LifeEventTypeDTO,
    LifeHistoryRowDTO,
    LifeStatusDTO,
)
from backend.core.dto.order import OrderDTO
from backend.core.dto.order_preview import (
    OrderPreviewDTO,
    OrderPreviewRequest,
    SovereignOrderPreviewDTO,
)
from backend.core.dto.patrimonial_history import (
    PatrimonialHistoryDTO,
    PortfolioHistoryPointDTO,
)
from backend.core.dto.pending import PendingDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.profession import (
    CONCLUDE_PREFIX,
    ENROLL_PREFIX,
    EXCHANGE_LOCK_ENDED,
    OVERTIME_AVAILABLE,
    OVERTIME_ENDED,
    SAVINGS_POSTPONED,
    SAVINGS_RELEASED,
    BrokerState,
    CltState,
    ConvertPension,
    EnrollCourse,
    EnrollStep,
    EntrepreneurState,
    ExporterState,
    FreelancerState,
    GraduateState,
    LeaveHome,
    LockedAssetDTO,
    LockExchange,
    MechanicAction,
    MechanicState,
    ProfessionPeriodDTO,
    ProfessionStateDTO,
    RedeemPension,
    RetireeState,
    SellCapital,
    SetExportMix,
    SetPrice,
    SetReinvestShare,
    WelfareState,
)
from backend.core.dto.profession_page import (
    HouseReportDTO,
    MechanicBlockDTO,
    ProfessionPageDTO,
)
from backend.core.dto.promises import BalanceDTO, PromisesPreviewDTO, PromisesRequest
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.snapshot import DayBalanceDTO, SnapshotDTO
from backend.core.dto.sovereign_fund import (
    SovereignContributionPreviewDTO,
    SovereignContributionRequest,
    SovereignFundPanelDTO,
)
from backend.core.dto.state_company import (
    FoundStateCompanyRequest,
    StateCompaniesPanelDTO,
    StateCompanyDetailDTO,
    StateFoundingPreviewDTO,
    StateOrderPreviewDTO,
    StateOrderRequest,
    StateReservationRequest,
)
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.strategy import (
    MyStrategyDTO,
    SignalDTO,
    StrategyInfoDTO,
    StrategyLogPageDTO,
    StrategyParamValue,
    StrategyViewDTO,
)
from backend.core.dto.technical_indicators import (
    IndicatorsRequestDTO,
    TechnicalIndicatorsDTO,
)
from backend.core.dto.treasury import (
    TreasuryCatalogDTO,
    TreasuryHistoryPointDTO,
    TreasuryPositionDTO,
    TreasurySaleQuoteDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.entrepreneur import BOT_SELL_SHARE, negative_quarters
from backend.core.enum import (
    AcademicStep,
    AssetClass,
    CashflowEventType,
    FixedIncomeType,
    FundAssemblyAgenda,
    FundComanagerStatus,
    GameType,
    IndicatorSeries,
    LifeEventEffect,
    MeasureKind,
    OrderAction,
    PauseReason,
    PendingType,
    PlayerGrouping,
    PrepaymentMode,
    Profession,
    VoterValue,
)
from backend.core.exceptions import InsufficentCashError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.exporter import (
    BOT_DOLLAR_AVERAGE_MONTHS,
    BOT_LOCK_MONTHS,
    BOT_LOCK_SHARE,
    LOCK_TERMS_MONTHS,
    forward_dollar,
)
from backend.core.fund_reference import FundReference
from backend.core.graduate import concluded as step_concluded
from backend.core.graduate import lives_with_parents
from backend.core.house_report import draw_report, previous_month_start, report_day
from backend.core.indicators import (
    annual_index_rate,
    last_known_rate,
    month_turns,
    monthly_average_rate,
    recent_focus_rate,
)
from backend.core.life_budget import LifeBudget
from backend.core.life_events import life_event_label
from backend.core.locked_assets import LOCKED_EXITS
from backend.core.metrics import (
    ENGINE_ACHIEVEMENTS,
    ENGINE_BACKTEST_DAY,
    ENGINE_BOTS,
    ENGINE_CONTRIBUTION,
    ENGINE_FIXED_INCOME,
    ENGINE_FUNDS,
    ENGINE_GOAL,
    ENGINE_GOVERNMENT,
    ENGINE_NEWS,
    ENGINE_PRICES,
    ENGINE_PUBLISH,
    ENGINE_SNAPSHOTS,
    ENGINE_SUMMARIES,
    ENGINE_TAXES,
    metrics,
)
from backend.core.networth import networth
from backend.core.pension import months_in_plan, real_rate, redeem_net
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.professions import (
    DOLLAR_WINDOW_DAYS,
    DRIVER_CURVES,
    HEALTH_EVENT_KEY,
    IncomeDriver,
    LifeLevers,
    RealRaise,
    available_professions,
    inheritance_rate,
    is_party_bound,
)
from backend.core.rates import from_percent, period_rate
from backend.core.repository.strategy import LogFilter
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import (
    format_money,
    format_quantity,
    last_month_turn,
    next_business_day,
    next_month_turn,
    required,
)
from backend.core.welfare import course_concluded
from backend.features.achievements.catalog import Achievement
from backend.features.achievements.evaluator import (
    AchievementEvaluator,
    match_result,
    unlocked_event,
)
from backend.features.backtest.progress import BacktestProgress
from backend.features.credit.overview import (
    build_overview,
    build_payroll_loan,
    build_payroll_quote,
    build_prepayment_preview,
)
from backend.features.credit.overview import build_quote as build_loan_quote
from backend.features.credit.rules import PAYROLL_MARGIN
from backend.features.economy.growth import (
    NEUTRAL_UNEMPLOYMENT,
    MacroCourse,
    MacroMonth,
    history_dollar,
    stocks_drawdown,
)
from backend.features.economy.panel import build_economy_panel
from backend.features.fixed_income import treasury, treasury_panel
from backend.features.fixed_income.accrual import (
    income_tax_brackets,
    income_tax_rate,
    iof_free_date,
    iof_rate,
    next_tax_drop,
    offer,
    project,
)
from backend.features.fixed_income.assistance import (
    apply_offer_assistance,
    build_quote,
)
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.liquidity import total_redeemable
from backend.features.funds.fund_book import Fund, FundBook
from backend.features.funds.fund_details import FundDetailsBuilder
from backend.features.funds.fund_estimate import IssuanceEstimator
from backend.features.funds.fund_preview import FundPreviewBuilder
from backend.features.funds.offers_panel import FundOffersBuilder
from backend.features.government import presidency
from backend.features.government.base_panel import build_base
from backend.features.government.base_panel import (
    build_preview as build_deal_preview,
)
from backend.features.government.budget_panel import build_budget
from backend.features.government.campaign_panel import (
    build_campaign,
    build_history,
    build_roll,
)
from backend.features.government.federation_panel import preview_dto
from backend.features.government.governance import (
    build_governance,
    build_government_status,
    sector_options,
)
from backend.features.government.government_book import GovernmentBook
from backend.features.government.map_panel import build_map
from backend.features.government.map_timeline import build_timeline
from backend.features.government.measures import short_date
from backend.features.government.panel import build_panel
from backend.features.government.promise_panel import (
    build_balances,
    build_preview,
    build_promises_panel,
)
from backend.features.newsroom.newsroom import Newsroom
from backend.features.notifications import news, registry
from backend.features.profession.banker import (
    BOT_HOUSE_CDB_YEARS,
    SELIC_AVERAGE_MONTHS,
    house_cdb_amount,
)
from backend.features.profession.broker import (
    bot_budget_each,
    bot_buys,
    candidates_of,
    horizon_end,
    picks_of,
    tradable_today,
    verdicts_of,
)
from backend.features.profession.clt import (
    after_layoff,
    after_month,
    clear_overtime_waiting,
    end_overtime,
    overtime_ends_with_recession,
    overtime_returns,
)
from backend.features.profession.entrepreneur import (
    pay_month,
    policy_recession_flag,
    policy_reinvest_share,
    policy_sale_due,
    sale_payout,
)
from backend.features.profession.exporter import (
    after_payment,
    lock_wanted,
    mix_change_allowed,
    mix_target,
)
from backend.features.profession.freelancer import policy_price, price_due
from backend.features.profession.graduate import conclude_step, policy_step
from backend.features.profession.mechanics import apply_action
from backend.features.profession.page import (
    appointee_block,
    banker_block,
    broker_block,
    build_header,
    build_series,
    clt_block,
    entrepreneur_block,
    exporter_block,
    freelancer_block,
    graduate_block,
    heir_block,
    no_block,
    offers_banker_block,
    public_servant_block,
    retiree_block,
    welfare_block,
)
from backend.features.profession.pension import (
    open_balance,
    policy_convert_amount,
    policy_redeem_amount,
)
from backend.features.profession.pension import pay_month as pay_pension_month
from backend.features.profession.policy import policy_action
from backend.features.profession.profession_book import ProfessionBook
from backend.features.profession.public_servant import (
    PAYROLL_TERM_MONTHS,
    PayrollMove,
    payroll_amount,
    payroll_policy,
)
from backend.features.profession.reserve import Reserve
from backend.features.profession.welfare import (
    mark_negative_cash,
    month_turn,
    policy_enroll,
    release,
    release_due,
)
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    ComanagerEventDTO,
    ComanagerEventKind,
    CorporateActionsEventDTO,
    HouseReportIssuedEventDTO,
    OvertimeAvailableEventDTO,
    PortfolioUpdateEventDTO,
    SimulationTickUpdateEventDTO,
    SnapshotUpdateEventDTO,
    SpeedUpdateEventDTO,
    StatisticsSnapshotEntryDTO,
    StatisticsSnapshotUpdateEventDTO,
    StocksUpdateEventDTO,
    StockUpdateEventDTO,
)
from backend.features.simulation.asset_page_feed import AssetPageFeed
from backend.features.simulation.cash_feed import CashFeed
from backend.features.simulation.day_feed import DayFeed
from backend.features.simulation.fund_preview_feed import (
    BUYBACK,
    DIRECTED,
    ISSUANCE,
    MERGE,
    SUBSCRIPTION,
    FundPreviewFeed,
)
from backend.features.simulation.funds_feed import FundsFeed
from backend.features.simulation.government_feed import GovernmentFeed
from backend.features.simulation.life_events import (
    layoff_factor_of,
    layoff_in,
    overdraft_interest,
    salary_skipped,
    unexpected_on,
)
from backend.features.simulation.life_history import (
    BudgetChange,
    HistoryPeriod,
    budget_changes,
)
from backend.features.simulation.life_history import (
    build_history as build_life_history,
)
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.sovereign_fund import headlines as fund_headlines
from backend.features.sovereign_fund import rules as fund_rules
from backend.features.sovereign_fund.book import FundQuotas
from backend.features.statistics.cache import ReportCache
from backend.features.statistics.goal import goal_on, goal_reached
from backend.features.strategy.runner import StrategyAccount, StrategyRunner
from backend.features.summaries.service import SummaryDelivery
from backend.features.tax_policy import TaxPolicy
from backend.features.variable_income.broker import to_money
from backend.features.variable_income.dividends import (
    build_asset_events,
    build_portfolio_dividends,
)
from backend.features.variable_income.entities.order import MarketOrder, Order
from backend.features.variable_income.price_impact import PriceImpact

# Pregões no mini gráfico da lista de mercado
SPARKLINE_DAYS = 30
ELIMINATED_MESSAGE = (
    "Você perdeu o controle da sua gestora e agora só assiste a partida."
)

logger = logging.getLogger(__name__)
P = ParamSpec("P")
R = TypeVar("R")


def synchronized(
    method: Callable[Concatenate[Simulation, P], R],
) -> Callable[Concatenate[Simulation, P], R]:
    """Uma consulta ou operação vê um pregão completo, usando o mesmo lock do motor."""

    @wraps(method)
    def call(self: Simulation, *args: P.args, **kwargs: P.kwargs) -> R:
        with self.lock:
            self._sync_depth += 1
            try:
                return method(self, *args, **kwargs)
            finally:
                self._sync_depth -= 1
                # A operação mais externa fecha com os painéis do país uma única vez,
                # qualquer que seja o número de mudanças que ela fez no governo
                if self._sync_depth == 0 and self._panels_stale:
                    self._panels_stale = False
                    self._publish_government_panels()
                # E com o que o caixa e as gestoras mudaram, já no estado final
                if self._sync_depth == 0:
                    self._publish_changed_screens()
                # E com as prévias de ordem que o caixa, a posição ou o book mudaram
                if self._sync_depth == 0:
                    self._refresh_order_previews()

    return call


_AGENDA_TITLES = {
    FundAssemblyAgenda.REPLACE_MANAGER: "Troca de gestor",
    FundAssemblyAgenda.FEE_INCREASE: "Aumento de taxa",
    FundAssemblyAgenda.MERGE: "Fusão",
}


def _agenda_title(assembly: FundAssemblyDTO) -> str:
    return _AGENDA_TITLES[assembly.agenda]


def _overdraft_rate(day: date) -> Decimal:
    """Juro mensal do cheque especial no dia: a SELIC da partida, em taxa mensal, mais o spread fixo."""
    selic = period_rate(
        annual_index_rate(IndicatorSeries.SELIC, day), Decimal(MONTHS_PER_YEAR)
    )
    return selic + Decimal(str(config.toml.simulation.overdraft_monthly_spread))


class Simulation:
    """
    Orquestrador principal da simulação financeira.

    Responsável por:
    - Avançar simulação dia-a-dia (next_tick), pulando finais de semana
    - Aplicar contribuições mensais e registrar eventos mensais
    - Debitar o IR da renda variável no vencimento do DARF
    - Criar snapshots diários do portfólio de todos os players
    - Fornecer interface de alto nível para operações (criar/cancelar ordens, consultar portfólio)
    - Gerenciar velocidade da simulação e notificar atualizações realtime
    - Limpar caches de usuários ao fazer logout
    """

    # Profundidade das operações sincronizadas em curso e se o governo mudou nelas:
    # `synchronized` publica os painéis do país ao fechar a operação mais externa
    _sync_depth = 0
    _panels_stale = False
    _publishing_round = False
    _participants_snapshot: list[UserDTO] | None = None

    def __init__(
        self,
        settings: SimulationDTO,
        resume_from: date | None = None,
        *,
        random_seed: int,
        backtest: BacktestProgress | None = None,
    ):
        """
        `resume_from` é o último dia já processado de uma simulação retomada; o
        primeiro tick é o dia útil seguinte. Sem ele, o primeiro tick é o `start_date`.
        `random_seed` é a semente gravada na partida, de onde saem os imprevistos.
        `backtest` põe a partida no modo de estratégias: sem avisos por pregão, sem
        meta nem conquistas, e os snapshots saem do balanço do motor, gravados em lote.
        """
        self._speed = 0
        # Quem parou a partida; vale enquanto a velocidade é 0
        self._pause_reason = PauseReason.HOST
        self.backtest = backtest
        # Snapshots do backtest ainda não gravados, e o aporte acumulado de cada jogador
        self._pending_snapshots: list[SnapshotDTO] = []
        self._contributed = Decimal(0)
        self.settings = settings
        self._random_seed = random_seed
        self._life = (
            LifeBudget.of(
                settings,
                lambda day: self._macro.latest(day).growth,
                self._levers_on,
                self._dollar_change_on,
                self._selic_on,
                lambda day: self._engine.dollar_on(day),
                self._unemployment_ratio_on,
            )
            if settings.game_type is GameType.FINANCIAL_INDEPENDENCE
            else None
        )
        # A profissão de cada jogador (user_id), lida da partida quando ela joga com profissões
        self._professions: dict[int, Profession] = {}
        # O partido de cada Comissionado (user_id) e os Banqueiros de ofertas da partida; lidos
        # da partida na primeira vez e refeitos quando entra jogador
        self._parties: dict[int, str] = {}
        self._offer_bankers: list[UUID] | None = None
        # As recomendações da casa sem desfecho e os meses com relatório, lidos do banco na primeira consulta
        self._house_open: list[HouseRecommendationDTO] | None = None
        self._house_months: set[date] | None = None
        # O estado da mecânica e os períodos de profissão de cada jogador
        self._profession_book = ProfessionBook(settings.id)
        self._current_date = resume_from or self.settings.start_date - timedelta(days=1)
        self._feed = AssetPageFeed(self)
        self._day_feed = DayFeed(self)
        self._cash_feed = CashFeed(self)
        self._funds_feed = FundsFeed(self)
        self._government_feed = GovernmentFeed(self)
        self._fund_preview_feed = FundPreviewFeed(self)
        self._engine = SimulationEngine(
            self._current_date,
            settings.id,
            settings.end_date,
            settings.start_date,
        )
        # O jogador escolhe no perfil se a cobertura automática vende também Prefixado e IPCA+
        self._engine.use_cover_marked(
            lambda client_id: repository.settings.get_cover_with_treasury(
                UserManager.get_user_id(client_id)
            )
        )
        self._engine.use_locked_assets(self._locked_assets_of)
        self._price_impact = PriceImpact(
            settings.id,
            settings.price_impact_enabled,
            settings.price_impact_k,
            settings.price_impact_decay_days,
        )

        # As estratégias ligadas voltam antes do primeiro tick, que já as roda
        self._strategies = StrategyRunner(
            self._engine,
            self._price_impact,
            settings.end_date,
            settings.funds_enabled and backtest is None,
            settings.government_enabled and backtest is None,
        )
        self._strategies.load(
            repository.simulation_player.participants(settings.id), resume_from
        )
        if backtest is not None:
            self._strategies.on_failure = self._backtest_failed
        self._strategies.on_pending_changed = self._pending_changed
        # O crédito de cada conta chega pelo tempo real ao fechar a operação que o mudou
        self._engine.credit_book.on_changed = self._credit_changed

        # Crescimento e desemprego do país: o painel da economia e a aprovação leem o mesmo curso
        self._macro = MacroCourse(settings.start_date)
        # O dólar da partida parte da história: a PTAX e, depois dela, a paridade do curso
        self._engine.use_dollar_history(lambda day: history_dollar(day, self._macro))

        # Expansão Governo & Política: o estado político volta dos eventos gravados
        self._government = (
            GovernmentBook(
                settings,
                self._engine,
                self._take_office,
                self._pay_legacy,
                lambda day, headline: news.publish(settings.id, day, headline),
                random_seed,
                self._macro,
                self._government_changed,
                repository.state_company.of_simulation(settings.id),
                repository.sovereign_fund.ensure(settings.id),
                repository.sovereign_fund.flows(settings.id),
                on_leave_office=self._leave_office,
            )
            if settings.government_enabled and backtest is None
            else None
        )

        # Expansão Gestoras: as gestoras e as cotas delas voltam dos registros gravados
        self._funds = (
            FundBook(
                settings.id,
                self._engine,
                self._client_of_user,
                lambda day, headline: news.publish(settings.id, day, headline),
                self._manager_frozen_until,
                self._participants,
                # Na aquisição hostil a assembleia espera o fim da carência, e nela o
                # gestor passa a ter no máximo a fração do mercado que sobra do mínimo
                add_months(settings.start_date, settings.fund_grace_months)
                if settings.is_fund_takeover
                else None,
                1 - settings.fund_min_market_share
                if settings.is_fund_takeover
                else None,
                self._strategies.is_active,
                self._stop_fund_strategy,
                (lambda: repository.simulation_player.teams(settings.id))
                if settings.is_takeover_teams
                else None,
            )
            if settings.funds_enabled and backtest is None
            else None
        )
        # A estratégia de cada gestora volta com a carteira dela, antes do primeiro tick
        if self._funds is not None:
            self._strategies.load_funds(
                {fund.terms.id: fund.account.client_id for fund in self._funds.funds()},
                resume_from,
            )
        # O caixa da gestora chega, pelo tempo real, ao gestor que a gere; o do Fundo Soberano, ao presidente
        self._engine.use_account_route(self._account_route)
        self._engine.on_cash_moved = self._cash_moved
        # A casa emite o CDB de cada Bancário com o teto que a renda dele no mês pede
        self._engine.fixed_income_market.use_house_cdb(self._house_cdb_caps)
        if self._government is not None:
            self._government.use_fund_lookup(self._fund_quotas_of)
        if self._funds is not None:
            # Toda captação de gestora paga a comissão aos Banqueiros de ofertas da partida
            self._engine.use_offer_bankers(self._bankers_of_offers)

        # No livro de ofertas, a conta pessoal e as gestoras de um jogador têm o mesmo dono
        self._engine.matching_engine.owner_of = self._account_owners

        # O noticiário lê as séries de cada pregão e entrega as manchetes ao jornal
        self._newsroom = (
            Newsroom(
                settings.id,
                lambda: self._engine.classification,
                lambda day, headline: news.publish(settings.id, day, headline),
                self._government_inflation,
            )
            if backtest is None
            else None
        )

        # As abas das Estatísticas desta partida, montadas uma vez por mês
        self.statistics = ReportCache()

        self._summaries = SummaryDelivery(settings.id, settings.start_date)

        # Fora da Clássica: onde cada um está na meta e se alguém já chegou
        self._goal_progress: GoalProgressDTO | None = None
        self._goal_reached = False
        # Modo aquisição hostil: os eliminados que já perderam o automático e o aviso de que
        # restou um único jogador ativo, que encerra a partida no tick seguinte
        self._eliminations_handled: set[int] = (
            set(self._funds.eliminated) if self._funds is not None else set()
        )
        self._last_standing = False

        # Os snapshots do último pregão são a base da avaliação final das conquistas
        self._achievements = AchievementEvaluator(
            settings,
            self._engine.assess_income_tax,
            self._portfolio_starting_cash,
        )
        # portfolio_id -> o capital inicial do jogador; ele não muda depois que a carteira abre
        self._portfolio_cash: dict[int, Decimal] = {}
        # user_id -> o snapshot do último pregão
        self._last_snapshots: dict[int, SnapshotDTO] = {}

        # O mês do último dia processado já recebeu o aporte
        self._last_contribution_month: tuple[int, int] | None = (
            (resume_from.year, resume_from.month) if resume_from else None
        )

        # Configura os alias
        self.get_cash = self._engine.get_cash

        # Roda o primeiro tick para a inicialização
        self.next_tick()

    @property
    def lock(self) -> threading.RLock:
        return self._engine._lock

    @synchronized
    def get_fixed_assets(self) -> list[FixedIncomeAssetDTO]:
        return self._engine.fixed_income_market.get_available_assets()

    @synchronized
    def get_fixed_asset(
        self, client_id: UUID, asset_uuid: str
    ) -> FixedIncomeAssetDTO | None:
        """O título como `client_id` o enxerga: o CDB da casa de outro jogador não existe para ele."""
        return self._engine.fixed_income_market.get_asset(client_id, asset_uuid)

    @synchronized
    def get_portfolio(self, client_id: UUID):
        return self._engine.get_portfolio(client_id)

    @synchronized
    def get_fixed_positions(self, client_id: UUID):
        return self._engine.fixed_broker.get_fixed_positions(client_id)

    @synchronized
    def create_order(
        self, order: Order, *, fill_max: bool = False, by_policy: bool = False
    ) -> None:
        # A política da profissão do bot opera ao lado da estratégia dele; só a boleta do jogador exige o manual
        if by_policy:
            self._ensure_can_trade(order.client_id)
        else:
            self._ensure_can_operate(order.client_id)
        if self._funds is not None and self._funds.is_merged(order.ticker):
            raise ConflictError("A gestora foi incorporada e a cota deixou o mercado.")
        if (
            order.action is OrderAction.BUY
            and self._funds is not None
            and order.client_id in self._funds.client_ids
            and self._engine.asset_class(order.ticker) is AssetClass.FUND
        ):
            raise ConflictError("A gestora não compra cota de gestora.")
        # O limite inteiro (a intenção Máx) e a compra por valor ganham a quantidade com o caixa,
        # a posição e o book de agora, no mesmo lock da execução
        if fill_max:
            self._engine.size_max_order(order)
        elif isinstance(order, MarketOrder) and order.budget is not None:
            self._engine.size_budget_order(order)
        self._ensure_sovereign_order(order)
        self._engine.check_quantity(order.ticker, order.size)
        try:
            self._engine.matching_engine.submit(order)
        finally:
            # Mesmo uma execução parcial precisa aparecer sem esperar outro tick.
            EventManager.flush()
            # A página da gestora muda com o negócio da cota (preço e cotistas) e com o da carteira dela
            if self._funds is not None and (
                self._engine.asset_class(order.ticker) is AssetClass.FUND
                or self._funds.of_client(order.client_id) is not None
            ):
                self._notify_funds_update()

    @synchronized
    def cancel_order(self, *, order_id: str, client_id: UUID) -> bool:
        self._ensure_can_operate(client_id)
        canceled = self._engine.matching_engine.cancel(
            order_id=order_id, client_id=client_id
        )
        EventManager.flush()
        return canceled

    @synchronized
    def cancel_open_orders(self) -> int:
        """Cancela as ordens abertas de todos os jogadores, devolvendo as reservas."""
        return self._engine.matching_engine.cancel_all()

    @synchronized
    def buy_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, value: Decimal
    ) -> None:
        self._ensure_can_operate(client_id)
        self._buy_fixed_income(client_id, asset, value)

    def _buy_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, value: Decimal
    ) -> None:
        """A compra de renda fixa das rotas dos jogadores e da política do bot, com as mesmas travas de conta e de teto."""
        self._ensure_not_sovereign(client_id)
        self._engine.fixed_broker.buy(client_id, asset, value)
        EventManager.flush()

    @synchronized
    def redeem_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, net_amount: Decimal
    ) -> None:
        self._ensure_can_operate(client_id)
        self._ensure_not_sovereign(client_id)
        self._engine.fixed_broker.redeem(client_id, asset, net_amount)
        EventManager.flush()

    @synchronized
    def get_strategies(self, for_fund: bool = False) -> list[StrategyInfoDTO]:
        return self._strategies.infos(self._current_date, for_fund=for_fund)

    @synchronized
    def get_my_strategy(self, user: UserDTO) -> MyStrategyDTO:
        return self._strategies.mine(StrategyAccount.of_user(user), self._current_date)

    @synchronized
    def set_my_strategy(
        self,
        user: UserDTO,
        key: str | None,
        params: dict[str, StrategyParamValue],
    ) -> None:
        if key is not None:
            self._ensure_can_trade(user.client_id)
        self._strategies.set_mode(
            StrategyAccount.of_user(user), key, params, self._current_date
        )

    @synchronized
    def mark_strategy_error_seen(self, user: UserDTO) -> None:
        self._strategies.mark_error_seen(user, self._current_date)

    @synchronized
    def get_strategy_signal(
        self, key: str, params: dict[str, StrategyParamValue], ticker: str
    ) -> SignalDTO:
        return self._strategies.signal(key, params, ticker, self._current_date)

    @synchronized
    def get_strategy_view(
        self, user: UserDTO, key: str, params: dict[str, StrategyParamValue]
    ) -> StrategyViewDTO:
        return self._strategies.view(
            StrategyAccount.of_user(user), key, params, self._current_date
        )

    @synchronized
    def get_strategy_log(
        self, user: UserDTO, kind: LogFilter, before: int | None, limit: int
    ) -> StrategyLogPageDTO:
        return self._strategies.log(StrategyAccount.of_user(user), kind, before, limit)

    @synchronized
    def get_fund_strategy(self, user: UserDTO, fund_id: int) -> MyStrategyDTO:
        fund = self._operated_fund(user, fund_id)
        return self._strategies.mine(self._fund_account(user, fund), self._current_date)

    @synchronized
    def set_fund_strategy(
        self,
        user: UserDTO,
        fund_id: int,
        key: str | None,
        params: dict[str, StrategyParamValue],
    ) -> None:
        """Liga, troca ou desliga a estratégia da carteira da gestora; vale também com a carteira congelada pela presidência."""
        fund = self._operated_fund(user, fund_id)
        self._strategies.set_mode(
            self._fund_account(user, fund), key, params, self._current_date
        )
        self._notify_funds_update()

    @synchronized
    def get_fund_strategy_view(
        self,
        user: UserDTO,
        fund_id: int,
        key: str,
        params: dict[str, StrategyParamValue],
    ) -> StrategyViewDTO:
        fund = self._operated_fund(user, fund_id)
        return self._strategies.view(
            self._fund_account(user, fund), key, params, self._current_date
        )

    @synchronized
    def get_fund_strategy_log(
        self,
        user: UserDTO,
        fund_id: int,
        kind: LogFilter,
        before: int | None,
        limit: int,
    ) -> StrategyLogPageDTO:
        fund = self._operated_fund(user, fund_id)
        return self._strategies.log(self._fund_account(user, fund), kind, before, limit)

    def _operated_fund(self, user: UserDTO, fund_id: int) -> Fund:
        """A gestora cuja carteira o jogador opera, como principal ou co-gestor ativo; quem governa o país não a opera."""
        self._ensure_not_eliminated(user)
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        if user.id not in book.operators(fund):
            raise ForbiddenError("Só quem gere a gestora liga o automático dela.")
        if (
            user.id != fund.terms.manager_user_id
            and self._manager_frozen_until(user.id) is not None
        ):
            raise ConflictError(
                "Você governa o país: a carteira da gestora fica congelada até o fim do mandato."
            )
        return fund

    @staticmethod
    def _fund_account(user: UserDTO, fund: Fund) -> StrategyAccount:
        return StrategyAccount(
            user.id, fund.account.client_id, fund.terms.id, user.nickname
        )

    def _stop_fund_strategy(self, fund: Fund, reason: str) -> None:
        """A gestora volta ao manual quando o principal muda; o registro guarda o motivo."""
        self._strategies.set_mode(
            StrategyAccount(
                fund.terms.manager_user_id, fund.account.client_id, fund.terms.id
            ),
            None,
            {},
            self._current_date,
            reason=reason,
        )

    @synchronized
    def get_election(self, user: UserDTO) -> ElectionPanelDTO:
        book = self._ensure_government()
        networths = {
            user_id: snapshot.total_networth
            for user_id, snapshot in self._last_snapshots.items()
        }
        return build_panel(
            book,
            self.settings,
            repository.simulation_player.participants(self.settings.id),
            user,
            self._current_date,
            networths,
        )

    @synchronized
    def get_map(self, user: UserDTO) -> MapPanelDTO:
        book = self._ensure_government()
        # Os números de campanha chegam a hoje com a queda do tempo aplicada
        book.state.advance(self._current_date)
        return build_map(book, self.settings, user, self._current_date)

    @synchronized
    def get_map_timeline(self, year: int | None) -> MapTimelineDTO:
        book = self._ensure_government()
        book.state.advance(self._current_date)
        return build_timeline(book, self.settings, self._current_date, year)

    @synchronized
    def get_campaign(self, user: UserDTO) -> CampaignPanelDTO:
        return build_campaign(
            self._ensure_government(),
            repository.simulation_player.participants(self.settings.id),
            user,
            self._current_date,
        )

    @synchronized
    def get_campaign_history(self, user: UserDTO) -> CampaignHistoryDTO:
        return build_history(
            self._ensure_government(),
            repository.simulation_player.participants(self.settings.id),
            user,
            self._current_date,
        )

    @synchronized
    def campaign_action(
        self, user: UserDTO, request: CampaignActionRequest
    ) -> CampaignRollDTO:
        book = self._ensure_government()
        result = book.campaign_action(
            user, self._current_date, request.action, request.group, request.rival_id
        )
        return build_roll(
            book,
            repository.simulation_player.participants(self.settings.id),
            user,
            self._current_date,
            result,
        )

    @synchronized
    def get_promises(self, user: UserDTO) -> PromisesPanelDTO:
        return build_promises_panel(
            self._ensure_government(),
            user,
            self._current_date,
            sector_options(self._engine),
        )

    @synchronized
    def preview_promises(
        self, user: UserDTO, request: PromisesRequest
    ) -> PromisesPreviewDTO:
        book = self._ensure_government()
        drafts = book.draft_promises(user, self._current_date, request.promises)
        return build_preview(book, user, self._current_date, drafts)

    @synchronized
    def set_promises(self, user: UserDTO, request: PromisesRequest) -> None:
        self._ensure_government().set_promises(
            user, self._current_date, request.promises
        )

    @synchronized
    def get_balances(self, user: UserDTO) -> list[BalanceDTO]:
        return build_balances(self._ensure_government(), user)

    @synchronized
    def found_party(self, user: UserDTO, party: FoundPartyRequest) -> None:
        self._ensure_government().found_party(
            user,
            self._current_date,
            name=party.name,
            abbr=party.abbr,
            color=party.color,
            flags=party.flags,
            contribution=party.contribution,
            congress=party.congress,
        )

    @synchronized
    def set_party_flags(self, user: UserDTO, flags: list[VoterValue]) -> None:
        self._ensure_government().set_flags(user, self._current_date, flags)

    @synchronized
    def join_party(
        self, user: UserDTO, party_id: int, contribution: Decimal, congress: Decimal
    ) -> None:
        self._ensure_government().join_party(
            user, self._current_date, party_id, contribution, congress
        )

    @synchronized
    def leave_party(self, user: UserDTO) -> None:
        self._ensure_government().leave_party(user, self._current_date)

    @synchronized
    def set_contribution(
        self, user: UserDTO, contribution: Decimal, congress: Decimal
    ) -> None:
        self._ensure_government().set_contribution(
            user, self._current_date, contribution, congress
        )

    @synchronized
    def guide_bloc(
        self,
        user: UserDTO,
        measure_id: int | None,
        yes: bool,
        break_deal: bool = False,
    ) -> None:
        self._ensure_government().guide(
            user, self._current_date, measure_id, yes, break_deal
        )

    @synchronized
    def request_impeachment(self, user: UserDTO) -> None:
        self._ensure_government().request_impeachment(user, self._current_date)

    @synchronized
    def get_base(self, user: UserDTO) -> CongressBaseDTO:
        return build_base(
            self._ensure_government(),
            repository.simulation_player.participants(self.settings.id),
            user,
            self._current_date,
        )

    @synchronized
    def preview_deal(self, bloc_key: int) -> DealPreviewDTO:
        return build_deal_preview(
            self._ensure_government(),
            repository.simulation_player.participants(self.settings.id),
            self._current_date,
            bloc_key,
        )

    @synchronized
    def propose_deal(self, user: UserDTO, bloc_key: int) -> None:
        self._ensure_government().propose_deal(user, self._current_date, bloc_key)

    @synchronized
    def withdraw_deal(self, user: UserDTO, deal_id: int) -> None:
        self._ensure_government().withdraw_deal(user, self._current_date, deal_id)

    @synchronized
    def answer_deal(
        self,
        user: UserDTO,
        accept: bool,
        sector: str | None = None,
        segment: str | None = None,
    ) -> None:
        self._ensure_government().answer_deal(
            user, self._current_date, accept, sector, segment
        )

    @synchronized
    def answer_demand(self, user: UserDTO, deal_id: int, accept: bool) -> None:
        self._ensure_government().answer_demand(
            user, self._current_date, deal_id, accept
        )

    @synchronized
    def break_deal(self, user: UserDTO, deal_id: int) -> None:
        self._ensure_government().break_deal(user, self._current_date, deal_id)

    @synchronized
    def leave_base(self, user: UserDTO) -> None:
        self._ensure_government().leave_base(user, self._current_date)

    @synchronized
    def set_guidance_rule(self, user: UserDTO, value: VoterValue, yes: bool) -> None:
        self._ensure_government().set_guidance_rule(
            user, self._current_date, value, yes
        )

    @synchronized
    def expel_member(self, founder: UserDTO, nickname: str) -> None:
        self._ensure_government().expel(
            founder,
            self._current_date,
            nickname,
            repository.simulation_player.participants(self.settings.id),
        )

    @synchronized
    def set_ticket(self, founder: UserDTO, candidate: str) -> None:
        self._ensure_government().set_ticket(
            founder,
            self._current_date,
            candidate,
            repository.simulation_player.participants(self.settings.id),
        )

    @synchronized
    def invite_vice(self, founder: UserDTO, vice: str) -> None:
        self._ensure_government().invite_vice(
            founder,
            self._current_date,
            vice,
            repository.simulation_player.participants(self.settings.id),
        )

    @synchronized
    def withdraw_vice(self, founder: UserDTO) -> None:
        self._ensure_government().withdraw_vice(founder, self._current_date)

    @synchronized
    def answer_vice(self, user: UserDTO, party_id: int, accept: bool) -> None:
        self._ensure_government().answer_vice(
            user, self._current_date, accept, party_id
        )

    @synchronized
    def preview_federation(
        self, user: UserDTO, partner_id: int, candidate_party_id: int
    ) -> FederationPreviewDTO:
        book = self._ensure_government()
        return preview_dto(
            book,
            book.federation_preview(
                user, self._current_date, partner_id, candidate_party_id
            ),
        )

    @synchronized
    def propose_federation(
        self,
        founder: UserDTO,
        partner_id: int,
        name: str,
        candidate_party_id: int,
        candidate: str | None,
    ) -> None:
        self._ensure_government().propose_federation(
            founder,
            self._current_date,
            partner_id,
            name,
            candidate_party_id,
            candidate,
            repository.simulation_player.participants(self.settings.id),
        )

    @synchronized
    def withdraw_federation(self, founder: UserDTO) -> None:
        self._ensure_government().withdraw_federation(founder, self._current_date)

    @synchronized
    def answer_federation(self, user: UserDTO, proposal_id: int, accept: bool) -> None:
        self._ensure_government().answer_federation(
            user, self._current_date, accept, proposal_id
        )

    @synchronized
    def leave_federation(self, founder: UserDTO) -> None:
        self._ensure_government().leave_federation(founder, self._current_date)

    @synchronized
    def donate_to_party(self, user: UserDTO, party_id: int, amount: Decimal) -> None:
        self._ensure_government().donate(user, self._current_date, party_id, amount)

    @synchronized
    def endorse(self, user: UserDTO, party_id: int | None) -> None:
        self._ensure_government().endorse(user, self._current_date, party_id)

    @synchronized
    def contribute_runoff(self, user: UserDTO, amount: Decimal) -> None:
        self._ensure_government().contribute_runoff(user, self._current_date, amount)

    @synchronized
    def get_governance(self, user: UserDTO) -> GovernmentPanelDTO:
        return build_governance(
            self._ensure_government(),
            self._engine,
            repository.simulation_player.participants(self.settings.id),
            user,
            self._current_date,
            self._presidential_pay,
        )

    @synchronized
    def get_government_status(self, user: UserDTO) -> GovernmentStatusDTO:
        return build_government_status(
            self._ensure_government(),
            self._current_date,
            user,
            self._presidential_pay,
        )

    @synchronized
    def get_budget(self) -> BudgetDTO:
        book = self._ensure_government()
        return build_budget(
            book.budget(),
            book.policy(self._current_date),
            self._current_date,
            book.term_end(),
            book.amendment_lines(self._current_date),
        )

    @synchronized
    def propose_measure(self, user: UserDTO, measure: ProposeMeasureRequest) -> None:
        self._ensure_government().propose(
            user,
            self._current_date,
            measure.kind,
            measure.value,
            measure.sector,
            measure.segment,
            measure.name,
            measure.ticker,
            measure.size,
            measure.lever,
        )

    @synchronized
    def preview_measure(
        self, user: UserDTO, measure: ProposeMeasureRequest
    ) -> MeasurePreviewDTO:
        return self._ensure_government().preview(
            user,
            self._current_date,
            measure.kind,
            measure.value,
            measure.sector,
            measure.segment,
            measure.name,
            measure.ticker,
            measure.size,
            measure.lever,
        )

    @synchronized
    def get_state_companies(self, user: UserDTO) -> StateCompaniesPanelDTO:
        return self._ensure_government().state_panel(
            user, self._current_date, SimulationManager.get_portfolio_id(user.id)
        )

    @synchronized
    def get_state_company_detail(
        self, user: UserDTO, ticker: str
    ) -> StateCompanyDetailDTO | None:
        """A estatal na tela da ação; None quando a partida não usa o governo ou o código não é de estatal."""
        if self._government is None:
            return None
        try:
            portfolio_id = SimulationManager.get_portfolio_id(user.id)
        except NotFoundError:
            portfolio_id = None
        return self._government.state_detail(self._current_date, ticker, portfolio_id)

    @synchronized
    def preview_state_order(self, user: UserDTO, ticker: str) -> StateOrderPreviewDTO:
        return self._ensure_government().state_order_preview(
            user, self._current_date, ticker
        )

    @synchronized
    def preview_state_founding(
        self, user: UserDTO, request: FoundStateCompanyRequest
    ) -> StateFoundingPreviewDTO:
        return self._ensure_government().state_founding_preview(
            user,
            self._current_date,
            request.name,
            request.ticker,
            request.size,
            request.lever,
        )

    @synchronized
    def get_sovereign_fund(self, user: UserDTO) -> SovereignFundPanelDTO:
        return self._ensure_government().sovereign_panel(user)

    @synchronized
    def preview_sovereign_contribution(
        self, user: UserDTO, request: SovereignContributionRequest
    ) -> SovereignContributionPreviewDTO:
        return self._ensure_government().sovereign_contribution_preview(
            user, self._current_date, request.value
        )

    @synchronized
    def set_state_order(
        self, user: UserDTO, ticker: str, request: StateOrderRequest
    ) -> None:
        self._ensure_government().set_state_order(
            user,
            self._current_date,
            ticker,
            request.control,
            request.dividend_policy,
        )

    @synchronized
    def reserve_state_offer(
        self, user: UserDTO, request: StateReservationRequest
    ) -> None:
        self._ensure_not_eliminated(user)
        self._ensure_government().reserve_state_offer(
            request.ticker,
            SimulationManager.get_portfolio_id(user.id),
            Decimal(request.quantity),
            self._current_date,
        )

    @synchronized
    def set_selic(self, user: UserDTO, selic: Decimal | None) -> None:
        self._ensure_government().set_selic(user, self._current_date, selic)

    @synchronized
    def withdraw_measure(self, user: UserDTO, measure_id: int) -> None:
        self._ensure_government().withdraw(user, self._current_date, measure_id)

    @synchronized
    def repropose_measure(self, user: UserDTO, measure_id: int) -> None:
        self._ensure_government().repropose(user, self._current_date, measure_id)

    # =========================
    # Gestoras
    # =========================

    @synchronized
    def acting_client(self, client_id: UUID, fund_id: int | None) -> UUID:
        """O client_id que opera no mercado: o do jogador, o da gestora que ele gere ou co-gere ou, ao presidente, o do Fundo Soberano."""
        if fund_id is None:
            return client_id
        if fund_id == fund_rules.ACCOUNT_ID:
            return self._acting_sovereign(client_id)
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        for user_id in book.operators(fund):
            if user_id in book.eliminated:
                continue
            if self._client_of_user(user_id) != client_id:
                continue
            # O co-gestor que governa o país não opera a gestora: o congelamento vale para ele
            if (
                user_id != fund.terms.manager_user_id
                and self._manager_frozen_until(user_id) is not None
            ):
                raise ConflictError(
                    "Você governa o país: a carteira da gestora fica congelada até o fim do mandato."
                )
            return fund.account.client_id
        raise ForbiddenError("Só quem gere a gestora opera a conta dela.")

    def _fund_quotas_of(self, ticker: str) -> FundQuotas | None:
        """A gestora dona da cota `ticker`: nome, cotas emitidas e sigla do partido do gestor; nulo se não é cota."""
        if self._funds is None:
            return None
        try:
            fund = self._funds.get(ticker)
        except KeyError:
            return None
        return FundQuotas(
            fund.terms.name,
            fund.account.quotas,
            self._party_of(fund.terms.manager_user_id),
        )

    def _ensure_sovereign_order(self, order: Order) -> None:
        """A compra do Fundo Soberano é só de ação e cota de gestora, com número de papéis conhecido, até o teto de fatia e o caixa que o aporte deu."""
        government = self._government
        if government is None or order.action is not OrderAction.BUY:
            return
        client_id = government.sovereign_fund().client_id
        if order.client_id != client_id:
            return
        asset_class = self._engine.asset_class(order.ticker)
        if asset_class not in (AssetClass.STOCK, AssetClass.FUND):
            raise ConflictError("O Fundo Soberano compra só ações e cotas de gestora.")
        _, issued, _ = government.issued_of(order.ticker)
        if not issued:
            raise ConflictError(
                "Sem o número de ações em circulação, o fundo não compra esta empresa."
            )
        held = self._fund_holding(client_id, order.ticker)
        room = fund_rules.room(held, issued)
        if order.size > room:
            raise ConflictError(
                f"O fundo não passa de {fund_rules.CEILING:.0%} do que existe: "
                f"cabem mais {format_quantity(room.to_integral_value(ROUND_FLOOR))} "
                "dessa compra."
            )

    def _fund_holding(self, client_id: UUID, ticker: str) -> Decimal:
        """O que a conta do fundo tem do ativo contando as ordens abertas de compra: é a base do teto de fatia."""
        position = self._engine.broker.get_positions(client_id).get(ticker)
        resting = sum(
            (
                open_order.remaining
                for open_order in self._engine.matching_engine.order_book.orders_of(
                    client_id
                )
                if open_order.ticker == ticker and open_order.action is OrderAction.BUY
            ),
            Decimal(0),
        )
        return (position.size if position is not None else Decimal(0)) + resting

    def _sovereign_preview(
        self, client_id: UUID, ticker: str, quantity: Decimal
    ) -> SovereignOrderPreviewDTO | None:
        """A fatia do fundo no ativo antes e depois da compra, o que cabe sob o teto e o que impede a compra; nulo fora da conta do fundo."""
        government = self._government
        if government is None or client_id != government.sovereign_fund().client_id:
            return None
        name, issued, is_fund = government.issued_of(ticker)
        asset_class = self._engine.asset_class(ticker)
        refusal = None
        if asset_class not in (AssetClass.STOCK, AssetClass.FUND):
            refusal = "O Fundo Soberano compra só ações e cotas de gestora."
        elif not issued:
            refusal = (
                "Sem o número de ações em circulação, o fundo não compra esta empresa."
            )
        held = self._fund_holding(client_id, ticker)
        return SovereignOrderPreviewDTO(
            issuer=name,
            is_fund=is_fund,
            stake_before=fund_rules.stake(held, issued) if issued else None,
            stake_after=fund_rules.stake(held + quantity, issued) if issued else None,
            ceiling=fund_rules.CEILING,
            room=fund_rules.room(held, issued) if issued else None,
            allied=government.is_allied_manager(ticker, self._current_date),
            refusal=refusal,
        )

    def _ensure_not_sovereign(self, client_id: UUID) -> None:
        """O Fundo Soberano não tem renda fixa nem Tesouro Direto."""
        government = self._government
        if (
            government is not None
            and client_id == government.sovereign_fund().client_id
        ):
            raise ConflictError("O Fundo Soberano compra só ações e cotas de gestora.")

    def _acting_sovereign(self, client_id: UUID) -> UUID:
        """O Fundo Soberano é do cargo: só o presidente em exercício opera a conta dele."""
        government = self._ensure_government()
        president = government.president()
        if (
            president is None
            or president.client_id != client_id
            or not government.governs()
        ):
            raise ForbiddenError("Só o presidente em exercício opera o Fundo Soberano.")
        return government.sovereign_fund().client_id

    def _account_route(self, client_id: UUID) -> tuple[tuple[UUID, ...], int] | None:
        """Quem recebe o tempo real de uma conta de gestora ou do Fundo Soberano; nulo nas demais."""
        government = self._government
        if government is not None and (
            client_id == government.sovereign_fund().client_id
        ):
            president = government.president()
            audience = () if president is None else (president.client_id,)
            return audience, fund_rules.ACCOUNT_ID
        return self._funds.audience_of(client_id) if self._funds is not None else None

    @synchronized
    def get_fund_accounts(self, user: UserDTO) -> list[FundAccountDTO]:
        """As contas do jogador: a pessoal, cada gestora que ele gere ou co-gere e, ao presidente, o Fundo Soberano."""
        book = self._funds
        if book is None and self._government is None:
            book = self._ensure_funds()
        accounts = [
            FundAccountDTO(
                fund_id=None,
                name="Conta pessoal",
                ticker=None,
                cash=self._engine.get_cash(user.client_id),
                frozen_until=self._manager_frozen_until(user.id),
                eliminated_on=book.eliminated.get(user.id) if book else None,
                role=None,
            )
        ]
        government = self._government
        if government is not None:
            president = government.president()
            if president is not None and president.id == user.id:
                accounts.append(
                    FundAccountDTO(
                        fund_id=fund_rules.ACCOUNT_ID,
                        name=fund_headlines.FUND,
                        ticker=None,
                        cash=self._engine.get_cash(
                            government.sovereign_fund().client_id
                        ),
                        frozen_until=None,
                        role="president",
                    )
                )
        for fund in book.operated_by(user.id) if book is not None else []:
            is_manager = fund.terms.manager_user_id == user.id
            accounts.append(
                FundAccountDTO(
                    fund_id=fund.terms.id,
                    name=fund.terms.name,
                    ticker=fund.ticker,
                    cash=self._engine.get_cash(fund.account.client_id),
                    # O co-gestor que governa congela com o país, o principal com a carteira da gestora
                    frozen_until=required(book).portfolio_frozen_until(fund)
                    if is_manager
                    else self._manager_frozen_until(user.id),
                    automatic=required(book).automatic(fund),
                    role="manager" if is_manager else "comanager",
                )
            )
        return accounts

    @synchronized
    def check_fund_ticker(self, user: UserDTO, ticker: str) -> FundTickerCheckDTO:
        """Confere a sigla de uma gestora sem alterar nada: formato, ativo (as quatro letras), gestora de outro jogador da partida ou livre."""
        book = self._ensure_funds()
        if re.fullmatch(FUND_TICKER_PATTERN, ticker) is None:
            return FundTickerCheckDTO(ticker=ticker, status="format", owner_name=None)
        if repository.fund.letters_taken_by_asset(ticker) or (
            self._government is not None and self._government.founding_reserves(ticker)
        ):
            return FundTickerCheckDTO(ticker=ticker, status="asset", owner_name=None)
        founder_id = book.founder_of(ticker)
        if founder_id is not None and founder_id != user.id:
            return FundTickerCheckDTO(
                ticker=ticker,
                status="fund",
                owner_name=self._nickname_of(founder_id),
            )
        return FundTickerCheckDTO(ticker=ticker, status="free", owner_name=None)

    @synchronized
    def get_funds(self, user: UserDTO) -> list[FundRoomItemDTO]:
        """As gestoras da sala, cada uma com as cotas e o papel de `user`."""
        book = self._ensure_funds()
        summaries = book.summaries()
        positions = self._engine.broker.get_positions(user.client_id)
        nicknames = {p.id: p.nickname for p in book.participants()}
        room: list[FundRoomItemDTO] = []
        for summary in summaries:
            position = positions.get(summary.ticker)
            mine = position.size if position is not None and position.size > 0 else 0
            comanagers = [
                c.user_id
                for c in book.by_id(summary.id).comanagers
                if c.status is FundComanagerStatus.ACTIVE
            ]
            room.append(
                FundRoomItemDTO(
                    **summary.model_dump(),
                    my_quotas=Decimal(mine),
                    comanager_nicknames=[
                        nicknames[uid] for uid in comanagers if uid in nicknames
                    ],
                    i_comanage=user.id in comanagers,
                )
            )
        return room

    @synchronized
    def get_fund_offers(self, user: UserDTO) -> FundOffersDTO:
        """As ofertas públicas como `user` as vê: a preferência dele, as abertas a todos e as encerradas."""
        book = self._ensure_funds()
        return FundOffersBuilder(book, self._engine.current_date).build(user)

    @synchronized
    def get_fund(self, user: UserDTO, fund_id: int) -> FundDetailsDTO:
        """A página da gestora como `user` a vê: a carteira viva é só do gestor."""
        book = self._ensure_funds()
        builder = FundDetailsBuilder(
            book,
            self._engine,
            self.settings.id,
            lambda: repository.simulation_player.colors(self.settings.id),
            self._issuance_estimator(book),
        )
        return builder.build(book.by_id(fund_id), user)

    @synchronized
    def get_fund_report(self, fund_id: int, month: date) -> FundMonthlyReportDTO:
        """O relatório de um mês fechado da gestora; qualquer jogador da sala lê."""
        book = self._ensure_funds()
        builder = FundDetailsBuilder(
            book,
            self._engine,
            self.settings.id,
            lambda: repository.simulation_player.colors(self.settings.id),
            self._issuance_estimator(book),
        )
        return builder.monthly_report(book.by_id(fund_id), month)

    @synchronized
    def found_fund(self, user: UserDTO, request: FundFoundRequest) -> FundSummaryDTO:
        self._ensure_not_eliminated(user)
        book = self._ensure_funds()
        if self._government is not None and self._government.founding_reserves(
            request.ticker
        ):
            raise ConflictError("As quatro letras deste ticker já são de um ativo")
        # Quem tem gestora, inclusive a congelada ou em licença pela presidência, não funda outra
        if book.held_by(user.id):
            raise ConflictError(
                "Fundar exige não ter gestora: você já tem uma. Quem perde a gestora "
                "(assembleia ou compra do controle) pode fundar outra."
            )
        blocked_until = book.founding_blocked_until(user.id)
        if blocked_until is not None:
            raise ConflictError(
                "Quem foi afastado da gestão por assembleia só funda outra gestora "
                f"em {short_date(blocked_until)}."
            )
        self._ensure_fees_within_ceiling(
            request.management_fee, request.performance_fee
        )
        fund = book.found(
            ticker=request.ticker,
            name=request.name,
            founder_user_id=user.id,
            manager_user_id=user.id,
            management_fee=request.management_fee,
            performance_fee=request.performance_fee,
        )
        self._notify_funds_update()
        return book.summary(fund)

    @synchronized
    def contribute_to_fund(
        self, user: UserDTO, fund_id: int, request: FundContributionRequest
    ) -> FundContributionResponse:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        stocks = {item.ticker: item.quantity for item in request.stocks}
        if len(stocks) != len(request.stocks):
            raise UnprocessableEntityError(
                "Cada ativo entra uma vez só na integralização"
            )
        quotas = book.contribute(fund.ticker, user.client_id, request.cash, stocks)
        EventManager.flush()
        self._notify_funds_update()
        return FundContributionResponse(quotas=quotas)

    @synchronized
    def pool_cash_into_fund(self, fund_id: int, user: UserDTO) -> None:
        """O caixa de um co-gestor da equipe entra na gestora no 1º dia e vira cotas dele."""
        book = self._ensure_funds()
        cash = self.get_cash(user.client_id)
        if cash > 0:
            book.contribute(book.by_id(fund_id).ticker, user.client_id, cash, {})
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def open_fund_offer(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundSummaryDTO:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        if fund.listed:
            raise ConflictError("A oferta pública abre uma vez só.")
        if fund.account.quotas <= 0:
            raise ConflictError("Integralize antes de abrir a oferta.")
        book.open_offer(fund.ticker, Decimal(quotas))
        EventManager.flush()
        self._notify_funds_update()
        return book.summary(fund)

    @synchronized
    def close_fund_offer(self, user: UserDTO, fund_id: int) -> None:
        fund = self._managed_fund(user, fund_id)
        if fund.account.offer_remaining is None:
            raise ConflictError("A gestora não tem oferta aberta.")
        self._ensure_funds().close_offer(fund.ticker)
        self._notify_funds_update()

    @synchronized
    def announce_fund_issuance(
        self, user: UserDTO, fund_id: int, request: FundIssuanceRequest
    ) -> FundIssuanceDTO:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        issuance = book.announce_issuance(fund.ticker, Decimal(request.quotas))
        EventManager.flush()
        self._notify_funds_update()
        return issuance

    @synchronized
    def subscribe_fund_issuance(
        self, user: UserDTO, fund_id: int, request: FundIssuanceSubscriptionRequest
    ) -> None:
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        self._ensure_can_operate(user.client_id)
        book.subscribe_issuance(fund.ticker, user, Decimal(request.quotas))
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def open_fund_buyback(
        self, user: UserDTO, fund_id: int, request: FundBuybackRequest
    ) -> FundBuybackDTO:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        buyback = book.open_buyback(
            fund.ticker, Decimal(request.quantity), request.max_price
        )
        EventManager.flush()
        self._notify_funds_update()
        return buyback

    @synchronized
    def cancel_fund_buyback(self, user: UserDTO, fund_id: int) -> None:
        fund = self._managed_fund(user, fund_id)
        self._ensure_funds().cancel_buyback(fund.ticker)
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def convene_fund_assembly(
        self, user: UserDTO, fund_id: int, request: FundAssemblyConveneRequest
    ) -> None:
        self._ensure_not_eliminated(user)
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        book.convene_assembly(fund.ticker, user, request.candidate_nickname)
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def propose_fund_fee_increase(
        self, user: UserDTO, fund_id: int, request: FundAssemblyFeeProposalRequest
    ) -> None:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        self._ensure_fees_within_ceiling(
            request.management_fee, request.performance_fee
        )
        book.propose_fee_increase(
            fund.ticker, user, request.management_fee, request.performance_fee
        )
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def propose_fund_merge(
        self, user: UserDTO, fund_id: int, request: FundMergeProposalRequest
    ) -> None:
        book = self._ensure_funds()
        mother = self._managed_fund(user, fund_id)
        daughter = self._managed_fund(user, request.daughter_fund_id)
        book.propose_merge(mother.terms.id, daughter.terms.id, user)
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def preview_fund_merge(
        self, user: UserDTO, fund_id: int, daughter_fund_id: int
    ) -> FundMergePreviewDTO:
        book = self._ensure_funds()
        mother = self._managed_fund(user, fund_id)
        daughter = self._managed_fund(user, daughter_fund_id)
        return book.merge_preview(mother.terms.id, daughter.terms.id)

    @synchronized
    def cancel_fund_assembly(self, user: UserDTO, fund_id: int) -> None:
        book = self._ensure_funds()
        book.cancel_assembly(book.by_id(fund_id).ticker, user)
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def answer_fund_assembly_invite(
        self, user: UserDTO, fund_id: int, accept: bool
    ) -> None:
        self._ensure_not_eliminated(user)
        book = self._ensure_funds()
        book.answer_assembly_invite(book.by_id(fund_id).ticker, user, accept)
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def invite_fund_comanager(
        self, user: UserDTO, fund_id: int, request: FundComanagerInviteRequest
    ) -> None:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id, frozen_ok=True)
        invite = book.invite_comanager(fund.ticker, request.nickname, request.share)
        self._notify_comanager(
            invite.user_id, "invited", fund, user.nickname, invite.future_share
        )

    @synchronized
    def seat_fund_comanager(self, fund_id: int, user_id: int, share: Decimal) -> None:
        """Põe na gestora o co-gestor que o lobby combinou, ativo e com a parte já valendo."""
        book = self._ensure_funds()
        book.seat_comanager(book.by_id(fund_id).ticker, user_id, share)

    @synchronized
    def answer_fund_comanager_invite(
        self, user: UserDTO, fund_id: int, accept: bool
    ) -> None:
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        # O aceite na presidência passa a gestão ao co-gestor: o aviso vai a quem convidou
        inviter_id = fund.terms.manager_user_id
        answered = book.answer_comanager_invite(fund.ticker, user, accept)
        self._notify_comanager(
            inviter_id,
            "accepted" if accept else "declined",
            fund,
            user.nickname,
            answered.future_share,
        )
        self._notify_funds_update()

    @synchronized
    def change_fund_comanager_share(
        self,
        user: UserDTO,
        fund_id: int,
        comanager_user_id: int,
        request: FundComanagerShareRequest,
    ) -> None:
        fund = self._managed_fund(user, fund_id)
        self._ensure_funds().change_comanager_share(
            fund.ticker, comanager_user_id, request.share
        )
        self._notify_funds_update()

    @synchronized
    def remove_fund_comanager(
        self, user: UserDTO, fund_id: int, comanager_user_id: int
    ) -> None:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id, frozen_ok=True)
        removed = book.remove_comanager(fund.ticker, comanager_user_id)
        self._notify_comanager(
            removed.user_id, "removed", fund, user.nickname, removed.future_share
        )

    @synchronized
    def leave_fund_comanagement(self, user: UserDTO, fund_id: int) -> None:
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        book.leave_comanagement(fund.ticker, user)
        self._notify_comanager(
            fund.terms.manager_user_id, "left", fund, user.nickname, None
        )

    def _notify_comanager(
        self,
        recipient_user_id: int,
        kind: ComanagerEventKind,
        fund: Fund,
        nickname: str,
        share: Decimal | None,
    ) -> None:
        """Avisa quem a mudança de co-gestão atinge e atualiza as páginas das gestoras."""
        notify(
            "comanager_update",
            ComanagerEventDTO(
                kind=kind,
                fund_id=fund.terms.id,
                ticker=fund.ticker,
                nickname=nickname,
                share=share,
            ).to_json(),
            to=self._client_of_user(recipient_user_id),
        )
        self._notify_funds_update()

    @synchronized
    def issue_fund_directed(
        self, user: UserDTO, fund_id: int, request: FundDirectedIssuanceRequest
    ) -> FundDirectedIssuanceDTO | None:
        """Emissão dirigida: para si, liquida na hora e devolve nulo; para um co-gestor, devolve a oferta que espera a resposta dele."""
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        quotas = Decimal(request.quotas)
        if request.buyer_nickname is None:
            self._ensure_can_operate(user.client_id)
            book.issue_directed(fund.ticker, user, quotas)
            EventManager.flush()
            self._notify_funds_update()
            return None
        offer = book.offer_directed(fund.ticker, request.buyer_nickname, quotas)
        self._notify_comanager(
            offer.buyer_user_id, "directed_offered", fund, user.nickname, None
        )
        return offer

    @synchronized
    def accept_fund_directed(self, user: UserDTO, fund_id: int) -> None:
        self._ensure_not_eliminated(user)
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        self._ensure_can_operate(user.client_id)
        book.accept_directed(fund.ticker, user)
        EventManager.flush()
        self._notify_comanager(
            fund.terms.manager_user_id, "directed_accepted", fund, user.nickname, None
        )

    @synchronized
    def decline_fund_directed(self, user: UserDTO, fund_id: int) -> None:
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        book.decline_directed(fund.ticker, user)
        self._notify_comanager(
            fund.terms.manager_user_id, "directed_declined", fund, user.nickname, None
        )

    @synchronized
    def cancel_fund_directed(self, user: UserDTO, fund_id: int) -> None:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        offer = book.cancel_directed(fund.ticker)
        self._notify_comanager(
            offer.buyer_user_id, "directed_cancelled", fund, user.nickname, None
        )

    @synchronized
    def preview_fund_directed(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundDirectedIssuancePreviewDTO:
        """A emissão dirigida vista por `user` como comprador: o principal e os co-gestores ativos a consultam."""
        book = self._ensure_funds()
        fund = book.by_id(fund_id)
        if user.id not in book.operators(fund):
            raise ForbiddenError("Só quem gere a gestora consulta a emissão dirigida.")
        return self._fund_previews(user).directed(fund, Decimal(quotas))

    @synchronized
    def vote_fund_assembly(
        self, user: UserDTO, fund_id: int, request: FundAssemblyVoteRequest
    ) -> None:
        self._ensure_not_eliminated(user)
        book = self._ensure_funds()
        book.cast_assembly_vote(
            book.by_id(fund_id).ticker, request.agenda, user, request.in_favor
        )
        EventManager.flush()
        self._notify_funds_update()

    @synchronized
    def preview_fund_issuance(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundIssuancePreviewDTO:
        fund = self._managed_fund(user, fund_id)
        return self._fund_previews(user).issuance(fund, Decimal(quotas))

    @synchronized
    def preview_fund_subscription(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundIssuanceSubscriptionPreviewDTO:
        fund = self._ensure_funds().by_id(fund_id)
        return self._fund_previews(user).subscription(fund, user, Decimal(quotas))

    @synchronized
    def preview_fund_buyback(
        self, user: UserDTO, fund_id: int, quantity: int, max_price: Decimal
    ) -> FundBuybackPreviewDTO:
        fund = self._managed_fund(user, fund_id)
        return self._fund_previews(user).buyback(fund, Decimal(quantity), max_price)

    @synchronized
    def watch_fund_issuance_preview(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundIssuancePreviewDTO:
        """A prévia de agora; o pedido fica registrado e a prévia nova chega pelo aviso `fund_issuance_preview:{fund_id}`."""
        return self._fund_preview_feed.watch(ISSUANCE, user, fund_id, (quotas,))

    @synchronized
    def watch_fund_subscription_preview(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundIssuanceSubscriptionPreviewDTO:
        """A prévia de agora; o pedido fica registrado e a prévia nova chega pelo aviso `fund_subscription_preview:{fund_id}`."""
        return self._fund_preview_feed.watch(SUBSCRIPTION, user, fund_id, (quotas,))

    @synchronized
    def watch_fund_directed_preview(
        self, user: UserDTO, fund_id: int, quotas: int
    ) -> FundDirectedIssuancePreviewDTO:
        """A prévia de agora; o pedido fica registrado e a prévia nova chega pelo aviso `fund_directed_preview:{fund_id}`."""
        return self._fund_preview_feed.watch(DIRECTED, user, fund_id, (quotas,))

    @synchronized
    def watch_fund_merge_preview(
        self, user: UserDTO, fund_id: int, daughter_fund_id: int
    ) -> FundMergePreviewDTO:
        """A prévia de agora; o pedido fica registrado e a prévia nova chega pelo aviso `fund_merge_preview:{fund_id}`."""
        return self._fund_preview_feed.watch(MERGE, user, fund_id, (daughter_fund_id,))

    @synchronized
    def watch_fund_buyback_preview(
        self, user: UserDTO, fund_id: int, quantity: int, max_price: Decimal
    ) -> FundBuybackPreviewDTO:
        """A prévia de agora; o pedido fica registrado e a prévia nova chega pelo aviso `fund_buyback_preview:{fund_id}`."""
        return self._fund_preview_feed.watch(
            BUYBACK, user, fund_id, (quantity, max_price)
        )

    def _fund_previews(self, manager: UserDTO) -> FundPreviewBuilder:
        book = self._ensure_funds()
        return FundPreviewBuilder(
            book, self._engine, manager, self._issuance_estimator(book)
        )

    def _issuance_estimator(self, book: FundBook) -> IssuanceEstimator:
        """A estimativa de captação da sobra: os bots da sala rodam a estratégia sobre o contexto de hoje."""

        def bot_demand(
            ticker: str, reference: FundReference, bias: float, quotas: Decimal
        ) -> Decimal:
            bots = [user for user in book.participants() if user.is_bot]
            return self._strategies.leftover_demand(
                bots, self._current_date, ticker, reference, bias, quotas
            )

        return IssuanceEstimator(book, self._engine, bot_demand)

    @synchronized
    def set_fund_fees(
        self, user: UserDTO, fund_id: int, request: FundFeesRequest
    ) -> FundSummaryDTO:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        self._ensure_fees_within_ceiling(
            request.management_fee, request.performance_fee
        )
        book.set_fees(fund.ticker, request.management_fee, request.performance_fee)
        self._notify_funds_update()
        return book.summary(fund)

    @synchronized
    def set_fund_distribution(
        self, user: UserDTO, fund_id: int, request: FundDistributionRequest
    ) -> FundSummaryDTO:
        book = self._ensure_funds()
        fund = self._managed_fund(user, fund_id)
        book.set_distribution(fund.ticker, request.distribution_rate)
        self._notify_funds_update()
        return book.summary(fund)

    def _notify_funds_update(self) -> None:
        """Marca que as páginas das gestoras mudaram: toda mudança de gestora (pregão, negócio
        da cota, oferta, taxas, congelamento) passa por aqui. A publicação sai ao fechar a
        operação em curso e, sem operação em curso, na hora."""
        with self.lock:
            self._funds_feed.mark()
            self._fund_preview_feed.funds_changed()
            if self._sync_depth == 0:
                self._publish_changed_screens()

    def _cash_moved(
        self,
        audience: tuple[UUID, ...],
        account: int | None,
        event_type: CashflowEventType,
    ) -> None:
        """O caixa de uma conta mexeu: quem a opera recebe o dado que depende dele ao fechar a operação em curso."""
        with self.lock:
            self._cash_feed.cash_moved(audience, account, event_type)
            self._fund_preview_feed.cash_moved(audience, account)
            if self._sync_depth == 0:
                self._publish_changed_screens()

    def _credit_changed(self, client_id: UUID) -> None:
        """O crédito de uma conta mudou: quem a vê recebe o panorama e a lista de pendências ao fechar a operação em curso."""
        with self.lock:
            self._cash_feed.credit_changed(client_id)
            self._cash_feed.pending_changed(self._engine.audience(client_id)[0][:1])
            if self._sync_depth == 0:
                self._publish_changed_screens()

    def _pending_changed(self, client_id: UUID) -> None:
        """A lista de pendências do jogador mudou por algo que não é o caixa."""
        with self.lock:
            self._cash_feed.pending_changed([client_id])
            if self._sync_depth == 0:
                self._publish_changed_screens()

    def _participants(self) -> list[UserDTO]:
        """Os jogadores da partida; numa rodada de publicação, a lista lida uma vez."""
        if not self._publishing_round:
            return repository.simulation_player.participants(self.settings.id)
        if self._participants_snapshot is None:
            self._participants_snapshot = repository.simulation_player.participants(
                self.settings.id
            )
        return self._participants_snapshot

    @contextmanager
    def _publishing(self) -> Generator[None]:
        """Uma rodada de publicação monta o dado de vários assinantes sobre os mesmos jogadores."""
        outermost = not self._publishing_round
        self._publishing_round = True
        try:
            yield
        finally:
            if outermost:
                self._publishing_round = False
                self._participants_snapshot = None

    def _publish_changed_screens(self) -> None:
        # A publicação roda dentro do lock, como uma operação sincronizada: as consultas
        # dela não disparam a publicação de novo
        self._sync_depth += 1
        try:
            with self._publishing():
                self._funds_feed.flush()
                self._cash_feed.flush()
                self._fund_preview_feed.flush()
        finally:
            self._sync_depth -= 1

    def _government_changed(self) -> None:
        """O livro do governo mudou: os painéis e as pendências dos jogadores saem ao fim da
        operação em curso e, sem operação em curso, na hora."""
        with self.lock:
            self._panels_stale = True
            # Convites, pedidos e votações do governo entram e saem da lista de pendências
            self._cash_feed.pending_changed(
                player.client_id for player in UserManager.list_active_players()
            )
            if self._sync_depth == 0:
                self._panels_stale = False
                self._publish_government_panels()
                self._publish_changed_screens()

    @synchronized
    def _publish_government_panels(self) -> None:
        """Leva ao vivo os painéis do país a quem está com a tela aberta (assina o evento do
        painel). O pregão publica uma vez ao fim do dia e cada ação do governo, uma vez ao
        fechar, com o estado já completo."""
        self._government_feed.publish()

    def _ensure_funds(self) -> FundBook:
        if self._funds is None:
            raise ConflictError("Esta partida não usa a expansão Gestoras.")
        return self._funds

    def _ensure_not_eliminated(self, user: UserDTO) -> None:
        """Quem perdeu a assembleia da própria gestora no modo aquisição hostil só assiste."""
        if self._funds is not None and user.id in self._funds.eliminated:
            raise ConflictError(ELIMINATED_MESSAGE)

    def _managed_fund(
        self, user: UserDTO, fund_id: int, *, frozen_ok: bool = False
    ) -> Fund:
        """A gestora de `fund_id`, que só o gestor dela opera.

        Com `frozen_ok`, o gestor também a alcança durante a presidência: é o que convidar e retirar co-gestor pedem.
        """
        self._ensure_not_eliminated(user)
        fund = self._ensure_funds().by_id(fund_id)
        if fund.terms.manager_user_id != user.id:
            raise ForbiddenError("Só o gestor opera esta gestora.")
        if not frozen_ok:
            self._ensure_fund_active(fund)
        return fund

    def _ensure_fund_active(self, fund: Fund) -> None:
        """A gestora do gestor que governa fica congelada até o fim do mandato dele."""
        until = self._ensure_funds().frozen_until(fund)
        if until is not None:
            raise ConflictError(
                "A gestora está congelada enquanto o gestor governa: ela volta a "
                f"operar em {short_date(until + timedelta(days=1))}."
            )

    def _manager_frozen_until(self, user_id: int) -> date | None:
        """O último dia do mandato de `user_id` quando ele é o presidente; sem governo ou sem mandato, nulo."""
        government = self._government
        if government is None:
            return None
        president = government.president()
        if president is None or president.id != user_id:
            return None
        return government.term_end()

    def _nickname_of(self, user_id: int) -> str | None:
        for user in repository.simulation_player.participants(self.settings.id):
            if user.id == user_id:
                return user.nickname
        return None

    def _ensure_fees_within_ceiling(
        self, management_fee: Decimal, performance_fee: Decimal
    ) -> None:
        """As taxas escolhidas cabem nos tetos que o host fixou na partida."""
        settings = self.settings
        if management_fee > settings.fund_max_management_fee:
            raise UnprocessableEntityError(
                "A taxa de administração desta partida vai até "
                f"{format_quantity(settings.fund_max_management_fee * 100)}% ao ano."
            )
        if performance_fee > settings.fund_max_performance_fee:
            raise UnprocessableEntityError(
                "A taxa de performance desta partida vai até "
                f"{format_quantity(settings.fund_max_performance_fee * 100)}% do que passar do CDI."
            )

    def _tax_policy(self) -> TaxPolicy:
        return self._engine.tax_policy_on(self._current_date)

    def _ensure_can_trade(self, client_id: UUID) -> None:
        """A carteira do presidente e a das gestoras dele ficam congeladas durante o mandato."""
        if self._government is not None:
            self._government.ensure_can_trade(client_id)
        if self._funds is not None:
            fund = self._funds.of_client(client_id)
            # Com a estratégia ligada a carteira da gestora opera, e a boleta manual recusa pelo automático
            if fund is not None and not self._funds.automatic(fund):
                self._ensure_fund_active(fund)
            if any(
                self._client_of_user(user_id) == client_id
                for user_id in self._funds.eliminated
            ):
                raise ConflictError(ELIMINATED_MESSAGE)

    def _ensure_can_operate(self, client_id: UUID) -> None:
        self._ensure_can_trade(client_id)
        self._strategies.ensure_manual(client_id)

    def _take_office(self, president: UserDTO, day: date) -> None:
        """Na posse as ordens abertas somem e o automático desliga: a carteira congela, com as gestoras do presidente."""
        self._engine.matching_engine.cancel_all(president.client_id)
        if self._funds is not None:
            self._funds.on_office(president.id)
            self._notify_funds_update()
        self._strategies.set_mode(
            StrategyAccount.of_user(president),
            None,
            {},
            day,
            reason="Você assumiu a presidência: a carteira fica congelada",
        )

    def _leave_office(self, president: UserDTO, day: date) -> None:
        """O presidente deixou a presidência sem reeleição: a gestão das gestoras dele volta a ele.

        É o ponto do fim do mandato, no dia em que o sucessor assume; o que a posse desligou para
        o presidente volta a ele aqui.
        """
        if self._funds is not None:
            self._funds.on_leave_office(president.id)
            self._notify_funds_update()

    def _presidential_pay(self, user: UserDTO, multiple: Decimal, day: date) -> Decimal:
        """O que `multiple` salários do host valem em reais líquidos para `user` no dia; sem o viver de renda não há salário."""
        if self._life is None:
            return Decimal(0)
        budget = self._life.for_profession(self._profession_of(user.id))
        return budget.as_president(multiple).net_salary_on(day)

    def _pay_legacy(self, president: UserDTO, salaries: Decimal) -> Decimal:
        """Credita ao ex-presidente o legado do mandato e devolve o valor pago em reais."""
        amount = self._presidential_pay(president, salaries, self._current_date)
        if amount > 0:
            self._engine.pay_legacy(president.client_id, amount)
        return amount

    def _life_budget(self, life: LifeBudget, user_id: int) -> LifeBudget:
        """O orçamento do jogador no dia: o da profissão dele ou, no cargo de presidente, o do salário da presidência."""
        # O salário do 1º pregão do mês (`_live`) sai antes de `GovernmentBook.on_tick` do mesmo
        # dia, e o governo só passa a valer a partir do dia seguinte à posse: a troca de
        # governo muda a renda do Comissionado no mês seguinte
        budget = self._with_mechanic(
            self._with_party(
                life.for_profession(self._profession_of(user_id)), user_id
            ),
            user_id,
        ).with_profession_start(self._profession_periods(user_id)[-1].start)
        president = self._government.president() if self._government else None
        if president is not None and president.id == user_id:
            return budget.as_president(presidency.SALARY_MULTIPLE)
        return budget

    def _ensure_government(self) -> GovernmentBook:
        if self._government is None:
            raise ConflictError("Esta partida não usa a expansão Governo & Política.")
        return self._government

    @synchronized
    def get_pending(self, user: UserDTO) -> list[PendingDTO]:
        """O que pede ação do jogador agora: as graves primeiro, cada uma some quando a condição acaba."""
        client_id, today = user.client_id, self._current_date
        items = self._engine.credit_book.pending(client_id, today)
        if self._funds is not None:
            # O atraso de parcela da gestora vai ao gestor principal e aponta para a gestora
            for fund in self._funds.managed_by(user.id):
                items += self._engine.credit_book.pending(
                    fund.account.client_id,
                    today,
                    fund=(fund.terms.id, fund.ticker),
                )
        cash = self._engine.get_cash(client_id)
        if cash < 0:
            detail = format_money(cash)
            if self._life is not None:
                detail += (
                    f" · cheque especial a {_overdraft_rate(today) * 100:.1f}% ao mês"
                )
            items.append(registry.pending(PendingType.NEGATIVE_CASH, detail))
        items += self._strategies.pending(user)
        if self._funds is not None:
            items += [
                registry.pending(
                    PendingType.FUND_ASSEMBLY_INVITE,
                    f"{convener} convoca a assembleia da {fund.ticker} e indica você para a gestão · responda até {invite.ends_on:%d/%m}",
                    ref=str(fund.terms.id),
                    title=f"Convite para gerir a {fund.ticker}",
                    fund_id=fund.terms.id,
                )
                for fund, invite, convener in self._funds.invites_for(user)
            ]
            items += [
                registry.pending(
                    PendingType.FUND_ASSEMBLY_VOTE,
                    f"{_agenda_title(assembly)} na {fund.ticker} · vote até {assembly.ends_on:%d/%m}",
                    ref=str(assembly.id),
                    title=(
                        f"Votação na {fund.terms.name}: {self._funds.merge_title(assembly)}"
                        if assembly.agenda is FundAssemblyAgenda.MERGE
                        else f"Votação na {fund.ticker}"
                    ),
                    fund_id=fund.terms.id,
                )
                for fund, assembly in self._funds.open_votes_for(user)
            ]
            items += [
                registry.pending(
                    PendingType.COMANAGER_INVITE,
                    f"{manager} convida você a co-gerir a {fund.ticker} com {format_quantity(invite.future_share * 100)}% das taxas · responda até {last_day:%d/%m}",
                    ref=str(fund.terms.id),
                    title=f"Convite para co-gerir a {fund.ticker}",
                    fund_id=fund.terms.id,
                )
                for fund, invite, manager, last_day in self._funds.comanager_invites_for(
                    user
                )
            ]
            items += [
                registry.pending(
                    PendingType.DIRECTED_ISSUANCE_OFFER,
                    f"{manager} oferece {format_quantity(offer.quotas)} cotas novas da {fund.ticker} · responda até {last_day:%d/%m}",
                    ref=str(fund.terms.id),
                    title=f"Oferta de cotas da {fund.ticker}",
                    fund_id=fund.terms.id,
                )
                for fund, offer, manager, last_day in self._funds.directed_offers_for(
                    user
                )
            ]
            items += [
                registry.pending(
                    PendingType.FUND_DISTRIBUTION_SHORT_CASH,
                    f"O caixa tem {format_money(plan.cash)} e o rendimento projetado é {format_money(plan.projected)} · o pagamento de {plan.pay_on:%d/%m} sai só até o caixa",
                    ref=str(fund.terms.id),
                    title=f"Caixa curto para o rendimento da {fund.ticker}",
                )
                for fund, plan in self._funds.short_cash_plans(user)
            ]
        if self._government is not None:
            items += self._government.pending(user, today)
        return registry.sort_pending(items)

    def _credit_account(self, user: UserDTO, acting: UUID) -> tuple[UUID, Fund | None]:
        """A conta do crédito e, na conta de gestora, a gestora: o crédito é da conta pessoal ou da gestora do gestor principal."""
        if acting == user.client_id:
            return acting, None
        government = self._government
        if government is not None and acting == government.sovereign_fund().client_id:
            raise ForbiddenError(
                "O Fundo Soberano não toma crédito.", code="credit_sovereign_fund"
            )
        self._ensure_not_eliminated(user)
        fund = self._funds.of_client(acting) if self._funds is not None else None
        if fund is None or fund.terms.manager_user_id != user.id:
            raise ForbiddenError(
                "Só o gestor principal toma crédito pela gestora.",
                code="credit_comanager",
            )
        return acting, fund

    @synchronized
    def get_credit(self, user: UserDTO, acting: UUID) -> CreditOverviewDTO:
        account, _ = self._credit_account(user, acting)
        return build_overview(self._engine.credit_book, account, self._current_date)

    @synchronized
    def quote_loan(
        self, user: UserDTO, acting: UUID, amount: Decimal, term_months: int
    ) -> LoanQuoteDTO:
        account, fund = self._credit_account(user, acting)
        if fund is not None:
            self._ensure_fund_borrows(fund)
        return build_loan_quote(
            self._engine.credit_book,
            account,
            self._current_date,
            amount,
            term_months,
            fund.account.quotas if fund is not None else None,
        )

    @synchronized
    def preview_prepayment(
        self, user: UserDTO, acting: UUID, loan_id: UUID, amount: Decimal
    ) -> PrepaymentPreviewDTO:
        account, _ = self._credit_account(user, acting)
        return build_prepayment_preview(
            self._engine.credit_book, account, loan_id, self._current_date, amount
        )

    @synchronized
    def contract_loan(
        self, user: UserDTO, acting: UUID, amount: Decimal, term_months: int
    ) -> None:
        account, fund = self._credit_account(user, acting)
        if fund is not None:
            self._ensure_fund_borrows(fund)
            self._ensure_fund_active(fund)
        try:
            self._engine.credit_book.contract(account, amount, term_months)
            if fund is not None:
                # A taxa a pagar sai do dinheiro novo logo na contratação
                self._ensure_funds().settle_payable(fund)
                self._notify_funds_update()
        finally:
            EventManager.flush()

    @synchronized
    def prepay_loan(
        self,
        user: UserDTO,
        acting: UUID,
        loan_id: UUID,
        amount: Decimal,
        mode: PrepaymentMode,
    ) -> None:
        account, fund = self._credit_account(user, acting)
        try:
            self._engine.credit_book.prepay(account, loan_id, amount, mode)
            self._after_fund_credit(fund)
        finally:
            EventManager.flush()

    @synchronized
    def payoff_loan(self, user: UserDTO, acting: UUID, loan_id: UUID) -> None:
        account, fund = self._credit_account(user, acting)
        try:
            self._engine.credit_book.payoff(account, loan_id)
            self._after_fund_credit(fund)
        finally:
            EventManager.flush()

    def _payroll_salary(self, user: UserDTO, acting: UUID) -> Decimal:
        """O salário líquido do mês de quem pode tomar o consignado: o Servidor, na conta pessoal e na partida com profissões."""
        if acting != user.client_id:
            raise ConflictError("O consignado é da conta pessoal, não da gestora.")
        if (
            self._life is None
            or not self.settings.uses_professions
            or self._profession_of(user.id) is not Profession.PUBLIC_SERVANT
        ):
            raise ConflictError("O consignado é exclusivo do Servidor Público.")
        budget = self._life_budget(self._life, user.id)
        return budget.net_salary_on(self._current_date)

    @synchronized
    def quote_payroll(
        self, user: UserDTO, acting: UUID, amount: Decimal, term_months: int
    ) -> PayrollQuoteDTO:
        net_salary = self._payroll_salary(user, acting)
        return build_payroll_quote(
            self._engine.credit_book,
            user.client_id,
            self._current_date,
            amount,
            term_months,
            net_salary,
        )

    @synchronized
    def contract_payroll(
        self, user: UserDTO, acting: UUID, amount: Decimal, term_months: int
    ) -> PayrollLoanDTO:
        net_salary = self._payroll_salary(user, acting)
        try:
            loan = self._engine.credit_book.contract_payroll(
                user.client_id, amount, term_months, net_salary
            )
            return build_payroll_loan(loan, self._current_date)
        finally:
            EventManager.flush()

    @synchronized
    def pay_overdue(self, user: UserDTO, acting: UUID, loan_id: UUID) -> None:
        account, fund = self._credit_account(user, acting)
        try:
            self._engine.credit_book.pay_overdue(account, loan_id)
            self._after_fund_credit(fund)
        finally:
            EventManager.flush()

    def _ensure_fund_borrows(self, fund: Fund) -> None:
        """A gestora toma empréstimo depois da oferta pública, quando já está listada."""
        if not fund.listed:
            raise ConflictError(
                "A gestora toma empréstimo depois da oferta pública, quando já está listada."
            )

    def _after_fund_credit(self, fund: Fund | None) -> None:
        """O pagamento de empréstimo mexe no caixa da gestora: as páginas dela se atualizam."""
        if fund is not None:
            self._notify_funds_update()

    @synchronized
    def get_fixed_offers(self, client_id: UUID) -> list[FixedIncomeOfferDTO]:
        """As ofertas do catálogo público e, para o Bancário, os CDBs da casa dele."""
        market = self._engine.fixed_income_market
        return [
            self.offer_of(a)
            for a in [*self.get_fixed_assets(), *market.get_house_assets(client_id)]
            if a.investment_type is not FixedIncomeType.TESOURO_DIRETO
        ]

    @synchronized
    def get_fixed_offer(
        self, client_id: UUID, asset_uuid: str
    ) -> FixedIncomeOfferDTO | None:
        asset = self.get_fixed_asset(client_id, asset_uuid)
        if not asset:
            return None
        return self.offer_of(asset)

    @synchronized
    def offer_of(self, asset: FixedIncomeAssetDTO) -> FixedIncomeOfferDTO:
        dto = apply_offer_assistance(
            offer(
                asset,
                self._current_date,
                self._tax_policy(),
                self._engine.dollar_today(),
            ),
            self.settings,
        )
        # O selo da profissão marca o CDB da casa, que o jogador só recebe pela profissão dele
        return dto.model_copy(
            update={
                "profession_offer": self._engine.fixed_income_market.is_house_asset(
                    str(asset.asset_uuid)
                )
            }
        )

    @synchronized
    def get_house_offers(self) -> list[tuple[UUID, FixedIncomeOfferDTO]]:
        """Cada CDB da casa do mês com o cliente que o recebeu, para o aviso ir só a ele."""
        return [
            (owner, self.offer_of(asset))
            for owner, asset in self._engine.fixed_income_market.house_catalog()
        ]

    @synchronized
    def quote_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, amount: Decimal
    ) -> FixedIncomeQuoteDTO:
        if self._current_date >= asset.maturity_date:
            raise ConflictError("Esse título já venceu. Escolha uma oferta atual.")
        cash = self.get_cash(client_id)
        applied = self._applied(client_id, asset)
        max_amount = cash
        if asset.player_cap is not None:
            max_amount = min(cash, max(asset.player_cap - applied, Decimal(0)))
        if asset.offered_until is not None and self._current_date > asset.offered_until:
            max_amount = Decimal(0)
        return build_quote(
            project(asset, amount, self._current_date, self._tax_policy()),
            self.settings,
            cash_before=cash,
            cash_after=cash - amount,
            max_amount=max_amount,
            cap_used=None if asset.player_cap is None else applied,
            income_tax_brackets=income_tax_brackets(self._tax_policy()),
        )

    def _applied(self, client_id: UUID, asset: FixedIncomeAssetDTO) -> Decimal:
        """Capital que `client_id` mantém aplicado no título; zero sem posição."""
        position = self.get_fixed_positions(client_id).get(asset.asset_uuid)
        return position.total_applied if position else Decimal(0)

    def _held_value(self, client_id: UUID, asset: FixedIncomeAssetDTO) -> Decimal:
        """O que a posição de `client_id` no título vale hoje; zero sem posição."""
        position = self.get_fixed_positions(client_id).get(asset.asset_uuid)
        return (
            position.reais_value(self._engine.fixed_quotes())
            if position
            else Decimal(0)
        )

    @synchronized
    def quote_fixed_redemption(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, amount: Decimal
    ) -> FixedIncomeRedemptionQuoteDTO:
        if not asset.daily_liquidity:
            raise ConflictError(f"{asset.name} só é resgatado no vencimento")
        position = self.get_fixed_positions(client_id).get(asset.asset_uuid)
        if position is None:
            raise NotFoundError(f"Você não tem posição em {asset.name}")

        today = self._current_date
        policy = self._tax_policy()
        quotes = self._engine.fixed_quotes()
        maximum = position.breakdown(today, None, policy, quotes).net
        redemption = (
            position.breakdown(today, amount, policy, quotes)
            if 0 < amount <= maximum
            else None
        )
        cash = self.get_cash(client_id)
        first = position.first_applied_date
        days_held = (today - first).days
        drop = next_tax_drop(asset.investment_type, first, today, policy)
        return FixedIncomeRedemptionQuoteDTO(
            amount=amount,
            max_amount=maximum,
            position_value=position.reais_value(quotes),
            total_applied=position.total_applied,
            first_applied_date=first,
            days_held=days_held,
            gross_amount=redemption and redemption.gross,
            yield_amount=redemption and redemption.yield_amount,
            iof_rate=iof_rate(asset.investment_type, days_held),
            iof=redemption and redemption.iof,
            income_tax_rate=income_tax_rate(asset.investment_type, days_held, policy),
            income_tax=redemption and redemption.income_tax,
            net_amount=redemption and redemption.net,
            cash_before=cash,
            cash_after=redemption and cash + redemption.net,
            remaining=redemption and redemption.remaining,
            full=redemption is not None and redemption.full,
            next_tax_drop=drop and NextTaxDropDTO(on=drop.on, rate=drop.rate),
            iof_free_date=iof_free_date(first, today),
        )

    @synchronized
    def get_treasury(self) -> TreasuryCatalogDTO:
        thermometer = (
            treasury_panel.build_thermometer(
                self._government.budget(), self._current_date
            )
            if self._government is not None
            else None
        )
        return treasury_panel.build_catalog(
            self.settings.start_date,
            self._current_date,
            self.get_fixed_assets(),
            thermometer,
            self.settings.show_equivalent_rate,
        )

    @synchronized
    def get_treasury_history(self) -> list[TreasuryHistoryPointDTO]:
        budget = self._government.budget() if self._government is not None else None
        points = treasury.history(
            self.settings.start_date,
            self._current_date,
            self._engine.risk_premium_on,
            None if budget is None else budget.debt_on,
        )
        return treasury_panel.build_history(points, self.settings.show_equivalent_rate)

    @synchronized
    def get_treasury_positions(self, client_id: UUID) -> list[TreasuryPositionDTO]:
        quotes = self._engine.fixed_quotes()
        return [
            treasury_panel.build_position(position, self._current_date, quotes)
            for position in self.get_fixed_positions(client_id).values()
            if position.asset.investment_type is FixedIncomeType.TESOURO_DIRETO
        ]

    def _treasury_position(
        self, client_id: UUID, asset_uuid: UUID
    ) -> FixedIncomePosition:
        position = self.get_fixed_positions(client_id).get(asset_uuid)
        if (
            position is None
            or position.asset.investment_type is not FixedIncomeType.TESOURO_DIRETO
        ):
            raise NotFoundError("Você não tem posição neste título do Tesouro")
        return position

    @synchronized
    def quote_treasury_sale(
        self, client_id: UUID, asset_uuid: UUID, amount: Decimal
    ) -> TreasurySaleQuoteDTO:
        return treasury_panel.build_sale_quote(
            self._treasury_position(client_id, asset_uuid),
            amount,
            self.get_cash(client_id),
            self._current_date,
            self._engine.fixed_quotes(),
            self._tax_policy(),
        )

    @synchronized
    def sell_treasury(
        self, client_id: UUID, asset_uuid: UUID, gross: Decimal | None
    ) -> None:
        self._ensure_can_operate(client_id)
        self._ensure_not_sovereign(client_id)
        asset = self._treasury_position(client_id, asset_uuid).asset
        self._engine.fixed_broker.sell_treasury(client_id, asset, gross)
        EventManager.flush()

    @synchronized
    def get_patrimonial_history(
        self, client_id: UUID
    ) -> list[PortfolioHistoryPointDTO]:
        portfolio_id = UserManager.get_portfolio_id(client_id)
        return [
            self._history_point(point, portfolio_id)
            for point in repository.portfolio.get_patrimonial_history(portfolio_id)
        ]

    def _portfolio_starting_cash(self, portfolio_id: int) -> Decimal:
        """O capital inicial do jogador, lido da carteira dele uma vez."""
        if portfolio_id not in self._portfolio_cash:
            self._portfolio_cash.update(
                repository.portfolio.starting_cash([portfolio_id])
            )
        return self._portfolio_cash[portfolio_id]

    def _history_point(
        self, point: PatrimonialHistoryDTO, portfolio_id: int
    ) -> PortfolioHistoryPointDTO:
        return PortfolioHistoryPointDTO(
            **point.model_dump(),
            total_provided=self._portfolio_starting_cash(portfolio_id)
            + point.total_contribution,
        )

    @synchronized
    def next_tick(self):
        # O dia em que alguém chegou à meta foi processado inteiro; a partida acaba no seguinte
        if self._goal_reached:
            logger.info("Meta alcançada")
            raise StopIteration()
        # O dia da última eliminação foi processado inteiro; a partida acaba no seguinte
        if self._last_standing:
            logger.info("Restou um jogador ativo")
            raise StopIteration()

        # Avança para o próximo dia útil; passou do fim, a simulação terminou
        previous_date = self._current_date
        if self._current_date <= self.settings.end_date:
            self._current_date = next_business_day(self._current_date)
        if self._current_date > self.settings.end_date:
            logger.info("Fim da simulação")
            raise StopIteration()
        # O mês que fechou ontem já vale nas séries e nos preços de hoje
        self._close_months(self._current_date)

        # O impacto é lido dos eventos no banco: o flush leva antes as ordens que
        # chegaram por HTTP depois do último tick, ainda datadas do dia anterior
        with metrics.measure("engine", ENGINE_PRICES):
            EventManager.flush()
            self._price_impact.refresh(self._current_date)

            # O matching pode executar ordens antigas durante a atualização do book.
            # Elas já pertencem ao dia novo, assim como os juros e as consultas.
            self._engine.current_date = self._current_date
            # Obtém os dados do dia atual e atualiza o buffer
            stocks = self.get_stocks()

            # Só quem estava na sala ao iniciar participa: é quem tem depósito e cor
            users = repository.simulation_player.participants(self.settings.id)

            # Desdobramentos e dividendos entram na abertura, antes de o book executar
            # qualquer ordem do dia: a posição e as ordens já valem na unidade nova
            corporate_actions = self._engine.apply_corporate_events(
                self._engine.corporate_events(
                    repository.corporate_event.get_between(
                        previous_date, self._current_date, self.settings.id
                    )
                ),
                stocks,
                [user.client_id for user in users]
                + (self._funds.client_ids if self._funds is not None else []),
            )
            self._engine.update_market_data(stocks)

        # Juros da renda fixa e, em seguida, as estratégias ligadas operam o dia
        with metrics.measure("engine", ENGINE_FIXED_INCOME):
            self._engine.next(self._current_date)
        # O PL e as ordens do formador e da oferta valem antes de qualquer jogador ou bot operar
        if self._funds is not None:
            with metrics.measure("engine", ENGINE_FUNDS):
                self._funds.on_open(self._current_date)
        if self._government is not None:
            with metrics.measure("engine", ENGINE_GOVERNMENT):
                self._government.open_state_market(self._current_date)
        with metrics.measure("engine", ENGINE_BOTS):
            self._strategies.run(users, self._current_date)
        month_changed = self._has_month_changed()

        # O aporte (ou o salário, a despesa e o imprevisto) e o DARF que vence hoje
        # entram nos eventos antes do flush, para o snapshot do dia já contá-los; o
        # juro do cheque especial vem por último, sobre o caixa que sobrou do dia
        with metrics.measure("engine", ENGINE_CONTRIBUTION):
            if self._life is not None:
                self._live(self._life, users, month_changed)
            elif month_changed:
                self._apply_monthly_contributions(users)
            self._settle_credit(users, month_changed)
        if self._government is not None:
            with metrics.measure("engine", ENGINE_GOVERNMENT):
                reason = self._government.on_tick(
                    users, self._current_date, month_changed
                )
            if reason:
                self._pause_for_result(reason)
        if self._funds is not None and month_changed:
            with metrics.measure("engine", ENGINE_FUNDS):
                self._funds.on_month(self._current_date)
        with metrics.measure("engine", ENGINE_TAXES):
            self._collect_income_tax(users)
            if self._life is not None:
                self._charge_overdraft(users)
                self._run_welfare_savings(users)
                self._run_house_report(users, stocks)
            EventManager.flush()
        with metrics.measure("engine", ENGINE_NEWS):
            self._publish_newsroom(stocks)

        # A vela das cotas fecha antes do snapshot: o preço de ranking do dia já vale nele
        fund_candles: list[CandleDTO] = []
        if self._funds is not None:
            with metrics.measure("engine", ENGINE_FUNDS):
                fund_candles = self._funds.on_close(self._current_date)
            self._advance_eliminations(users)
        created_candles = list(fund_candles)
        if self._government is not None:
            with metrics.measure("engine", ENGINE_GOVERNMENT):
                created_candles += self._government.close_state_market(
                    self._current_date
                )

        if self.backtest is not None:
            with metrics.measure("engine", ENGINE_BACKTEST_DAY):
                self._record_backtest_day(users, month_changed)
            return

        with metrics.measure("engine", ENGINE_SNAPSHOTS):
            snapshots = self._create_daily_snapshots(users, month_changed)

        # Emite notificações
        logger.debug(
            "Dia simulado: %s (%s ativos, %s jogadores)",
            self.get_current_date_formatted(),
            len(stocks),
            len(users),
        )
        with metrics.measure("engine", ENGINE_PUBLISH):
            # As linhas do registro e o modo das estratégias do dia saem com tudo já gravado
            self._strategies.publish()
            for stock in [*stocks, *created_candles]:
                ticker = stock.ticker
                notify(
                    f"stock_update:{ticker}",
                    StockUpdateEventDTO(stock=stock).to_json(),
                )
            self._feed.publish_day([*stocks, *created_candles])
            notify(
                "simulation_update",
                SimulationTickUpdateEventDTO(current_date=self._current_date).to_json(),
            )
            # As cotas listadas andam junto das ações; as estatais seguem só no evento do ativo
            notify(
                "stocks_update",
                StocksUpdateEventDTO(stocks=[*stocks, *fund_candles]).to_json(),
            )
            if self._funds is not None:
                self._funds_feed.mark()
            self._fund_preview_feed.day_passed()
            self._cash_feed.day_passed()
            with self._publishing():
                self._day_feed.publish(month_changed=month_changed)
            self._publish_government_panels()
            for player in UserManager.list_active_players():
                notify(
                    "portfolio_update",
                    PortfolioUpdateEventDTO(
                        portfolio=self.get_portfolio(player.client_id), account=None
                    ).to_json(),
                    to=player.client_id,
                )
                # Cada gestora que o jogador gere vai ao gestor marcada com o id dela
                for fund in self._funds.operated_by(player.id) if self._funds else []:
                    notify(
                        "portfolio_update",
                        PortfolioUpdateEventDTO(
                            portfolio=self.get_portfolio(fund.account.client_id),
                            account=fund.terms.id,
                        ).to_json(),
                        to=player.client_id,
                    )
                # Só quem tinha o ativo na abertura recebe o aviso do pregão
                actions = corporate_actions.get(player.client_id)
                if actions is not None:
                    notify(
                        "corporate_actions",
                        CorporateActionsEventDTO.from_actions(actions).to_json(),
                        to=player.client_id,
                    )
                    self._day_feed.publish_corporate_events(
                        player.client_id,
                        [
                            *(line.ticker for line in actions.dividends),
                            *(split.ticker for split in actions.splits),
                        ],
                    )
        if self.settings.game_type.has_goal:
            with metrics.measure("engine", ENGINE_GOAL):
                self._track_goal(users, snapshots)

        self._last_snapshots = {
            user.id: entry.snapshot
            for user, entry in zip(users, snapshots, strict=True)
        }
        if month_changed and self._current_date.month == 1:
            with metrics.measure("engine", ENGINE_SUMMARIES):
                self._deliver_summaries(users)
        with metrics.measure("engine", ENGINE_ACHIEVEMENTS):
            self._unlock_achievements(
                users,
                lambda: self._achievements.on_tick(
                    self._human_snapshots(users), month_changed
                ),
            )

    def _advance_eliminations(self, users: list[UserDTO]) -> None:
        """Quem acabou de ser eliminado perde o automático; com um humano ativo só (em equipes, uma equipe só), a partida acaba."""
        funds = self._funds
        if funds is None or not funds.eliminated:
            return
        eliminated = funds.eliminated
        for user in users:
            if user.id in eliminated and user.id not in self._eliminations_handled:
                self._eliminations_handled.add(user.id)
                self._strategies.set_mode(
                    StrategyAccount.of_user(user),
                    None,
                    {},
                    self._current_date,
                    reason=(
                        "Sua equipe perdeu a assembleia da gestora: agora só assiste"
                        if self.settings.is_takeover_teams
                        else "Você perdeu a assembleia da sua gestora: agora só assiste"
                    ),
                )
        active = [u for u in users if not u.is_bot and u.id not in eliminated]
        if self.settings.is_takeover_teams:
            # Quem joga sem equipe (chegou depois da largada) não sustenta a disputa
            teams = repository.simulation_player.teams(self.settings.id)
            self._last_standing = (
                len({teams[u.id] for u in active if u.id in teams}) <= 1
            )
        else:
            self._last_standing = len(active) <= 1

    def _account_owners(self, client_id: UUID) -> frozenset[int] | None:
        """Os user_ids donos da conta `client_id`: quem opera a gestora para a conta de uma gestora, o próprio jogador para a pessoal."""
        if self._funds is not None:
            fund = self._funds.of_client(client_id)
            if fund is not None:
                return frozenset(self._funds.operators(fund))
        user = UserManager.get_user(client_id)
        return frozenset({user.id}) if user is not None else None

    def _client_of_user(self, user_id: int) -> UUID:
        """O client_id do participante da partida."""
        for user in repository.simulation_player.participants(self.settings.id):
            if user.id == user_id:
                return user.client_id
        raise NotFoundError("Jogador fora da partida")

    def _government_inflation(self, day: date) -> float:
        """Os pontos de IPCA que o governo soma à série no dia, pelas medidas e pelas ligações da economia; zero sem o governo."""
        if self._government is None:
            return 0.0
        return self._government.linked().layer.inflation_points(day)

    def _close_months(self, day: date) -> None:
        """Fecha os meses da economia até `day`; com o governo, na ordem da economia interligada."""
        if self._government is None:
            self._macro.months_until(day)
        else:
            self._government.close_months(day)

    def _publish_newsroom(self, stocks: list[CandleDTO]) -> None:
        """As manchetes do pregão; uma falha do noticiário não para a partida."""
        if self._newsroom is None:
            return
        try:
            self._newsroom.on_tick(self._current_date, stocks)
        except Exception:
            logger.exception("Erro ao montar o noticiário do pregão")

    def _record_backtest_day(self, users: list[UserDTO], month_changed: bool) -> None:
        """
        O snapshot do dia sai do balanço do motor e espera o lote: a cada passo do
        gráfico o lote é gravado e a sala é avisada, nessa ordem, para quem abrir o
        resultado já encontrar os dados.
        """
        backtest = required(self.backtest)
        contribution = (
            self.settings.monthly_contribution if month_changed else Decimal(0)
        )
        self._contributed += contribution
        today = [self._balance_snapshot(user) for user in users]
        self._pending_snapshots.extend(today)
        if backtest.record_day(self._current_date, today, contribution):
            self.flush_backtest()
            backtest.publish()

    def _balance_snapshot(self, user: UserDTO) -> SnapshotDTO:
        balance = self._engine.balance_sheet(user.client_id)
        return SnapshotDTO(
            portfolio_id=SimulationManager.get_portfolio_id(user.id),
            snapshot_date=self._current_date,
            total_equity=balance.total_equity,
            total_fixed=balance.total_fixed,
            total_cash=balance.total_cash,
            total_contribution=self._contributed,
            total_debt=balance.total_debt,
            total_locked=balance.total_locked,
            total_networth=networth(
                cash=balance.total_cash,
                equity=balance.total_equity,
                fixed=balance.total_fixed,
                locked=balance.total_locked,
                debt=balance.total_debt,
            ),
            equity_by_class=balance.equity_by_class,
            created_at=datetime.now(UTC),
        )

    def _backtest_failed(self, nickname: str, day: date, message: str) -> None:
        required(self.backtest).fail(nickname, day, message)

    def flush_backtest(self) -> None:
        """Grava os snapshots pendentes do backtest."""
        repository.snapshot.create_many(self.settings.id, self._pending_snapshots)
        self._pending_snapshots = []

    def end_match(self) -> None:
        """
        Conquistas que dependem do resultado: roda com a partida ainda ativa, depois
        do último flush.
        """
        users = repository.simulation_player.participants(self.settings.id)
        self._unlock_achievements(
            users,
            lambda: self._achievements.on_match_end(
                self._human_snapshots(users),
                match_result(self.settings.id, users, self._goal_reached),
            ),
        )

    def _human_snapshots(self, users: list[UserDTO]) -> dict[int, SnapshotDTO]:
        """Conquista é de pessoa: os snapshots dos bots não chegam ao avaliador."""
        bots = {u.id for u in users if u.is_bot}
        return {
            user_id: snapshot
            for user_id, snapshot in self._last_snapshots.items()
            if user_id not in bots
        }

    def _unlock_achievements(
        self,
        users: list[UserDTO],
        evaluate: Callable[[], dict[int, list[Achievement]]],
    ) -> None:
        """
        Avalia e avisa cada jogador, uma vez, com tudo o que saiu agora (o toast é um
        só). As conquistas são um extra: um erro ao avaliá-las não interrompe a partida.
        """
        try:
            unlocked = evaluate()
        except Exception:
            logger.exception("Erro ao avaliar as conquistas")
            return
        for user in users:
            if achievements := unlocked.get(user.id):
                notify(
                    "achievement_unlocked",
                    unlocked_event(achievements).to_json(),
                    to=user.client_id,
                )

    def _deliver_summaries(self, users: list[UserDTO]) -> None:
        """
        A retrospectiva sai depois dos snapshots do dia. Ela é um extra:
        um erro ao montá-la não interrompe a partida.
        """
        try:
            self._summaries.on_year_turn(users, self._current_date)
        except Exception:
            logger.exception("Erro ao montar a retrospectiva do ano")

    def get_goal_progress(self) -> GoalProgressDTO | None:
        return self._goal_progress

    def _track_goal(
        self, users: list[UserDTO], snapshots: list[StatisticsSnapshotEntryDTO]
    ) -> None:
        """Avisa onde cada um está na meta e marca o fim da partida quando alguém chega."""
        colors = repository.simulation_player.colors(self.settings.id)
        teams = repository.simulation_player.teams(self.settings.id)
        team_names = (
            repository.fund.team_names(self.settings.id)
            if self.settings.is_takeover_teams
            else {}
        )
        goal = goal_on(self.settings, self._current_date)
        # A tela refaz a busca do relatório quando a meta sobe: a meta em degraus é dele
        if self._goal_progress is not None and goal != self._goal_progress.goal:
            self.statistics.clear()
        self._goal_progress = GoalProgressDTO(
            goal=goal,
            players=[
                GoalRunnerDTO(
                    nickname=entry.player_nickname,
                    color=colors[user.id],
                    team=teams.get(user.id),
                    team_name=team_names.get(teams.get(user.id, 0)),
                    networth=entry.snapshot.total_networth,
                )
                for user, entry in zip(users, snapshots, strict=True)
            ],
        )
        notify("goal_progress_update", self._goal_progress.to_json())
        self._goal_reached = goal_reached(
            {
                user.id: entry.snapshot.total_networth
                for user, entry in zip(users, snapshots, strict=True)
            },
            teams,
            goal,
            self.settings.player_grouping is PlayerGrouping.TEAMS,
        )

    def _live(self, life: LifeBudget, users: list[UserDTO], month_changed: bool):
        """
        No 1º pregão do mês a renda de cada jogador entra pela profissão dele (menos
        depois de uma demissão sorteada, nas profissões que a sentem) e a despesa sai;
        todo pregão pode sortear um imprevisto, o mesmo para todos, que cada profissão
        sente à sua maneira. A carreira que pesa a demissão sorteia com a chance
        multiplicada pelo peso do dia: sobre o mesmo sorteio, quem pesa mais perde a
        renda em dias em que a sala não perde.
        """
        day = self._current_date
        per_year = self.settings.unexpected_per_year
        # O curso concluído troca a profissão e o degrau concluído abre o trecho novo da curva antes de montar os orçamentos: o primeiro salário do mês já é o novo
        if month_changed:
            self._conclude_courses(users, day)
            self._conclude_steps(users, day)
        budgets = {user.client_id: self._life_budget(life, user.id) for user in users}
        skipped_by_weight: dict[Decimal, bool] = {}
        event_by_weight: dict[Decimal, LifeEventTypeDTO | None] = {}

        def skipped_for(budget: LifeBudget) -> bool:
            weight = budget.layoff_weight_on(day)
            if weight not in skipped_by_weight:
                skipped_by_weight[weight] = salary_skipped(
                    self._random_seed,
                    day,
                    per_year,
                    self.settings.start_date,
                    self.settings.life_events,
                    layoff_factor_on=self._layoff_factor_for(budget),
                    frequencies=self.settings.life_frequencies,
                )
            return skipped_by_weight[weight]

        def event_for(budget: LifeBudget) -> LifeEventTypeDTO | None:
            weight = budget.layoff_weight_on(day)
            if weight not in event_by_weight:
                event_by_weight[weight] = unexpected_on(
                    self._random_seed,
                    day,
                    per_year,
                    self.settings.life_events,
                    layoff_factor=self._layoff_factor_for(budget)(day),
                    frequencies=self.settings.life_frequencies,
                )
            return event_by_weight[weight]

        if month_changed:
            # A recessão desliga a hora extra e a política do bot age antes da renda do mês: o estado que ficam vale já neste mês
            self._end_overtime_in_recession(users, day)
            self._run_bot_policies(users, day, budgets)
            self._run_broker_month(users, day)
            for user in users:
                budget = budgets[user.client_id]
                loses_income = budget.income_loss() is not None and skipped_for(budget)
                salary = budget.net_salary_on(day, income_lost=loses_income)
                self._run_welfare_month(user, budget, day)
                if salary > 0 or not loses_income:
                    self._engine.pay_salary(user.client_id, salary)
                self._run_capital_month(user, budget, day, profit=salary)
                self._run_pension_month(user, day)
                # A parcela do consignado sai do salário que acabou de entrar
                self._engine.credit_book.collect_payroll(user.client_id, self._speed)
                self._engine.pay_expense(user.client_id, budget.paid_expense_on(day))
                self._run_fgts_month(user, budget, day, salary_paid=salary > 0)
                self._run_exchange_lock_month(user, budget, day, salary_paid=salary > 0)

        for user in users:
            budget = budgets[user.client_id]
            event = event_for(budget)
            if event is None:
                continue
            is_layoff = event.effect is LifeEventEffect.SKIP_NEXT_SALARY
            is_income = event.effect is LifeEventEffect.CASH_IN
            # A profissão que não sente a demissão sorteada não a registra
            if is_layoff and budget.income_loss() is None:
                continue
            health = budget.health_multiple if event.key == HEALTH_EVENT_KEY else 1
            amount = event.expense_multiple * budget.expense_on(day) * health
            if is_income:
                self._engine.receive_unexpected(user.client_id, amount, event.key)
            else:
                self._engine.charge_unexpected(user.client_id, amount, event.key)
            if is_layoff:
                self._pay_out_fgts(user)
            if self.settings.uses_professions and not user.is_bot:
                self._notify_life_event(event, amount, budget, user)
        if not self.settings.uses_professions:
            budget = budgets[users[0].client_id] if users else life
            event = event_for(budget)
            if event is not None:
                amount = event.expense_multiple * budget.expense_on(day)
                self._notify_life_event(event, amount, budget)

    def _notify_life_event(
        self,
        event: LifeEventTypeDTO,
        amount: Decimal,
        budget: LifeBudget,
        user: UserDTO | None = None,
    ):
        """O aviso do imprevisto: um só para a sala com salário igual, e o de cada jogador com profissões, com o nome, o valor e o efeito da dele."""
        profession = budget.profession if user is not None else None
        notify(
            "life_event",
            LifeEventDTO(
                key=event.key,
                label=life_event_label(event.key, event.label, profession),
                effect=event.effect,
                amount=amount,
                event_date=self._current_date,
                income_loss=budget.income_loss(),
            ).to_json(),
            to=user.client_id if user is not None else None,
        )

    def _unemployment_ratio_on(self, day: date) -> Decimal:
        """O desemprego da partida sobre o neutro: o que escala a perda de clientes do Autônomo."""
        return self._macro.latest(day).unemployment / NEUTRAL_UNEMPLOYMENT

    def _layoff_factor(self, day: date) -> float:
        """A chance de demissão em `day` segue o desemprego da partida."""
        return layoff_factor_of(self._macro.latest(day).unemployment)

    def _layoff_factor_for(self, budget: LifeBudget) -> Callable[[date], float]:
        """A chance de demissão da profissão: a da sala vezes o peso da carreira dela."""
        return lambda day: (
            self._layoff_factor(day) * float(budget.layoff_weight_on(day))
        )

    def _dollar_change_on(self, day: date) -> Decimal:
        """A variação do dólar da partida em 12 meses; o dia consultado é o último a ficar no cache do motor."""
        before = self._engine.dollar_on(day - timedelta(days=DOLLAR_WINDOW_DAYS))
        return self._engine.dollar_on(day) / before - 1

    def _selic_on(self, day: date) -> Decimal:
        """A SELIC ao ano que a partida vive no dia, a mesma que o cheque especial cobra."""
        return annual_index_rate(IndicatorSeries.SELIC, day)

    def _levers_on(self, day: date) -> LifeLevers:
        """As medidas do governo que chegam à renda no dia; sem governo, o país padrão."""
        policy = self._engine.tax_policy_on(day)
        levers = LifeLevers(
            personal_rate=policy.personal_rate,
            corporate_rate=policy.corporate_rate,
            consumption_rate=policy.consumption_rate,
        )
        government = self._government
        if government is None:
            return levers
        return replace(
            levers,
            servant_raise=self._in_force(
                MeasureKind.SERVANT_RAISE, day, levers.servant_raise
            ),
            retiree_raise=self._in_force(
                MeasureKind.RETIREE_RAISE, day, levers.retiree_raise
            ),
            welfare_spending=self._in_force(
                MeasureKind.WELFARE_SPENDING, day, levers.welfare_spending
            ),
        )

    def _lever_author_on(
        self, kind: MeasureKind, day: date
    ) -> tuple[str | None, str | None]:
        """Quem propôs a medida de gasto em vigor no dia; sem governo na sala, ninguém."""
        government = self._government
        if government is None:
            return None, None
        return government.author_of_lever(kind, day)

    def _in_force(self, kind: MeasureKind, day: date, default: Decimal) -> Decimal:
        government = self._government
        value = None if government is None else government.value_in_force(kind, day)
        return default if value is None else value

    def _profession_of(self, user_id: int) -> Profession:
        """A profissão do jogador; sem o modo de profissões, todo mundo é CLT."""
        if not self.settings.uses_professions:
            return Profession.CLT
        if user_id not in self._professions:
            self._professions = repository.simulation_player.professions(
                self.settings.id
            )
        return self._professions.get(user_id, Profession.CLT)

    def _party_of(self, user_id: int) -> str | None:
        """A sigla do partido que o Comissionado escolheu ao entrar."""
        if user_id not in self._parties:
            self._parties = repository.simulation_player.parties(self.settings.id)
        return self._parties.get(user_id)

    def _with_party(self, budget: LifeBudget, user_id: int) -> LifeBudget:
        """A renda de quem tem profissão presa a partido acompanha se o partido escolhido está no governo."""
        government = self._government
        if government is None or not is_party_bound(budget.profession):
            return budget
        party = self._party_of(user_id)
        if party is None:
            return budget
        return budget.with_party(lambda day: government.is_aligned(party, day))

    def _mechanic_state_of(self, user_id: int) -> MechanicState:
        """O estado da mecânica da profissão que o jogador exerce agora; o saldo da previdência que ainda não abriu abre na primeira leitura."""
        profession = self._profession_of(user_id)
        state = self._profession_book.state_of(user_id, profession)
        if isinstance(state, RetireeState) and state.balance is None:
            return self._open_pension(user_id, state)
        return state

    def _open_pension(self, user_id: int, state: RetireeState) -> RetireeState:
        """
        Abre o saldo da previdência em 24 rendas do mês de hoje e o guarda: o tempo no
        plano conta daqui. A renda vem do orçamento da profissão sem o estado da mecânica,
        que é o que está sendo aberto.
        """
        if self._life is None or not self.settings.uses_professions:
            return state
        income = self._life.for_profession(Profession.RETIREE).net_salary_on(
            self._current_date
        )
        opened = open_balance(state, income, self._current_date)
        self._profession_book.save_state(user_id, opened)
        return opened

    def _with_mechanic(self, budget: LifeBudget, user_id: int) -> LifeBudget:
        """A renda de quem tem mecânica acompanha o estado dela, lido a cada cálculo."""
        return budget.with_mechanic_state(lambda: self._mechanic_state_of(user_id))

    @synchronized
    def get_profession_state(self, client_id: UUID) -> ProfessionStateDTO:
        """A profissão de `client_id` e o estado da mecânica dela."""
        user_id = UserManager.get_user_id(client_id)
        return ProfessionStateDTO(
            profession=self._profession_of(user_id),
            state=self._mechanic_state_of(user_id),
        )

    @synchronized
    def get_profession_page(self, client_id: UUID) -> ProfessionPageDTO:
        """A página Profissão de `client_id`: o cabeçalho, os indicadores que mexem na renda e o bloco da mecânica."""
        if self._life is None or not self.settings.uses_professions:
            raise ConflictError("A partida joga com salário igual: não há profissões.")
        user_id = UserManager.get_user_id(client_id)
        day = self._current_date
        budget = self._life_budget(self._life, user_id)

        def unemployment_on(on: date) -> Decimal:
            return self._macro.latest(on).unemployment

        return ProfessionPageDTO(
            profession=budget.profession,
            header=build_header(budget, day, unemployment_on(day)),
            series=build_series(budget, day, unemployment_on, self._lever_author_on),
            mechanic=self._mechanic_block(client_id, user_id, budget, day),
        )

    def _mechanic_block(
        self, client_id: UUID, user_id: int, budget: LifeBudget, day: date
    ) -> MechanicBlockDTO:
        """O bloco da mecânica da profissão do jogador; as sem mecânica devolvem o bloco vazio."""
        match budget.profession:
            case Profession.CLT:
                state = self._clt_state_of(user_id)
                if state is None:
                    return no_block()
                tr = last_known_rate(IndicatorSeries.TR, day)
                return clt_block(
                    state,
                    budget.salary_on(day),
                    Decimal(0) if tr is None else from_percent(tr),
                    budget.growth_on(day),
                )
            case Profession.ENTREPRENEUR:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, EntrepreneurState):
                    return no_block()
                return entrepreneur_block(
                    state,
                    budget,
                    day,
                    negative_quarters(self._gdp_quarters(day)),
                )
            case Profession.RETIREE:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, RetireeState):
                    return no_block()
                rate, expected, from_focus = self._pension_real_rate(day)
                return retiree_block(
                    state,
                    budget,
                    day,
                    annual_index_rate(IndicatorSeries.CDI, day),
                    self._selic_on(day),
                    expected,
                    from_focus,
                    rate,
                )
            case Profession.WELFARE:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, WelfareState):
                    return no_block()
                return welfare_block(
                    state,
                    budget,
                    day,
                    self.settings.start_date,
                    self._engine.liquid_wealth(client_id),
                )
            case Profession.NEW_GRADUATE:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, GraduateState):
                    return no_block()
                return graduate_block(
                    state, budget, day, self._macro.latest(day).unemployment
                )
            case Profession.BROKER:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, BrokerState):
                    return no_block()
                months = self._house_months_issued()
                ordered = sorted(months, reverse=True)
                return broker_block(
                    state,
                    budget,
                    day,
                    self._house_report_of(ordered[0]) if ordered else None,
                    self._house_report_of(ordered[1]) if len(ordered) > 1 else None,
                    repository.house_report.scoreboard(self.settings.id),
                    months,
                )
            case Profession.EXPORTER:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, ExporterState):
                    return no_block()
                return exporter_block(state, budget, day, self._exchange_quotes(day))
            case Profession.FREELANCER:
                state = self._mechanic_state_of(user_id)
                if not isinstance(state, FreelancerState):
                    return no_block()
                return freelancer_block(
                    state, budget, day, self._macro.latest(day).unemployment
                )
            case Profession.PUBLIC_SERVANT:
                book = self._engine.credit_book
                net_salary = budget.net_salary_on(day)
                return public_servant_block(
                    [
                        build_payroll_loan(loan, day)
                        for loan in book.payroll_loans(client_id)
                    ],
                    net_salary,
                    net_salary * PAYROLL_MARGIN,
                    book.payroll_used(client_id),
                    book.payroll_rate(day),
                )
            case Profession.BANKER:
                return banker_block(
                    self._engine.fixed_income_market.get_house_terms(client_id),
                    lambda asset: self._applied(client_id, asset),
                    lambda asset: self._held_value(client_id, asset),
                )
            case Profession.HEIR:
                periods = self._profession_periods(user_id)
                return heir_block(
                    budget,
                    day,
                    periods[-1].start,
                    self.settings.starting_cash,
                    self.settings.end_date,
                )
            case Profession.COMMISSIONED:
                government = self._government
                return appointee_block(
                    budget,
                    day,
                    self._party_of(user_id),
                    None if government is None else government.cycle().first_round,
                )
            case Profession.OFFERS_BANKER:
                events = repository.event.get_cashflow_events(
                    self.settings.id, UserManager.get_portfolio_id(client_id)
                )
                return offers_banker_block(
                    [
                        (event.event_date, event.amount)
                        for event in events
                        if event.event_type is CashflowEventType.OFFER_COMMISSION
                    ],
                    day,
                )
            case _:
                return no_block()

    @synchronized
    def apply_profession_action(
        self, user: UserDTO, action: MechanicAction, payout: Decimal = Decimal(0)
    ) -> MechanicState:
        """
        Aplica a ação de `user` na mecânica da profissão dele: valida pela regra da
        mecânica, guarda o estado novo e lança a ação no histórico da vida, com o
        `payout` que a ação deixa no caixa. É o único caminho das ações: as rotas dos
        jogadores e a política dos bots passam por ele.
        """
        if not self.settings.uses_professions:
            raise ConflictError("A partida joga com salário igual: não há profissões.")
        profession = self._profession_of(user.id)
        state = apply_action(
            profession,
            self._mechanic_state_of(user.id),
            action,
            self._current_date,
            self._macro.latest(self._current_date),
        )
        self._profession_book.save_state(user.id, state)
        self._engine.record_profession_action(user.client_id, action.kind, payout)
        return state

    def _exchange_quotes(self, day: date) -> dict[int, Decimal]:
        """O dólar travado de cada prazo do câmbio futuro em `day`: o dólar do dia corrigido pelo CDI contra os Fed Funds."""
        spot = self._engine.dollar_on(day)
        cdi = annual_index_rate(IndicatorSeries.CDI, day)
        fed_funds = annual_index_rate(IndicatorSeries.FED_FUNDS, day)
        return {
            months: forward_dollar(spot, cdi, fed_funds, months)
            for months in LOCK_TERMS_MONTHS
        }

    @synchronized
    def lock_exchange(
        self, user: UserDTO, share: Decimal, months: int
    ) -> MechanicState:
        """Contrata a trava de câmbio do Exportador pelo dólar travado do dia, pelo mesmo caminho das ações da mecânica."""
        if self._profession_of(user.id) is not Profession.EXPORTER:
            raise ConflictError("Só o Exportador contrata trava de câmbio.")
        locked_dollar = forward_dollar(
            self._engine.dollar_on(self._current_date),
            annual_index_rate(IndicatorSeries.CDI, self._current_date),
            annual_index_rate(IndicatorSeries.FED_FUNDS, self._current_date),
            months,
        )
        return self.apply_profession_action(
            user, LockExchange(share=share, months=months, locked_dollar=locked_dollar)
        )

    @synchronized
    def set_export_mix(self, user: UserDTO, share: Decimal) -> MechanicState:
        """Muda a fração exportada do Exportador."""
        if self._profession_of(user.id) is not Profession.EXPORTER:
            raise ConflictError("Só o Exportador muda o mix de exportação.")
        return self.apply_profession_action(user, SetExportMix(share=share))

    @synchronized
    def set_price(self, user: UserDTO, price: Decimal) -> MechanicState:
        """Salva o preço por atendimento do Autônomo, com a referência do mercado do dia, pelo mesmo caminho das ações da mecânica."""
        if self._profession_of(user.id) is not Profession.FREELANCER:
            raise ConflictError("Só o Autônomo define o preço por atendimento.")
        if self._life is None:
            raise ConflictError("A partida joga com salário igual: não há profissões.")
        reference = self._life_budget(self._life, user.id).reference_price_on(
            self._current_date
        )
        return self.apply_profession_action(
            user, SetPrice(price=price, reference=reference)
        )

    @synchronized
    def set_reinvest_share(self, user: UserDTO, share: Decimal) -> MechanicState:
        """Salva a fração do lucro que o Empreendedor reinveste, pelo mesmo caminho das ações da mecânica."""
        if self._profession_of(user.id) is not Profession.ENTREPRENEUR:
            raise ConflictError("Só o Empreendedor reinveste o lucro na empresa.")
        return self.apply_profession_action(user, SetReinvestShare(share=share))

    @synchronized
    def sell_capital(self, user: UserDTO, share: Decimal) -> MechanicState:
        """Vende a fração do capital da empresa do Empreendedor: a parte vendida sai do capital e entra no caixa com o desconto, na linha do histórico da venda."""
        if self._profession_of(user.id) is not Profession.ENTREPRENEUR:
            raise ConflictError("Só o Empreendedor vende parte da empresa.")
        state = self._mechanic_state_of(user.id)
        payout = (
            sale_payout(state, share)
            if isinstance(state, EntrepreneurState)
            else Decimal(0)
        )
        return self.apply_profession_action(user, SellCapital(share=share), payout)

    def _pension_real_rate(self, day: date) -> tuple[Decimal, Decimal, bool]:
        """
        O juro real da previdência no dia, o IPCA esperado de que ele sai e se esse IPCA é
        o do Focus: a pesquisa de até 30 dias; sem ela vale o IPCA realizado em 12 meses.
        """
        expected = recent_focus_rate(IndicatorSeries.FOCUS_IPCA, day)
        from_focus = expected is not None
        if expected is None:
            expected = annual_index_rate(IndicatorSeries.IPCA, day)
        return real_rate(self._selic_on(day), expected), expected, from_focus

    @synchronized
    def convert_pension(self, user: UserDTO, amount: Decimal) -> MechanicState:
        """Converte parte do saldo da previdência do Aposentado em renda vitalícia, ao juro real do dia, pelo mesmo caminho das ações da mecânica."""
        if self._profession_of(user.id) is not Profession.RETIREE:
            raise ConflictError("Só o Aposentado converte a previdência em renda.")
        rate, _, _ = self._pension_real_rate(self._current_date)
        return self.apply_profession_action(
            user, ConvertPension(amount=amount, real_rate=rate)
        )

    @synchronized
    def redeem_pension(self, user: UserDTO, amount: Decimal) -> MechanicState:
        """Resgata parte do saldo da previdência do Aposentado: o valor sai do saldo e cai no caixa depois do IR regressivo, na linha do histórico do resgate."""
        if self._profession_of(user.id) is not Profession.RETIREE:
            raise ConflictError("Só o Aposentado resgata a previdência.")
        state = self._mechanic_state_of(user.id)
        payout = Decimal(0)
        if isinstance(state, RetireeState) and state.since is not None:
            months = months_in_plan(state.since, self._current_date)
            payout = redeem_net(amount, months)
        return self.apply_profession_action(user, RedeemPension(amount=amount), payout)

    @synchronized
    def switch_profession(self, user: UserDTO, profession: Profession) -> None:
        """
        A troca de profissão no meio da partida: o jogador mantém o caixa e o capital
        inicial, o período novo abre hoje com o estado inicial da mecânica nova e a
        troca entra no histórico da vida. Antes da troca cada patrimônio travado da
        profissão antiga vira caixa pela regra de saída do tipo. A profissão presa a
        partido não é destino: o partido se escolhe ao entrar.
        """
        if not self.settings.uses_professions:
            raise ConflictError("A partida joga com salário igual: não há profissões.")
        if profession not in available_professions(
            inflation_adjusted=self.settings.inflation_adjusted,
            government_enabled=self.settings.government_enabled,
            funds_enabled=self.settings.funds_enabled,
        ):
            raise ConflictError("Essa profissão não existe nas regras desta partida.")
        if is_party_bound(profession):
            raise ConflictError(
                "A profissão presa a partido só se escolhe ao entrar na partida."
            )
        if self._profession_of(user.id) is profession:
            raise ConflictError("O jogador já exerce essa profissão.")
        payout = self._locked_exit_payout(user)
        self._profession_book.switch(user.id, profession, self._current_date)
        self._professions = {**self._professions, user.id: profession}
        self._offer_bankers = None
        UserManager.replace_profession(user, profession)
        self._engine.record_profession_switch(user.client_id, profession, payout)

    def _locked_exit_payout(self, user: UserDTO) -> Decimal:
        """O que os patrimônios travados da profissão atual deixam no caixa na troca de profissão: cada saldo pela regra de saída do tipo, no dia da troca."""
        day = self._current_date
        return sum(
            (
                LOCKED_EXITS[asset.kind].payout(asset.value, asset.since, day)
                for asset in self._mechanic_state_of(user.id).locked_assets
            ),
            Decimal(0),
        )

    def _run_bot_policies(
        self, users: list[UserDTO], day: date, budgets: dict[UUID, LifeBudget]
    ) -> None:
        """Cada bot toma a ação que a política da profissão dele manda no mês, pelo mesmo caminho das ações dos jogadores."""
        if not self.settings.uses_professions:
            return
        macro = self._macro.latest(day)
        health = next(
            event
            for event in self.settings.life_events
            if event.key == HEALTH_EVENT_KEY
        )
        for user in users:
            if not user.is_bot:
                continue
            reserve = Reserve(
                cash=self._engine.coverable_cash(user.client_id),
                health_cost=health.expense_multiple
                * budgets[user.client_id].paid_expense_on(day),
            )
            action = policy_action(
                self._profession_of(user.id),
                self._mechanic_state_of(user.id),
                day,
                macro,
                reserve,
            )
            if action is not None:
                self.apply_profession_action(user, action)
            self._run_payroll_policy(user, budgets[user.client_id], day)
            self._run_house_cdb_policy(user, budgets[user.client_id], reserve, day)
            self._run_exporter_policy(user, day, macro)
            self._run_freelancer_policy(user, budgets[user.client_id], day, macro)
            self._run_entrepreneur_policy(user, budgets[user.client_id], day)
            self._run_retiree_policy(user, day)
            self._run_welfare_policy(user, day)
            self._run_graduate_policy(user, budgets[user.client_id], day, macro)

    def _run_house_cdb_policy(
        self, user: UserDTO, budget: LifeBudget, reserve: Reserve, day: date
    ) -> None:
        """O Bancário-bot aplica no CDB da casa de 3 anos com a SELIC acima da média, pelo mesmo serviço da compra dos jogadores."""
        if self._profession_of(user.id) is not Profession.BANKER:
            return
        asset = self._engine.fixed_income_market.get_house_asset(
            user.client_id, BOT_HOUSE_CDB_YEARS
        )
        if asset is None or asset.player_cap is None:
            return
        amount = house_cdb_amount(
            annual_index_rate(IndicatorSeries.SELIC, day),
            monthly_average_rate(IndicatorSeries.SELIC, day, SELIC_AVERAGE_MONTHS),
            asset.player_cap - self._applied(user.client_id, asset),
            reserve,
        )
        # O caixa que a reserva enxerga é o que um débito alcança; a compra sai do caixa de fato
        amount = min(amount, self.get_cash(user.client_id)).quantize(Decimal("0.01"))
        if amount <= 0:
            return
        self._buy_fixed_income(user.client_id, asset, amount)

    def _run_freelancer_policy(
        self, user: UserDTO, budget: LifeBudget, day: date, macro: MacroMonth
    ) -> None:
        """O Autônomo-bot reajusta o preço uma vez por ano pelo IPCA de 12 meses, com 5% a mais quando o desemprego está abaixo do neutro, dentro da faixa e pelas mesmas ações dos jogadores."""
        if self._profession_of(user.id) is not Profession.FREELANCER:
            return
        state = self._mechanic_state_of(user.id)
        if not isinstance(state, FreelancerState) or not price_due(
            state, self.settings.start_date, day
        ):
            return
        target = policy_price(
            budget.price_on(day),
            annual_index_rate(IndicatorSeries.IPCA, day),
            macro.unemployment,
            NEUTRAL_UNEMPLOYMENT,
        )
        low, high = budget.price_range_on(day)
        self.set_price(user, min(max(target, low), high))

    def _gdp_quarters(self, day: date) -> list[Decimal]:
        """O PIB de 12 meses de cada trimestre fechado até `day`, em ordem: o do último mês de cada trimestre, que o jogador vê no indicador."""
        return [
            month.growth
            for month in self._macro.months_until(day)
            if month.month_end.month % MONTHS_PER_QUARTER == 0
        ]

    def _run_entrepreneur_policy(
        self, user: UserDTO, budget: LifeBudget, day: date
    ) -> None:
        """O Empreendedor-bot reinveste 30% com o PIB de 12 meses acima do neutro e nada abaixo, e vende 25% do capital uma vez por recessão de dois trimestres negativos, pelas mesmas ações dos jogadores."""
        if self._profession_of(user.id) is not Profession.ENTREPRENEUR:
            return
        state = self._mechanic_state_of(user.id)
        if not isinstance(state, EntrepreneurState):
            return
        share = policy_reinvest_share(
            budget.growth_on(day), DRIVER_CURVES[IncomeDriver.GDP].neutral
        )
        if share != state.reinvest_share:
            state = self.set_reinvest_share(user, share)
        quarters = self._gdp_quarters(day)
        sold = isinstance(state, EntrepreneurState) and policy_sale_due(state, quarters)
        if sold:
            state = self.sell_capital(user, BOT_SELL_SHARE)
        if isinstance(state, EntrepreneurState):
            marked = policy_recession_flag(state, quarters, sold)
            if marked is not state:
                self._profession_book.save_state(user.id, marked)

    def _run_retiree_policy(self, user: UserDTO, day: date) -> None:
        """O Aposentado-bot resgata o saldo inteiro na faixa de menor IR e converte metade do saldo uma vez, no primeiro mês com o juro real acima de 6% ao ano, pelas mesmas ações dos jogadores."""
        if self._profession_of(user.id) is not Profession.RETIREE:
            return
        state = self._mechanic_state_of(user.id)
        if not isinstance(state, RetireeState):
            return
        redeem = policy_redeem_amount(state, day)
        if redeem is not None:
            self.redeem_pension(user, redeem)
            return
        rate, _, _ = self._pension_real_rate(day)
        convert = policy_convert_amount(state, rate)
        if convert is not None:
            self.convert_pension(user, convert)

    @synchronized
    def enroll_course(self, user: UserDTO) -> MechanicState:
        """Matricula o jogador do Auxílio no curso técnico, pelo mesmo caminho das ações da mecânica."""
        if self._profession_of(user.id) is not Profession.WELFARE:
            raise ConflictError("Só quem vive do Auxílio faz o curso técnico.")
        return self.apply_profession_action(user, EnrollCourse())

    @synchronized
    def enroll_step(self, user: UserDTO, step: AcademicStep) -> MechanicState:
        """Matricula o Recém-formado no degrau da escada acadêmica, pelo mesmo caminho das ações da mecânica."""
        if self._profession_of(user.id) is not Profession.NEW_GRADUATE:
            raise ConflictError("Só o Recém-formado sobe a escada acadêmica.")
        if step is AcademicStep.GRADUATION:
            raise ConflictError("A graduação já vem concluída no início da carreira.")
        return self.apply_profession_action(
            user, EnrollStep(kind=f"{ENROLL_PREFIX}{step.value.lower()}")
        )

    @synchronized
    def leave_home(self, user: UserDTO) -> MechanicState:
        """O Recém-formado sai da casa dos pais: a despesa volta ao normal, sem volta."""
        state = self._graduate_state_of(user)
        if state is None:
            raise ConflictError("Só o Recém-formado mora com os pais.")
        start = self._profession_periods(user.id)[-1].start
        if state.left_home_on is None and not lives_with_parents(
            start, None, self._current_date
        ):
            raise ConflictError(
                "O desconto da casa dos pais já acabou: a despesa já voltou ao normal."
            )
        return self.apply_profession_action(user, LeaveHome())

    def _graduate_state_of(self, user: UserDTO) -> GraduateState | None:
        """O estado do Recém-formado de quem exerce a profissão; nulo para as demais ou sem profissões na partida."""
        if not self.settings.uses_professions:
            return None
        state = self._mechanic_state_of(user.id)
        return state if isinstance(state, GraduateState) else None

    def _conclude_steps(self, users: list[UserDTO], day: date) -> None:
        """Na virada do mês em que os meses do degrau fecham, ele conclui: nasce o trecho novo da curva, sem salto, e a conclusão vai ao histórico da vida."""
        for user in users:
            state = self._graduate_state_of(user)
            if state is None or state.current is None:
                continue
            if not step_concluded(state.current.enrolled_on, state.current.step, day):
                continue
            if self._life is None:
                continue
            budget = self._life_budget(self._life, user.id)
            self._profession_book.save_state(
                user.id,
                conclude_step(state, day, budget.multiple_on(day), budget.career_end),
            )
            self._engine.record_profession_action(
                user.client_id, f"{CONCLUDE_PREFIX}{state.current.step.value.lower()}"
            )

    def _run_graduate_policy(
        self, user: UserDTO, budget: LifeBudget, day: date, macro: MacroMonth
    ) -> None:
        """O Recém-formado-bot sobe o degrau seguinte só quando o que sobra da partida o paga, pela mesma ação dos jogadores."""
        state = self._graduate_state_of(user)
        if state is None:
            return
        step = policy_step(
            state,
            day,
            self.settings.end_date,
            budget.multiple_on,
            budget.base_income_on(day),
            inheritance_rate(self.settings.inflation_adjusted),
            macro.unemployment > NEUTRAL_UNEMPLOYMENT,
            budget.career_end,
        )
        if step is not None:
            self.enroll_step(user, step)

    def _welfare_state_of(self, user: UserDTO) -> WelfareState | None:
        """O estado do Auxílio de quem exerce a profissão; nulo para as demais ou sem profissões na partida."""
        if not self.settings.uses_professions:
            return None
        state = self._mechanic_state_of(user.id)
        return state if isinstance(state, WelfareState) else None

    def _conclude_courses(self, users: list[UserDTO], day: date) -> None:
        """Na virada do mês em que os 12 meses fecham, o curso técnico conclui: o jogador vira CLT e o Pé-de-Meia cai no caixa pela regra de saída."""
        for user in users:
            state = self._welfare_state_of(user)
            if (
                state is not None
                and state.course_enrolled_on is not None
                and course_concluded(state.course_enrolled_on, day)
            ):
                self.switch_profession(user, Profession.CLT)

    def _run_welfare_month(self, user: UserDTO, budget: LifeBudget, day: date) -> None:
        """
        A virada do mês do Auxílio, antes da renda do mês cair: o Pé-de-Meia recebe o
        depósito da sobra do mês que fechou, e o patrimônio líquido de hoje fica
        guardado como o início do mês que abre. O dinheiro é do governo: o caixa não muda.
        """
        state = self._welfare_state_of(user)
        if state is None:
            return
        turn = month_turn(
            state,
            self._engine.liquid_wealth(user.client_id),
            budget.net_salary_on(day),
            budget.levers_on(day).welfare_spending,
        )
        self._profession_book.save_state(user.id, turn.state)

    def _run_welfare_savings(self, users: list[UserDTO]) -> None:
        """
        No fim do pregão, depois do juro do cheque especial: o caixa negativo do dia
        marca o período, e a data de liberação do Pé-de-Meia paga o saldo inteiro ou
        o adia, pela marca. Os dois casos entram no histórico da vida.
        """
        day = self._current_date
        start = self.settings.start_date
        for user in users:
            state = self._welfare_state_of(user)
            if state is None:
                continue
            marked = mark_negative_cash(state, self.get_cash(user.client_id))
            if release_due(marked, start, day):
                result = release(marked, start, day)
                self._profession_book.save_state(user.id, result.state)
                if result.postponed and marked.balance > 0:
                    self._engine.record_profession_action(
                        user.client_id, SAVINGS_POSTPONED
                    )
                elif result.released > 0:
                    self._engine.record_profession_action(
                        user.client_id, SAVINGS_RELEASED, result.released
                    )
            elif marked is not state:
                self._profession_book.save_state(user.id, marked)

    def _broker_state_of(self, user: UserDTO) -> BrokerState | None:
        """O estado do Corretor de quem exerce a profissão; nulo para as demais ou sem profissões na partida."""
        if not self.settings.uses_professions:
            return None
        state = self._mechanic_state_of(user.id)
        return state if isinstance(state, BrokerState) else None

    def _run_broker_month(self, users: list[UserDTO], day: date) -> None:
        """
        Na virada do mês cada Corretor guarda o volume que a sala negociou no mês civil
        que fechou e quantos Corretores o dividem: a comissão desse mês entra com o
        salário de hoje. O volume vem dos eventos já gravados, até o dia anterior.
        """
        brokers = [
            (user, state)
            for user in users
            if (state := self._broker_state_of(user)) is not None
        ]
        if not brokers:
            return
        volume = repository.event.get_traded_volume(
            self.settings.id, previous_month_start(day), day.replace(day=1)
        )
        for user, state in brokers:
            self._profession_book.save_state(
                user.id,
                state.model_copy(update={"volume": volume, "brokers": len(brokers)}),
            )

    def _house_months_issued(self) -> set[date]:
        """Os meses da sala que já têm relatório."""
        if self._house_months is None:
            self._house_months = set(repository.house_report.months(self.settings.id))
        return self._house_months

    def _house_open_ones(self) -> list[HouseRecommendationDTO]:
        """As recomendações da casa que ainda esperam o desfecho."""
        if self._house_open is None:
            self._house_open = repository.house_report.open_before(
                self.settings.id, date.max
            )
        return self._house_open

    def _house_report_of(self, month: date) -> HouseReportDTO:
        """O relatório do mês, como foi guardado."""
        items = repository.house_report.of_month(self.settings.id, month)
        return HouseReportDTO(month=month, issued_on=items[0].issued_on, items=items)

    @synchronized
    def get_house_picks(self, client_id: UUID) -> list[HousePickDTO]:
        """A ação e o lado de cada recomendação do relatório vigente; só o Corretor vê, e quem não é recebe a lista vazia."""
        user_id = UserManager.get_user_id(client_id)
        if (
            not self.settings.uses_professions
            or self._profession_of(user_id) is not Profession.BROKER
        ):
            return []
        months = self._house_months_issued()
        if not months:
            return []
        return picks_of(repository.house_report.of_month(self.settings.id, max(months)))

    def _run_house_report(self, users: list[UserDTO], candles: list[CandleDTO]) -> None:
        """
        No fim do pregão, depois da gravação do dia: o desfecho das recomendações em
        aberto com a máxima, a mínima e o fechamento de hoje e, no 5º dia útil do mês, o
        relatório da casa da sala, que o Corretor-bot já age no mesmo dia. O relatório
        guardado nunca é recalculado.
        """
        if not self.settings.uses_professions:
            return
        day = self._current_date
        reports = repository.house_report
        verdicts = verdicts_of(
            self._house_open_ones(), candles, day, next_business_day(day)
        )
        if verdicts:
            reports.resolve(verdicts, day)
            self._house_open = [
                item for item in self._house_open_ones() if item.id not in verdicts
            ]
        month = day.replace(day=1)
        if day == report_day(month) and month not in self._house_months_issued():
            self._issue_house_report(users, candles, day, month)
        self._run_broker_bot_sales(users, day)

    def _issue_house_report(
        self, users: list[UserDTO], candles: list[CandleDTO], day: date, month: date
    ) -> None:
        """Sorteia o relatório do mês entre as ações negociadas hoje, guarda e avisa os Corretores."""
        tradable = tradable_today(candles, day)
        if not tradable:
            return
        future = repository.stock.get_highs_lows_between(
            [candle.ticker for candle in tradable],
            day,
            horizon_end(day, self.settings.end_date),
            self.settings.id,
        )
        drafts = draw_report(
            str(self._random_seed),
            day,
            self.settings.end_date,
            candidates_of(tradable, future),
        )
        if not drafts:
            return
        items = repository.house_report.insert_report(
            self.settings.id, month, day, drafts
        )
        self._house_months_issued().add(month)
        self._house_open = [*self._house_open_ones(), *items]
        for user in users:
            if user.is_bot or self._broker_state_of(user) is None:
                continue
            notify(
                "house_report_issued",
                HouseReportIssuedEventDTO(month=month, issued_on=day).to_json(),
                to=user.client_id,
            )
        self._run_broker_bot_buys(users, day, items)

    def _run_broker_bot_buys(
        self, users: list[UserDTO], day: date, items: list[HouseRecommendationDTO]
    ) -> None:
        """
        No dia do relatório o Corretor-bot compra as recomendações de compra com 20% do
        patrimônio (até o caixa livre), em partes iguais, por valor e pelo mesmo caminho das ordens dos
        jogadores; a quantidade que entrou de cada uma fica no estado dele para a venda
        no prazo. As recomendações de venda ele ignora.
        """
        buys = bot_buys(items)
        if not buys:
            return
        for user in users:
            state = self._broker_state_of(user)
            if not user.is_bot or state is None:
                continue
            sheet = self._engine.balance_sheet(user.client_id)
            each = bot_budget_each(
                sheet.total_equity + sheet.total_fixed + sheet.total_cash,
                sheet.total_cash,
                len(buys),
            )
            if each <= 0:
                continue
            bought = dict(state.bought)
            for item in buys:
                order = MarketOrder(
                    placed_on=day,
                    client_id=user.client_id,
                    ticker=item.ticker,
                    size=Decimal(0),
                    action=OrderAction.BUY,
                    budget=each,
                )
                try:
                    self.create_order(order, by_policy=True)
                except (ConflictError, UnprocessableEntityError, InsufficentCashError):
                    continue
                # A compra por valor fecha com o tamanho que executou
                if order.size > 0:
                    bought[str(item.id)] = order.size
            self._profession_book.save_state(
                user.id, state.model_copy(update={"bought": bought})
            )

    def _run_broker_bot_sales(self, users: list[UserDTO], day: date) -> None:
        """O Corretor-bot vende o que comprou de cada recomendação no último pregão do prazo dela."""
        next_day = next_business_day(day)
        for user in users:
            state = self._broker_state_of(user)
            if not user.is_bot or state is None or not state.bought:
                continue
            recommendations = repository.house_report.by_ids(
                [int(key) for key in state.bought]
            )
            bought = dict(state.bought)
            for key, quantity in state.bought.items():
                item = recommendations.get(int(key))
                if item is not None and next_day <= item.deadline:
                    continue
                if item is not None:
                    free = self._engine.broker.get_available_position(
                        user.client_id, item.ticker
                    )
                    size = min(quantity, free)
                    if size > 0:
                        try:
                            self.create_order(
                                MarketOrder(
                                    placed_on=day,
                                    client_id=user.client_id,
                                    ticker=item.ticker,
                                    size=size,
                                    action=OrderAction.SELL,
                                ),
                                by_policy=True,
                            )
                        except ConflictError:
                            continue
                        except UnprocessableEntityError:
                            pass
                del bought[key]
            if bought != state.bought:
                self._profession_book.save_state(
                    user.id, state.model_copy(update={"bought": bought})
                )

    def _run_welfare_policy(self, user: UserDTO, day: date) -> None:
        """O Auxílio-bot se matricula no curso técnico no primeiro mês da partida com 10 anos ou mais, pela mesma ação dos jogadores."""
        state = self._welfare_state_of(user)
        if state is not None and policy_enroll(
            state, self.settings.start_date, self.settings.end_date
        ):
            self.enroll_course(user)

    def _run_pension_month(self, user: UserDTO, day: date) -> None:
        """O saldo da previdência no pagamento do mês: rende o CDI menos 1% ao ano, sem IR."""
        state = (
            self._mechanic_state_of(user.id) if self.settings.uses_professions else None
        )
        if not isinstance(state, RetireeState):
            return
        self._profession_book.save_state(
            user.id,
            pay_pension_month(state, annual_index_rate(IndicatorSeries.CDI, day)),
        )

    def _run_capital_month(
        self, user: UserDTO, budget: LifeBudget, day: date, profit: Decimal
    ) -> None:
        """
        O capital da empresa no pagamento do mês: o rendimento sobre o capital do dia
        (positivo no caixa, negativo no capital) e a fração do lucro `profit` que sai do
        caixa para o capital.
        """
        state = (
            self._mechanic_state_of(user.id) if self.settings.uses_professions else None
        )
        if not isinstance(state, EntrepreneurState):
            return
        paid, reinvested, income = pay_month(state, budget.growth_on(day), profit)
        self._profession_book.save_state(user.id, paid)
        if income > 0:
            self._engine.pay_capital_income(user.client_id, income)
        if reinvested > 0:
            self._engine.reinvest_profit(user.client_id, reinvested)

    def _run_exporter_policy(self, user: UserDTO, day: date, macro: MacroMonth) -> None:
        """O Exportador-bot ajusta o mix pelo dólar e pelo PIB de 12 meses e trava o dólar acima da média, pelas mesmas ações dos jogadores."""
        if self._profession_of(user.id) is not Profession.EXPORTER:
            return
        state = self._mechanic_state_of(user.id)
        if not isinstance(state, ExporterState):
            return
        target = mix_target(self._dollar_change_on(day), macro.growth)
        if target != state.export_share and mix_change_allowed(state, day):
            state = self.set_export_mix(user, target)
        dollar_start = self._dollar_history_start()
        turn_dollars = [
            self._engine.dollar_on(turn)
            for turn in month_turns(day, BOT_DOLLAR_AVERAGE_MONTHS)
            if dollar_start is not None and turn >= dollar_start
        ]
        if isinstance(state, ExporterState) and lock_wanted(
            state, self._engine.dollar_on(day), turn_dollars
        ):
            self.lock_exchange(user, BOT_LOCK_SHARE, BOT_LOCK_MONTHS)

    def _dollar_history_start(self) -> date | None:
        """O primeiro dia da série do dólar; antes dele o motor devolve paridade, que não entra na média do bot."""
        return repository.economic.get_history(IndicatorSeries.PTAX, stored=True).start

    def _run_exchange_lock_month(
        self, user: UserDTO, budget: LifeBudget, day: date, salary_paid: bool
    ) -> None:
        """
        O pagamento do mês com a trava de câmbio: soma o que a trava rendeu e conta o
        mês; no último pagamento a trava vence e o histórico registra o fim.
        """
        state = self._exporter_state_of(user.id)
        if state is None or state.lock is None or not salary_paid:
            return
        state, ended = after_payment(state, budget.lock_gain_on(day))
        self._profession_book.save_state(user.id, state)
        if ended:
            self._engine.record_profession_action(user.client_id, EXCHANGE_LOCK_ENDED)

    def _exporter_state_of(self, user_id: int) -> ExporterState | None:
        """O estado do Exportador de quem exerce a profissão na partida com profissões; nulo para as demais."""
        if not self.settings.uses_professions:
            return None
        state = self._mechanic_state_of(user_id)
        return state if isinstance(state, ExporterState) else None

    def _house_cdb_caps(self, day: date) -> dict[UUID, Decimal]:
        """O teto do CDB da casa de cada Bancário da partida: um salário líquido do mês de `day`."""
        if self._life is None or not self.settings.uses_professions:
            return {}
        caps: dict[UUID, Decimal] = {}
        for user in repository.simulation_player.participants(self.settings.id):
            if self._profession_of(user.id) is not Profession.BANKER:
                continue
            salary = self._life_budget(self._life, user.id).net_salary_on(day)
            if salary > 0:
                caps[user.client_id] = salary
        return caps

    def _run_payroll_policy(self, user: UserDTO, budget: LifeBudget, day: date) -> None:
        """O Servidor-bot contrata o consignado com o Ibovespa fundo e o quita na volta ao topo, pelo mesmo serviço das rotas dos jogadores."""
        if self._profession_of(user.id) is not Profession.PUBLIC_SERVANT:
            return
        book = self._engine.credit_book
        loans = book.payroll_loans(user.client_id)
        move = payroll_policy(stocks_drawdown(day), bool(loans))
        if move is PayrollMove.TAKE:
            margin = book.payroll_margin(user.client_id, budget.net_salary_on(day))
            amount = payroll_amount(margin, book.payroll_rate(day))
            if amount > 0:
                self.contract_payroll(user, user.client_id, amount, PAYROLL_TERM_MONTHS)
        elif move is PayrollMove.PAY_OFF:
            for loan in loans:
                self._engine.cover_before_debit(
                    user.client_id, loan.payoff_on(day), CashflowEventType.LOAN_PAYMENT
                )
                try:
                    self.payoff_loan(user, user.client_id, loan.loan_id)
                except InsufficentCashError:
                    # Sem caixa nem renda fixa para vender, a quitação fica para o mês seguinte
                    return

    def _clt_state_of(self, user_id: int) -> CltState | None:
        """O estado do CLT de quem exerce a profissão na partida com profissões; nulo para as demais."""
        if not self.settings.uses_professions:
            return None
        state = self._mechanic_state_of(user_id)
        return state if isinstance(state, CltState) else None

    def _locked_assets_of(self, client_id: UUID) -> list[LockedAssetDTO]:
        """Os patrimônios travados da conta `client_id`, que entram no patrimônio dela; só o jogador com mecânica tem."""
        user = UserManager.get_user(client_id)
        if user is None or not self.settings.uses_professions:
            return []
        return self._mechanic_state_of(user.id).locked_assets

    def _end_overtime_in_recession(self, users: list[UserDTO], day: date) -> None:
        """
        Na virada do mês, a hora extra ligada acaba sozinha se o PIB de 12 meses ficou
        negativo, e a que a recessão desligou avisa o jogador quando volta a ser possível;
        os dois casos entram no histórico.
        """
        macro = self._macro.latest(day)
        for user in users:
            state = self._clt_state_of(user.id)
            if state is None:
                continue
            if overtime_ends_with_recession(state, macro):
                self._profession_book.save_state(user.id, end_overtime(state))
                self._engine.record_profession_action(user.client_id, OVERTIME_ENDED)
            elif overtime_returns(state, macro):
                self._profession_book.save_state(user.id, clear_overtime_waiting(state))
                if user.is_bot:
                    continue
                self._engine.record_profession_action(
                    user.client_id, OVERTIME_AVAILABLE
                )
                notify(
                    "overtime_available",
                    OvertimeAvailableEventDTO(event_date=day).to_json(),
                    to=user.client_id,
                )

    def _run_fgts_month(
        self, user: UserDTO, budget: LifeBudget, day: date, salary_paid: bool
    ) -> None:
        """O FGTS do mês: o saldo rende com a TR e, com o salário pago, recebe o depósito sobre o bruto da renda de CLT."""
        state = self._clt_state_of(user.id)
        if state is None:
            return
        tr = last_known_rate(IndicatorSeries.TR, day)
        gross = (
            budget.salary_on(day) if budget.presidency_multiple is None else Decimal(0)
        )
        self._profession_book.save_state(
            user.id,
            after_month(
                state,
                gross,
                Decimal(0) if tr is None else from_percent(tr),
                salary_paid,
            ),
        )

    def _pay_out_fgts(self, user: UserDTO) -> None:
        """Na demissão sorteada o saldo do FGTS e a multa caem no caixa, a conta recomeça do zero e a hora extra desliga."""
        state = self._clt_state_of(user.id)
        if state is None:
            return
        reset, payout = after_layoff(state)
        self._profession_book.save_state(user.id, reset)
        if payout > 0:
            self._engine.withdraw_fgts(user.client_id, payout)

    def party_abbrs(self) -> frozenset[str]:
        """As siglas dos partidos da partida; vazio sem o Governo & Política."""
        return (
            frozenset() if self._government is None else self._government.party_abbrs()
        )

    def _bankers_of_offers(self) -> list[UUID]:
        """Os jogadores que são Banqueiros de ofertas na partida."""
        if self._offer_bankers is None:
            professions = repository.simulation_player.professions(self.settings.id)
            self._offer_bankers = [
                user.client_id
                for user in repository.simulation_player.participants(self.settings.id)
                if professions.get(user.id) is Profession.OFFERS_BANKER
            ]
        return self._offer_bankers

    def _charge_overdraft(self, users: list[UserDTO]):
        rate = _overdraft_rate(self._current_date)
        for user in users:
            interest = overdraft_interest(self.get_cash(user.client_id), rate)
            if interest > 0:
                self._engine.charge_overdraft_interest(user.client_id, interest)

    def get_life_status(self, client_id: UUID) -> LifeStatusDTO | None:
        """A vida financeira de `client_id` hoje; None fora do viver de renda."""
        if self._life is None:
            return None
        day = self._current_date
        seed, per_year = self._random_seed, self.settings.unexpected_per_year
        start = self.settings.start_date
        budget = self._life_budget(self._life, UserManager.get_user_id(client_id))
        loss = budget.income_loss()
        expense = budget.expense_on(day)
        cash = self.get_cash(client_id)
        rate = _overdraft_rate(day)
        # A reserva soma o caixa e a liquidez diária líquida, e nunca fica negativa
        positions = list(self.get_fixed_positions(client_id).values())
        policy = self._tax_policy()
        daily_liquidity = total_redeemable(
            positions, day, policy, self._engine.fixed_quotes()
        )
        reserve = max(cash + daily_liquidity, Decimal(0))
        reserve_cash = max(cash, Decimal(0))
        return LifeStatusDTO(
            monthly_salary=budget.net_salary_on(day),
            monthly_expense=expense,
            salary_skipped_by=layoff_in(
                seed,
                day.replace(day=1) - timedelta(days=1),
                per_year,
                start,
                self.settings.life_events,
                layoff_factor_on=self._layoff_factor_for(budget),
                frequencies=self.settings.life_frequencies,
            )
            if loss is not None
            else None,
            next_salary_skipped_by=layoff_in(
                seed,
                day,
                per_year,
                start,
                self.settings.life_events,
                until=day,
                layoff_factor_on=self._layoff_factor_for(budget),
                frequencies=self.settings.life_frequencies,
            )
            if loss is not None
            else None,
            goal=budget.goal_on(day),
            inflation_adjusted=self.settings.inflation_adjusted,
            withdrawal_rate=self.settings.withdrawal_rate,
            unexpected_per_year=per_year,
            overdraft_monthly_rate=rate,
            overdraft_daily_interest=overdraft_interest(cash, rate),
            reserve_months=reserve / expense,
            reserve_cash=reserve_cash,
            reserve_daily_liquidity=reserve - reserve_cash,
            cover_with_treasury=repository.settings.get_cover_with_treasury(
                UserManager.get_user_id(client_id)
            ),
            **self._profession_status(budget, day),
        )

    def _profession_status(self, budget: LifeBudget, day: date) -> dict:
        """O que a profissão do jogador sente no dia; vazio com salário igual."""
        if not self.settings.uses_professions:
            return {}
        rule = budget.rule
        levers = budget.levers_on(day)
        raised = rule.real_raise in (RealRaise.SERVANTS, RealRaise.RETIREES)
        return {
            "profession": budget.profession,
            "income_loss": budget.income_loss(),
            "health_multiple": budget.health_multiple,
            "tax": rule.tax,
            "tax_rate": budget.tax_rate_on(day),
            "tax_reference": budget.tax_reference(),
            "real_raise": levers.real_raise_of(rule.real_raise) if raised else None,
            "welfare_spending": levers.welfare_spending
            if rule.benefit_multiple > 0
            else None,
            "driver": rule.driver,
            "driver_value": budget.driver_value_on(day),
        }

    @synchronized
    def get_life_history(self, client_id: UUID) -> list[LifeHistoryRowDTO]:
        """O histórico do viver de renda de `client_id`: os eventos de caixa e, na ordem das datas, as mudanças do orçamento com a origem na economia."""
        events = repository.event.get_cashflow_events(
            self.settings.id, UserManager.get_portfolio_id(client_id)
        )
        if self._life is None:
            return build_life_history(events, self.settings.life_events)
        user_id = UserManager.get_user_id(client_id)
        periods = self._profession_periods(user_id)
        changes: list[BudgetChange] = []
        history_periods: list[HistoryPeriod] = []
        for index, period in enumerate(periods):
            following = periods[index + 1].start if index + 1 < len(periods) else None
            # Só o trecho atual tem o estado da mecânica; os anteriores são de outra profissão
            budget = self._with_party(
                self._life.for_profession(period.profession), user_id
            ).with_profession_start(period.start)
            if following is None:
                budget = self._with_mechanic(budget, user_id)
            changes += budget_changes(
                budget,
                self._current_date if following is None else following,
                _overdraft_rate,
                since=None if index == 0 else period.start,
            )
            history_periods.append(
                HistoryPeriod(
                    period.start,
                    period.profession if self.settings.uses_professions else None,
                    budget.income_loss(),
                )
            )
        return build_life_history(
            events,
            self.settings.life_events,
            changes,
            lambda day: self._macro.latest(day).unemployment,
            history_periods,
        )

    def _profession_periods(self, user_id: int) -> list[ProfessionPeriodDTO]:
        """Os períodos de profissão do jogador; sem período gravado, a profissão dele vale desde o início da partida."""
        return self._profession_book.periods_of(user_id) or [
            ProfessionPeriodDTO(
                profession=self._profession_of(user_id),
                start=self.settings.start_date,
            )
        ]

    @synchronized
    def get_current_date(self) -> date:
        return self._current_date

    @synchronized
    def next_statistics_update(self) -> date | None:
        """Dia em que as estatísticas fecham o mês de novo; nulo quando a partida acaba antes."""
        turn = next_month_turn(self._current_date)
        return turn if turn <= self.settings.end_date else None

    @synchronized
    def last_statistics_update(self) -> date | None:
        """Dia em que as estatísticas fecharam o mês pela última vez; nulo antes da primeira virada da partida."""
        turn = last_month_turn(self._current_date)
        return turn if turn > self.settings.start_date else None

    def get_current_date_formatted(self) -> str:
        return self._current_date.strftime("%d/%m/%Y")

    @synchronized
    def set_speed(self, speed: int, reason: PauseReason = PauseReason.HOST):
        logger.info("Velocidade da simulação alterada para %sx", speed)
        self._speed = speed
        if speed <= 0:
            self._pause_reason = reason

    def get_speed(self) -> int:
        return self._speed

    def get_pause_reason(self) -> PauseReason | None:
        """O motivo da pausa; nulo com a partida em andamento."""
        return self._pause_reason if self._speed <= 0 else None

    @synchronized
    def get_stocks(self) -> list[CandleDTO]:
        return [
            self._price_impact.apply(stock)
            for stock in repository.stock.get_stocks_by_date(self._current_date)
        ]

    @synchronized
    def get_market(self) -> list[MarketQuoteDTO]:
        """As cotações do dia com os 30 pregões do mini gráfico; o último ponto é o de hoje, com impacto."""
        closes = repository.stock.get_recent_closes(self._current_date, SPARKLINE_DAYS)
        classification = self._engine.classification
        state_tickers = (
            self._government.state_companies().state_tickers()
            if self._government
            else set()
        )

        def quote_of(candle: CandleDTO, *, fund: bool) -> MarketQuoteDTO:
            history = closes.get(candle.ticker, [])
            segment = classification.get(candle.ticker)
            return MarketQuoteDTO(
                **candle.model_dump(),
                sparkline=[*history[:-1], candle.close] if history else [candle.close],
                sector=segment.sector if segment else None,
                segment=segment.segment if segment else None,
                state_owned=candle.ticker in state_tickers,
                fund=fund,
            )

        quotes = [quote_of(candle, fund=False) for candle in self.get_stocks()]
        # As cotas de gestora com a oferta aberta ou já negociando; a gestora fechada fica fora
        quotes.extend(
            quote_of(candle, fund=True) for candle in self._listed_fund_candles()
        )
        return quotes

    def _listed_fund_candles(self) -> list[CandleDTO]:
        """A última vela de cada cota listada."""
        if self._funds is None:
            return []
        return self._funds.listed_candles(self._current_date)

    @synchronized
    def get_stock_details(self, ticker: str) -> StockDetailsDTO | None:
        fund = self._funds.find(ticker) if self._funds is not None else None
        # A cota só existe para a partida depois que a gestora abre a oferta, e some com a fusão
        if fund is not None and not fund.listed:
            return None
        if self._funds is not None and self._funds.is_merged(ticker):
            return None
        details = repository.stock.get_stock_details(ticker, self._current_date)
        if details is None:
            return None
        # A cota no pregão da estreia ainda não tem vela salva: o preço é o da vela plana do motor
        if fund is not None and not details.history:
            listed = next(
                (c for c in self._listed_fund_candles() if c.ticker == ticker), None
            )
            if listed is not None:
                details = details.model_copy(update=listed.model_dump())
        return self._price_impact.apply(details).model_copy(
            update={
                "history": self._price_impact.apply_history(ticker, details.history),
                "fund_id": fund.terms.id if fund is not None else None,
            }
        )

    @synchronized
    def get_portfolio_ticker(self, client_id: UUID, ticker: str) -> PositionDTO:
        positions = self._engine.get_positions(client_id)
        position = positions.get(ticker)
        return (
            position.to_dto(self._engine.get_current_price(position))
            if position
            else PositionDTO(
                ticker=ticker,
                size=Decimal(0),
                reserved=Decimal(0),
                total_cost=Decimal(0),
                avg_price=Decimal(0),
                current_price=Decimal(0),
                current_value=Decimal(0),
                return_value=Decimal(0),
                return_pct=Decimal(0),
            )
        )

    @synchronized
    def get_dividends(self, client_id: UUID) -> PortfolioDividendsDTO:
        """Os proventos que o jogador recebeu na partida, até hoje."""
        payments = repository.portfolio.get_dividend_payments(
            UserManager.get_portfolio_id(client_id)
        )
        return build_portfolio_dividends(payments, self._current_date)

    @synchronized
    def get_asset_corporate_events(
        self, client_id: UUID, ticker: str
    ) -> AssetCorporateEventsDTO | None:
        """Proventos e desdobramentos do ativo até hoje, com o que cada um fez na carteira do jogador."""
        stock = self._engine.stocks.get(ticker)
        if stock is None:
            return None
        portfolio_id = UserManager.get_portfolio_id(client_id)
        position = self._engine.get_positions(client_id).get(ticker)
        last = self._engine.matching_engine.market_data.get_last(ticker)
        return build_asset_events(
            ticker=ticker,
            asset_class=stock.asset_class,
            events=self._engine.corporate_events(
                repository.corporate_event.get_for_stock(
                    stock.id, self._current_date, self.settings.id
                )
            ),
            equity_events=[
                e
                for e in repository.portfolio.get_equity_events(portfolio_id)
                if e.ticker == ticker
            ],
            payments=[
                p
                for p in repository.portfolio.get_dividend_payments(portfolio_id)
                if p.ticker == ticker
            ],
            match_start=self.settings.start_date,
            per_share=self._engine.dividends_per_share(self._current_date).get(
                stock.id, Decimal(0)
            ),
            price=to_money(last.close) if last else Decimal(0),
            avg_price=position.avg_price if position and position.size > 0 else None,
        )

    @synchronized
    def get_economic_indicators(self) -> EconomicIndicatorsDTO:
        return EconomicIndicatorsDTO(
            ipca=annual_index_rate(IndicatorSeries.IPCA, self._current_date),
            selic=annual_index_rate(IndicatorSeries.SELIC, self._current_date),
            cdi=annual_index_rate(IndicatorSeries.CDI, self._current_date),
            fed=annual_index_rate(IndicatorSeries.FED_FUNDS, self._current_date),
        )

    @synchronized
    def get_economy_panel(self) -> EconomyPanelDTO:
        return build_economy_panel(
            self.settings.start_date,
            self._current_date,
            self._macro,
            self._government.linked() if self._government is not None else None,
            self._government.economy() if self._government is not None else None,
            self._government.state.measures.values()
            if self._government is not None
            else (),
        )

    @synchronized
    def preview_order(
        self,
        client_id: UUID,
        ticker: str,
        action: OrderAction,
        quantity: Decimal | None,
        limit_price: float | None,
        amount: Decimal | None = None,
        max_size: bool = False,
    ) -> OrderPreviewDTO:
        preview = self._engine.preview_order(
            client_id, ticker, action, quantity, limit_price, amount, max_size
        )
        if action is not OrderAction.BUY:
            return preview
        return preview.model_copy(
            update={
                "sovereign": self._sovereign_preview(
                    client_id, ticker, preview.quantity
                )
            }
        )

    @synchronized
    def watch_order_preview(
        self,
        requester: UUID,
        account: int | None,
        ticker: str,
        request: OrderPreviewRequest,
    ) -> OrderPreviewDTO:
        """A prévia de agora; o pedido fica registrado e a prévia nova chega pelo aviso `order_preview:{ticker}`."""
        return self._feed.watch_preview(requester, account, ticker, request)

    @synchronized
    def watch_fixed_income_projection(
        self, requester: UUID, account: int | None, asset_id: str, amount: Decimal
    ) -> FixedIncomeQuoteDTO:
        """A cotação de agora; o valor fica registrado e a cotação nova chega pelo aviso `fixed_income_projection:{id}`."""
        return self._cash_feed.watch_projection(requester, account, asset_id, amount)

    @synchronized
    def watch_indicators(
        self, requester: UUID, ticker: str, request: IndicatorsRequestDTO
    ) -> TechnicalIndicatorsDTO | None:
        """Os indicadores de agora; o pedido fica registrado e o ponto novo chega pelo aviso `indicators_update:{ticker}`."""
        return self._feed.watch_indicators(requester, ticker, request)

    def _refresh_order_previews(self) -> None:
        # A varredura roda dentro do lock, como uma operação sincronizada: as consultas
        # dela não disparam a varredura de novo
        self._sync_depth += 1
        try:
            self._feed.refresh_previews()
        except Exception:
            logger.exception("Falha ao atualizar as prévias de ordem")
        finally:
            self._sync_depth -= 1

    @synchronized
    def get_orders(self, ticker: str) -> list[OrderDTO]:
        orders = self._engine.matching_engine.order_book.get_orders(ticker)
        return [o.to_dto() for o in orders]

    @synchronized
    def clear_user_cache(self, client_id: UUID) -> None:
        EventManager.flush()
        # Remove saldo em cache
        self._engine._cash.pop(client_id, None)
        # Remove posições de renda variável em cache
        self._engine.broker._positions.pop(client_id, None)
        # Remove ativos de renda fixa em cache
        self._engine.fixed_broker._assets.pop(client_id, None)
        # Remove os empréstimos em cache
        self._engine.credit_book.forget(client_id)

    def _pause_for_result(self, reason: PauseReason) -> None:
        """O resultado de um turno pausa a partida para todos, com o dia já apurado."""
        self.set_speed(0, reason)
        simulation_controller.pause()
        notify(
            "speed_update",
            SpeedUpdateEventDTO(speed=0, pause_reason=reason).to_json(),
        )

    def _has_month_changed(self) -> bool:
        current_month = (self._current_date.year, self._current_date.month)

        if self._last_contribution_month != current_month:
            self._last_contribution_month = current_month
            return True

        return False

    def _apply_monthly_contributions(self, users: list[UserDTO]):
        if self.settings.monthly_contribution <= 0:
            return

        for user in users:
            self._engine.add_contribution(
                user.client_id, self.settings.monthly_contribution
            )

    def _settle_credit(self, users: list[UserDTO], month_changed: bool):
        """
        A nota do mês que fechou vale antes das parcelas do dia, e as parcelas saem
        do caixa antes do IR e do juro do cheque especial.
        """
        credit = self._engine.credit_book
        client_ids = [user.client_id for user in users]
        # As gestoras pagam as parcelas dos empréstimos pelo caixa delas
        if self._funds is not None:
            client_ids += self._funds.client_ids
        if month_changed:
            credit.close_month(client_ids, self._current_date)
        credit.process_due(client_ids, self._current_date, self._speed)
        credit.monthly_summary(client_ids, self._current_date, self._speed)

    def _collect_income_tax(self, users: list[UserDTO]):
        """
        O DARF do mês anterior vence no último dia útil do mês. O evento TAX fica
        datado do vencimento e a retomada começa no dia seguinte ao último evento,
        então cada DARF sai do caixa uma vez só.
        """
        if next_business_day(self._current_date).month == self._current_date.month:
            return

        for user in users:
            months = self._engine.assess_income_tax(
                SimulationManager.get_portfolio_id(user.id)
            )
            darf = next(
                (m.darf_amount for m in months if m.due_date == self._current_date),
                None,
            )
            if darf:
                self._engine.pay_income_tax(user.client_id, darf)

    def _create_daily_snapshots(
        self, users: list[UserDTO], month_changed: bool
    ) -> list[StatisticsSnapshotEntryDTO]:
        """
        `statistics_snapshot_update` faz a tela de Estatísticas buscar o histórico
        inteiro de novo, então sai só na virada do mês, depois de o relatório guardado
        do mês anterior sair; `snapshot_update` é um merge por data no cache da
        Carteira e sai todo dia.
        """
        snapshots_payload = self._snapshot_users(users)

        if month_changed:
            self.statistics.clear()
            notify(
                event="statistics_snapshot_update",
                payload=StatisticsSnapshotUpdateEventDTO(
                    snapshots=snapshots_payload
                ).to_json(),
            )
        return snapshots_payload

    def _snapshot_users(self, users: list[UserDTO]) -> list[StatisticsSnapshotEntryDTO]:
        """Grava o snapshot do dia de `users` de uma vez, avisa a carteira de cada um e devolve as linhas das Estatísticas."""
        balances = {}
        for user in users:
            balance = self._engine.balance_sheet(user.client_id)
            balances[SimulationManager.get_portfolio_id(user.id)] = DayBalanceDTO(
                balance.total_equity,
                balance.total_fixed,
                balance.total_debt,
                balance.equity_by_class,
                balance.total_locked,
            )
        snapshots = repository.snapshot.create_snapshots(self._current_date, balances)

        entries = []
        for user in users:
            snapshot = snapshots[SimulationManager.get_portfolio_id(user.id)]
            notify(
                event="snapshot_update",
                payload=SnapshotUpdateEventDTO(
                    snapshot=self._history_point(
                        PatrimonialHistoryDTO.model_validate(
                            snapshot.model_dump(
                                include=set(PatrimonialHistoryDTO.model_fields)
                            )
                        ),
                        snapshot.portfolio_id,
                    )
                ).to_json(),
                to=user.client_id,
            )
            entries.append(
                StatisticsSnapshotEntryDTO(
                    player_nickname=user.nickname, snapshot=snapshot
                )
            )
        return entries

    @synchronized
    def starting_cash_for(self, profession: Profession | None) -> Decimal:
        """O caixa com que quem entra hoje começa: o da profissão, ou o da sala sem o viver de renda."""
        if self._life is None or profession is None:
            return self.settings.starting_cash
        return self._life.for_profession(profession).starting_capital(
            self.settings.starting_cash, self._current_date, self.settings.end_date
        )

    @synchronized
    def add_player(self, user: UserDTO, cash: Decimal) -> None:
        """
        Quem entra com a partida em andamento recebe o depósito inicial `cash` (o mesmo
        que a carteira dele guarda) no dia corrente e o snapshot desse dia; o aporte
        mensal e os snapshots seguintes já o incluem porque `participants` lê a linha
        dele em `simulation_players`.
        """
        self._offer_bankers = None
        self._profession_book.forget()
        if cash > 0:
            self._engine.add_cash(user.client_id, cash)
        EventManager.flush()
        self._snapshot_users([user])
        self.statistics.clear()
