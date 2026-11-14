from __future__ import annotations

import logging
import re
import threading
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar
from uuid import UUID

from backend import config
from backend.core import repository
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
    FundBuybackDTO,
    FundBuybackPreviewDTO,
    FundBuybackRequest,
    FundContributionRequest,
    FundContributionResponse,
    FundDetailsDTO,
    FundFeesRequest,
    FundFoundRequest,
    FundIssuanceDTO,
    FundIssuancePreviewDTO,
    FundIssuanceRequest,
    FundIssuanceSubscriptionPreviewDTO,
    FundIssuanceSubscriptionRequest,
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
    MapPanelDTO,
    MapTimelineDTO,
    MeasurePreviewDTO,
    PromisesPanelDTO,
    ProposeMeasureRequest,
)
from backend.core.dto.life import (
    LifeEventDTO,
    LifeEventTypeDTO,
    LifeHistoryRowDTO,
    LifeStatusDTO,
)
from backend.core.dto.order import OrderDTO
from backend.core.dto.order_preview import OrderPreviewDTO
from backend.core.dto.patrimonial_history import (
    PatrimonialHistoryDTO,
    PortfolioHistoryPointDTO,
)
from backend.core.dto.pending import PendingDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.promises import BalanceDTO, PromisesPreviewDTO, PromisesRequest
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.snapshot import DayBalanceDTO, SnapshotDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.strategy import (
    MyStrategyDTO,
    SignalDTO,
    StrategyInfoDTO,
    StrategyLogPageDTO,
    StrategyParamValue,
    StrategyViewDTO,
)
from backend.core.dto.treasury import (
    TreasuryCatalogDTO,
    TreasuryHistoryPointDTO,
    TreasuryPositionDTO,
    TreasurySaleQuoteDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    AssetClass,
    FixedIncomeType,
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
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.indicators import annual_index_rate
from backend.core.life_budget import LifeBudget
from backend.core.life_events import life_event_label
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
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.professions import (
    DRIVER_CURVES,
    HEALTH_EVENT_KEY,
    IncomeDriver,
    LifeLevers,
    RealRaise,
)
from backend.core.rates import period_rate
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
from backend.features.achievements.catalog import Achievement
from backend.features.achievements.evaluator import (
    AchievementEvaluator,
    match_result,
    unlocked_event,
)
from backend.features.backtest.progress import BacktestProgress
from backend.features.credit.overview import (
    build_overview,
    build_prepayment_preview,
)
from backend.features.credit.overview import build_quote as build_loan_quote
from backend.features.economy.growth import (
    MacroCourse,
    history_dollar,
    stocks_return,
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
from backend.features.funds.fund_preview import FundPreviewBuilder
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
from backend.features.government.governance import build_governance, sector_options
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
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    CorporateActionsEventDTO,
    FundsUpdateEventDTO,
    PortfolioUpdateEventDTO,
    SimulationTickUpdateEventDTO,
    SnapshotUpdateEventDTO,
    SpeedUpdateEventDTO,
    StatisticsSnapshotEntryDTO,
    StatisticsSnapshotUpdateEventDTO,
    StocksUpdateEventDTO,
    StockUpdateEventDTO,
)
from backend.features.simulation.life_events import (
    layoff_factor_of,
    layoff_in,
    overdraft_interest,
    salary_skipped,
    unexpected_on,
)
from backend.features.simulation.life_history import (
    budget_changes,
)
from backend.features.simulation.life_history import (
    build_history as build_life_history,
)
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.statistics.cache import ReportCache
from backend.features.statistics.goal import goal_on, goal_reached
from backend.features.strategy.runner import StrategyRunner
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
# A janela da variação do dólar que move a renda do exportador
DOLLAR_WINDOW_DAYS = 365

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
            return method(self, *args, **kwargs)

    return call


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
                self._stocks_return_on,
            )
            if settings.game_type is GameType.FINANCIAL_INDEPENDENCE
            else None
        )
        # A profissão de cada jogador (user_id), lida da partida quando ela joga com profissões
        self._professions: dict[int, Profession] = {}
        self._current_date = resume_from or self.settings.start_date - timedelta(days=1)
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
        self._price_impact = PriceImpact(
            settings.id,
            settings.price_impact_enabled,
            settings.price_impact_k,
            settings.price_impact_decay_days,
        )

        # As estratégias ligadas voltam antes do primeiro tick, que já as roda
        self._strategies = StrategyRunner(
            self._engine, self._price_impact, settings.end_date
        )
        self._strategies.load(
            repository.simulation_player.participants(settings.id), resume_from
        )
        if backtest is not None:
            self._strategies.on_failure = self._backtest_failed

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
                lambda: repository.simulation_player.participants(settings.id),
            )
            if settings.funds_enabled and backtest is None
            else None
        )
        # O caixa da gestora chega, pelo tempo real, ao gestor que a gere
        if self._funds is not None:
            self._engine.use_account_route(self._funds.audience_of)

        # No livro de ofertas, a conta pessoal e as gestoras de um jogador têm o mesmo dono
        self._engine.matching_engine.owner_of = self._account_owner

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
    def get_fixed_asset(self, asset_uuid: str) -> FixedIncomeAssetDTO | None:
        return self._engine.fixed_income_market.get_asset(asset_uuid)

    @synchronized
    def get_portfolio(self, client_id: UUID):
        return self._engine.get_portfolio(client_id)

    @synchronized
    def get_fixed_positions(self, client_id: UUID):
        return self._engine.fixed_broker.get_fixed_positions(client_id)

    @synchronized
    def create_order(self, order: Order) -> None:
        self._ensure_can_operate(order.client_id)
        if (
            order.action is OrderAction.BUY
            and self._funds is not None
            and order.client_id in self._funds.client_ids
            and self._engine.asset_class(order.ticker) is AssetClass.FUND
        ):
            raise ConflictError("A gestora não compra cota de gestora.")
        # A compra por valor ganha a quantidade com o book de agora, no mesmo lock da execução
        if isinstance(order, MarketOrder) and order.budget is not None:
            self._engine.size_budget_order(order)
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
        self._engine.fixed_broker.buy(client_id, asset, value)
        EventManager.flush()

    @synchronized
    def redeem_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, net_amount: Decimal
    ) -> None:
        self._ensure_can_operate(client_id)
        self._engine.fixed_broker.redeem(client_id, asset, net_amount)
        EventManager.flush()

    @synchronized
    def get_strategies(self) -> list[StrategyInfoDTO]:
        return self._strategies.infos(self._current_date)

    @synchronized
    def get_my_strategy(self, user: UserDTO) -> MyStrategyDTO:
        return self._strategies.mine(user, self._current_date)

    @synchronized
    def set_my_strategy(
        self,
        user: UserDTO,
        key: str | None,
        params: dict[str, StrategyParamValue],
    ) -> None:
        if key is not None:
            self._ensure_can_trade(user.client_id)
        self._strategies.set_mode(user, key, params, self._current_date)

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
        return self._strategies.view(user, key, params, self._current_date)

    @synchronized
    def get_strategy_log(
        self, user: UserDTO, kind: LogFilter, offset: int, limit: int
    ) -> StrategyLogPageDTO:
        return self._strategies.log(user, kind, offset, limit)

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
    def get_map_timeline(self, user: UserDTO, year: int | None) -> MapTimelineDTO:
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
        """O client_id que opera no mercado: o do jogador, ou o da gestora que ele gere."""
        if fund_id is None:
            return client_id
        fund = self._ensure_funds().by_id(fund_id)
        if self._client_of_user(fund.terms.manager_user_id) != client_id:
            raise ForbiddenError("Só o gestor opera a conta da gestora.")
        return fund.account.client_id

    @synchronized
    def get_fund_accounts(self, user: UserDTO) -> list[FundAccountDTO]:
        """As contas do jogador: a pessoal e depois cada gestora que ele gere."""
        book = self._ensure_funds()
        accounts = [
            FundAccountDTO(
                fund_id=None,
                name="Conta pessoal",
                ticker=None,
                cash=self._engine.get_cash(user.client_id),
                frozen_until=self._manager_frozen_until(user.id),
            )
        ]
        accounts.extend(
            FundAccountDTO(
                fund_id=fund.terms.id,
                name=fund.terms.name,
                ticker=fund.ticker,
                cash=self._engine.get_cash(fund.account.client_id),
                frozen_until=book.frozen_until(fund),
            )
            for fund in book.funds()
            if fund.terms.manager_user_id == user.id
        )
        return accounts

    @synchronized
    def check_fund_ticker(self, user: UserDTO, ticker: str) -> FundTickerCheckDTO:
        """Confere a sigla de uma gestora sem alterar nada: formato, ativo (as quatro letras), gestora de outro jogador da partida ou livre."""
        book = self._ensure_funds()
        if re.fullmatch(FUND_TICKER_PATTERN, ticker) is None:
            return FundTickerCheckDTO(ticker=ticker, status="format", owner_name=None)
        if repository.fund.letters_taken_by_asset(ticker):
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
    def get_funds(self) -> list[FundSummaryDTO]:
        return self._ensure_funds().summaries()

    @synchronized
    def get_fund(self, user: UserDTO, fund_id: int) -> FundDetailsDTO:
        """A página da gestora como `user` a vê: a carteira viva é só do gestor."""
        book = self._ensure_funds()
        builder = FundDetailsBuilder(
            book,
            self._engine,
            self.settings.id,
            lambda: repository.simulation_player.colors(self.settings.id),
        )
        return builder.build(book.by_id(fund_id), user)

    @synchronized
    def found_fund(self, user: UserDTO, request: FundFoundRequest) -> FundSummaryDTO:
        book = self._ensure_funds()
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

    def _fund_previews(self, manager: UserDTO) -> FundPreviewBuilder:
        return FundPreviewBuilder(self._ensure_funds(), self._engine, manager)

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

    def _notify_funds_update(self) -> None:
        """Avisa a sala de que as páginas das gestoras mudaram: toda mudança de gestora
        (pregão, negócio da cota, oferta, taxas, congelamento) passa por aqui."""
        notify("funds_update", FundsUpdateEventDTO().to_json())

    def _ensure_funds(self) -> FundBook:
        if self._funds is None:
            raise ConflictError("Esta partida não usa a expansão Gestoras.")
        return self._funds

    def _managed_fund(self, user: UserDTO, fund_id: int) -> Fund:
        """A gestora de `fund_id`, que só o gestor dela opera."""
        fund = self._ensure_funds().by_id(fund_id)
        if fund.terms.manager_user_id != user.id:
            raise ForbiddenError("Só o gestor opera esta gestora.")
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
            if fund is not None:
                self._ensure_fund_active(fund)

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
            president,
            None,
            {},
            day,
            reason="Você assumiu a presidência: a carteira fica congelada",
        )

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
        budget = life.for_profession(self._profession_of(user_id))
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
        cash = self._engine.get_cash(client_id)
        if cash < 0:
            detail = format_money(cash)
            if self._life is not None:
                detail += (
                    f" · cheque especial a {_overdraft_rate(today) * 100:.1f}% ao mês"
                )
            items.append(registry.pending(PendingType.NEGATIVE_CASH, detail))
        items += self._strategies.pending(user)
        if self._government is not None:
            items += self._government.pending(user, today)
        return registry.sort_pending(items)

    @synchronized
    def get_credit(self, client_id: UUID) -> CreditOverviewDTO:
        return build_overview(self._engine.credit_book, client_id, self._current_date)

    @synchronized
    def quote_loan(
        self, client_id: UUID, amount: Decimal, term_months: int
    ) -> LoanQuoteDTO:
        return build_loan_quote(
            self._engine.credit_book,
            client_id,
            self._current_date,
            amount,
            term_months,
        )

    @synchronized
    def preview_prepayment(
        self, client_id: UUID, loan_id: UUID, amount: Decimal
    ) -> PrepaymentPreviewDTO:
        return build_prepayment_preview(
            self._engine.credit_book, client_id, loan_id, self._current_date, amount
        )

    @synchronized
    def contract_loan(self, client_id: UUID, amount: Decimal, term_months: int) -> None:
        try:
            self._engine.credit_book.contract(client_id, amount, term_months)
        finally:
            EventManager.flush()

    @synchronized
    def prepay_loan(
        self, client_id: UUID, loan_id: UUID, amount: Decimal, mode: PrepaymentMode
    ) -> None:
        try:
            self._engine.credit_book.prepay(client_id, loan_id, amount, mode)
        finally:
            EventManager.flush()

    @synchronized
    def payoff_loan(self, client_id: UUID, loan_id: UUID) -> None:
        try:
            self._engine.credit_book.payoff(client_id, loan_id)
        finally:
            EventManager.flush()

    @synchronized
    def pay_overdue(self, client_id: UUID, loan_id: UUID) -> None:
        try:
            self._engine.credit_book.pay_overdue(client_id, loan_id)
        finally:
            EventManager.flush()

    @synchronized
    def get_fixed_offers(self) -> list[FixedIncomeOfferDTO]:
        return [
            apply_offer_assistance(
                offer(
                    a,
                    self._current_date,
                    self._tax_policy(),
                    self._engine.dollar_today(),
                ),
                self.settings,
            )
            for a in self.get_fixed_assets()
            if a.investment_type is not FixedIncomeType.TESOURO_DIRETO
        ]

    @synchronized
    def get_fixed_offer(self, asset_uuid: str) -> FixedIncomeOfferDTO | None:
        asset = self.get_fixed_asset(asset_uuid)
        if not asset:
            return None
        return apply_offer_assistance(
            offer(
                asset,
                self._current_date,
                self._tax_policy(),
                self._engine.dollar_today(),
            ),
            self.settings,
        )

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
            EventManager.flush()
        with metrics.measure("engine", ENGINE_NEWS):
            self._publish_newsroom(stocks)

        # A vela das cotas fecha antes do snapshot: o preço de ranking do dia já vale nele
        fund_candles: list[CandleDTO] = []
        if self._funds is not None:
            with metrics.measure("engine", ENGINE_FUNDS):
                fund_candles = self._funds.on_close(self._current_date)

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
            for stock in [*stocks, *fund_candles]:
                ticker = stock.ticker
                notify(
                    f"stock_update:{ticker}",
                    StockUpdateEventDTO(stock=stock).to_json(),
                )
            notify(
                "simulation_update",
                SimulationTickUpdateEventDTO(current_date=self._current_date).to_json(),
            )
            notify("stocks_update", StocksUpdateEventDTO(stocks=stocks).to_json())
            if self._funds is not None:
                self._notify_funds_update()
            for player in UserManager.list_active_players():
                notify(
                    "portfolio_update",
                    PortfolioUpdateEventDTO(
                        portfolio=self.get_portfolio(player.client_id), account=None
                    ).to_json(),
                    to=player.client_id,
                )
                # Cada gestora que o jogador gere vai ao gestor marcada com o id dela
                for fund in self._funds.managed_by(player.id) if self._funds else []:
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

    def _account_owner(self, client_id: UUID) -> int | None:
        """O user_id dono da conta `client_id`: o gestor para a conta de uma gestora, o próprio jogador para a pessoal."""
        if self._funds is not None:
            fund = self._funds.of_client(client_id)
            if fund is not None:
                return fund.terms.manager_user_id
        user = UserManager.get_user(client_id)
        return user.id if user is not None else None

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
            total_networth=balance.total_cash
            + balance.total_equity
            + balance.total_fixed
            - balance.total_debt,
            equity_by_class=balance.equity_by_class,
            created_at=datetime.now(UTC),
        )

    def _backtest_failed(self, user: UserDTO, day: date, message: str) -> None:
        required(self.backtest).fail(user.nickname, day, message)

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
            for user in users:
                budget = budgets[user.client_id]
                loses_income = budget.income_loss() is not None and skipped_for(budget)
                salary = budget.net_salary_on(day, income_lost=loses_income)
                if salary > 0 or not loses_income:
                    self._engine.pay_salary(user.client_id, salary)
                self._engine.pay_expense(user.client_id, budget.expense_on(day))

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
            health = budget.rule.health_multiple if event.key == HEALTH_EVENT_KEY else 1
            amount = event.expense_multiple * budget.expense_on(day) * health
            if is_income:
                self._engine.receive_unexpected(user.client_id, amount, event.key)
            else:
                self._engine.charge_unexpected(user.client_id, amount, event.key)
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

    def _stocks_return_on(self, day: date) -> Decimal:
        """O retorno do Ibovespa da partida em 12 meses; sem série, o valor neutro da curva."""
        value = stocks_return(day)
        return DRIVER_CURVES[IncomeDriver.STOCKS].neutral if value is None else value

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
            "income_loss": rule.loss,
            "health_multiple": rule.health_multiple,
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
        budget = self._life.for_profession(
            self._profession_of(UserManager.get_user_id(client_id))
        )
        changes = budget_changes(budget, self._current_date, _overdraft_rate)
        return build_life_history(
            events,
            self.settings.life_events,
            changes,
            lambda day: self._macro.latest(day).unemployment,
            budget.income_loss(),
            budget.profession if self.settings.uses_professions else None,
        )

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
        quotes = []
        for candle in self.get_stocks():
            history = closes.get(candle.ticker, [])
            segment = classification.get(candle.ticker)
            quotes.append(
                MarketQuoteDTO(
                    **candle.model_dump(),
                    sparkline=[*history[:-1], candle.close]
                    if history
                    else [candle.close],
                    sector=segment.sector if segment else None,
                    segment=segment.segment if segment else None,
                )
            )
        return quotes

    @synchronized
    def get_stock_details(self, ticker: str) -> StockDetailsDTO | None:
        details = repository.stock.get_stock_details(ticker, self._current_date)
        if details is None:
            return None
        return self._price_impact.apply(details).model_copy(
            update={
                "history": self._price_impact.apply_history(ticker, details.history)
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
    ) -> OrderPreviewDTO:
        return self._engine.preview_order(
            client_id, ticker, action, quantity, limit_price, amount
        )

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
        if cash > 0:
            self._engine.add_cash(user.client_id, cash)
        EventManager.flush()
        self._snapshot_users([user])
        self.statistics.clear()
