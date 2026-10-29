from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar
from uuid import UUID

import pandas as pd

from backend import config
from backend.core import repository
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
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.economy import EconomyPanelDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO, FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import (
    FixedIncomeQuoteDTO,
    FixedIncomeRedemptionQuoteDTO,
    NextTaxDropDTO,
)
from backend.core.dto.goal import GoalProgressDTO, GoalRunnerDTO
from backend.core.dto.government import (
    ElectionPanelDTO,
    FoundPartyRequest,
    GovernmentPanelDTO,
    MeasurePreviewDTO,
    PromisesPanelDTO,
    ProposeMeasureRequest,
)
from backend.core.dto.life import LifeEventDTO, LifeStatusDTO
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
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.strategy import (
    MyStrategyDTO,
    SignalDTO,
    StrategyInfoDTO,
    StrategyLogPageDTO,
    StrategyParamValue,
    StrategyViewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    GameType,
    IndicatorSeries,
    OrderAction,
    PauseReason,
    PendingType,
    PlayerGrouping,
    PrepaymentMode,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.indicators import annual_index_rate
from backend.core.life_budget import LifeBudget
from backend.core.repository.strategy import LogFilter
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import (
    format_money,
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
from backend.features.candle_challenge import service as candle_challenge
from backend.features.credit.overview import (
    build_overview,
    build_prepayment_preview,
)
from backend.features.credit.overview import build_quote as build_loan_quote
from backend.features.economy.panel import build_economy_panel
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
from backend.features.fixed_income.liquidity import overdraft_cover, total_redeemable
from backend.features.government.campaign_panel import (
    build_campaign,
    build_history,
    build_roll,
)
from backend.features.government.governance import build_governance, sector_options
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import build_panel
from backend.features.government.promise_panel import (
    build_balances,
    build_preview,
    build_promises_panel,
)
from backend.features.notifications import news, registry
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
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
    layoff_in,
    overdraft_interest,
    salary_skipped,
    unexpected_on,
)
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.simulation.simulation_loop import simulation_controller
from backend.features.statistics.cache import ReportCache
from backend.features.statistics.goal import goal_on, goal_reached
from backend.features.statistics.report import build_overview_report
from backend.features.strategy.runner import StrategyRunner
from backend.features.summaries.service import SummaryDelivery
from backend.features.tax_policy import TaxPolicy
from backend.features.technical_analysis.summary import price_frame
from backend.features.variable_income.entities.order import MarketOrder, Order
from backend.features.variable_income.price_impact import PriceImpact

# Pregões no mini gráfico da lista de mercado
SPARKLINE_DAYS = 30

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


def _overdraft_rate() -> Decimal:
    return Decimal(str(config.toml.simulation.overdraft_monthly_rate))


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
            LifeBudget.of(settings)
            if settings.game_type is GameType.FINANCIAL_INDEPENDENCE
            else None
        )
        self._current_date = resume_from or self.settings.start_date - timedelta(days=1)
        self._engine = SimulationEngine(
            self._current_date,
            settings.starting_cash,
            settings.id,
            settings.end_date,
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

        # Expansão Governo & Política: o estado político volta dos eventos gravados
        self._government = (
            GovernmentBook(
                settings,
                self._engine,
                self._take_office,
                lambda day, headline: news.publish(settings.id, day, headline),
                random_seed,
            )
            if settings.government_enabled and backtest is None
            else None
        )

        # As abas das Estatísticas desta partida, montadas uma vez por mês
        self.statistics = ReportCache()

        # O resumo do mês usa o ranking da aba Geral do mês que começa
        self._summaries = SummaryDelivery(
            settings.id,
            settings.start_date,
            settings.starting_cash,
            lambda: self.statistics.report(
                "overview", lambda: build_overview_report([settings.id])
            ),
            lambda: {ticker: s.name for ticker, s in self._engine.stocks.items()},
        )

        # Fora da Clássica: onde cada um está na meta e se alguém já chegou
        self._goal_progress: GoalProgressDTO | None = None
        self._goal_reached = False

        # Os snapshots do último pregão são a base da avaliação final das conquistas
        self._achievements = AchievementEvaluator(
            settings, self._engine.assess_income_tax
        )
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
        # A compra por valor ganha a quantidade com o book de agora, no mesmo lock da execução
        if isinstance(order, MarketOrder) and order.budget is not None:
            self._engine.size_budget_order(order)
        self._engine.check_quantity(order.ticker, order.size)
        try:
            self._engine.matching_engine.submit(order)
        finally:
            # Mesmo uma execução parcial precisa aparecer sem esperar outro tick.
            EventManager.flush()

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
        )

    @synchronized
    def set_party_flags(self, user: UserDTO, flags: list[VoterValue]) -> None:
        self._ensure_government().set_flags(user, self._current_date, flags)

    @synchronized
    def join_party(self, user: UserDTO, party_id: int, contribution: Decimal) -> None:
        self._ensure_government().join_party(
            user, self._current_date, party_id, contribution
        )

    @synchronized
    def leave_party(self, user: UserDTO) -> None:
        self._ensure_government().leave_party(user, self._current_date)

    @synchronized
    def set_contribution(self, user: UserDTO, contribution: Decimal) -> None:
        self._ensure_government().set_contribution(
            user, self._current_date, contribution
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
    def set_ticket(self, founder: UserDTO, candidate: str, vice: str | None) -> None:
        self._ensure_government().set_ticket(
            founder,
            self._current_date,
            candidate,
            vice,
            repository.simulation_player.participants(self.settings.id),
        )

    @synchronized
    def answer_vice(self, user: UserDTO, accept: bool) -> None:
        self._ensure_government().answer_vice(user, self._current_date, accept)

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
        )

    @synchronized
    def withdraw_measure(self, user: UserDTO, measure_id: int) -> None:
        self._ensure_government().withdraw(user, self._current_date, measure_id)

    @synchronized
    def repropose_measure(self, user: UserDTO, measure_id: int) -> None:
        self._ensure_government().repropose(user, self._current_date, measure_id)

    def _tax_policy(self) -> TaxPolicy:
        return self._engine.tax_policy_on(self._current_date)

    def _ensure_can_trade(self, client_id: UUID) -> None:
        """A carteira do presidente fica congelada durante o mandato."""
        if self._government is not None:
            self._government.ensure_can_trade(client_id)

    def _ensure_can_operate(self, client_id: UUID) -> None:
        self._ensure_can_trade(client_id)
        self._strategies.ensure_manual(client_id)

    def _take_office(self, president: UserDTO, day: date) -> None:
        """Na posse as ordens abertas somem e o automático desliga: a carteira congela."""
        self._engine.matching_engine.cancel_all(president.client_id)
        self._strategies.set_mode(
            president,
            None,
            {},
            day,
            reason="Você assumiu a presidência: a carteira fica congelada",
        )

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
                detail += f" · cheque especial a {_overdraft_rate() * 100:.0f}% ao mês"
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
                offer(a, self._current_date, self._tax_policy()), self.settings
            )
            for a in self.get_fixed_assets()
        ]

    @synchronized
    def get_fixed_offer(self, asset_uuid: str) -> FixedIncomeOfferDTO | None:
        asset = self.get_fixed_asset(asset_uuid)
        if not asset:
            return None
        return apply_offer_assistance(
            offer(asset, self._current_date, self._tax_policy()), self.settings
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
        maximum = position.breakdown(today, None, policy).net
        redemption = (
            position.breakdown(today, amount, policy) if 0 < amount <= maximum else None
        )
        cash = self.get_cash(client_id)
        first = position.first_applied_date
        days_held = (today - first).days
        drop = next_tax_drop(asset.investment_type, first, today, policy)
        return FixedIncomeRedemptionQuoteDTO(
            amount=amount,
            max_amount=maximum,
            position_value=position.current_value,
            total_applied=position.total_applied,
            first_applied_date=first,
            days_held=days_held,
            gross_amount=redemption and redemption.gross,
            yield_amount=redemption and redemption.yield_amount,
            iof_rate=iof_rate(days_held),
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
    def get_patrimonial_history(
        self, client_id: UUID
    ) -> list[PortfolioHistoryPointDTO]:
        return [
            self._history_point(point)
            for point in repository.portfolio.get_patrimonial_history(
                UserManager.get_user_id(client_id)
            )
        ]

    def _history_point(self, point: PatrimonialHistoryDTO) -> PortfolioHistoryPointDTO:
        return PortfolioHistoryPointDTO(
            **point.model_dump(),
            total_provided=self.settings.starting_cash + point.total_contribution,
        )

    @synchronized
    def next_tick(self):
        # O dia em que alguém chegou à meta foi processado inteiro; a partida acaba no seguinte
        if self._goal_reached:
            logger.info("Meta alcançada")
            raise StopIteration()

        # Avança para o próximo dia útil; passou do fim, a simulação terminou
        if self._current_date <= self.settings.end_date:
            self._current_date = next_business_day(self._current_date)
        if self._current_date > self.settings.end_date:
            logger.info("Fim da simulação")
            raise StopIteration()

        # O impacto é lido dos eventos no banco: o flush leva antes as ordens que
        # chegaram por HTTP depois do último tick, ainda datadas do dia anterior
        EventManager.flush()
        self._price_impact.refresh(self._current_date)

        # O matching pode executar ordens antigas durante a atualização do book.
        # Elas já pertencem ao dia novo, assim como os juros e as consultas.
        self._engine.current_date = self._current_date
        # Obtém os dados do dia atual e atualiza o buffer
        stocks = self.get_stocks()
        self._engine.update_market_data(stocks)

        # Só quem estava na sala ao iniciar participa: é quem tem depósito e cor
        users = repository.simulation_player.participants(self.settings.id)

        # Juros da renda fixa e, em seguida, as estratégias ligadas operam o dia
        self._engine.next(self._current_date)
        self._strategies.run(users, self._current_date)
        month_changed = self._has_month_changed()

        # O aporte (ou o salário, a despesa e o imprevisto) e o DARF que vence hoje
        # entram nos eventos antes do flush, para o snapshot do dia já contá-los; o
        # juro do cheque especial vem por último, sobre o caixa que sobrou do dia
        if self._life is not None:
            self._live(self._life, users, month_changed)
        elif month_changed:
            self._apply_monthly_contributions(users)
        self._settle_credit(users, month_changed)
        if self._government is not None and (
            reason := self._government.on_tick(users, self._current_date, month_changed)
        ):
            self._pause_for_result(reason)
        self._collect_income_tax(users)
        if self._life is not None:
            self._charge_overdraft(users)
        EventManager.flush()

        if self.backtest is not None:
            self._record_backtest_day(users, month_changed)
            return

        # As respostas do desafio da vela já conferem antes do snapshot e das conquistas do dia
        self._settle_candle_challenges()
        snapshots = self._create_daily_snapshots(users, month_changed)

        # Emite notificações
        logger.debug(
            "Dia simulado: %s (%s ativos, %s jogadores)",
            self.get_current_date_formatted(),
            len(stocks),
            len(users),
        )
        for stock in stocks:
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
        for player in UserManager.list_active_players():
            notify(
                "portfolio_update",
                PortfolioUpdateEventDTO(
                    portfolio=self.get_portfolio(player.client_id)
                ).to_json(),
                to=player.client_id,
            )
        if self.settings.game_type.has_goal:
            self._track_goal(snapshots)

        self._last_snapshots = {e.snapshot.user_id: e.snapshot for e in snapshots}
        if month_changed:
            self._deliver_summaries(users)
        self._unlock_achievements(
            users,
            lambda: self._achievements.on_tick(
                self._human_snapshots(users), month_changed
            ),
        )

    def _settle_candle_challenges(self) -> None:
        """
        Confere as respostas que chegaram ao 5º pregão depois do padrão. O desafio é
        um extra: um erro ao conferir não interrompe a partida.
        """
        if not self.settings.show_chart_hints:
            return
        try:
            candle_challenge.settle(self.settings.id, self._price_frame)
        except Exception:
            logger.exception("Erro ao conferir o desafio da vela")

    def _price_frame(self, ticker: str) -> pd.DataFrame | None:
        """O histórico do ativo até hoje, com o impacto de preço, como o gráfico o vê."""
        details = self.get_stock_details(ticker)
        return price_frame(details.history) if details else None

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
        equity, fixed, cash, debt = self._engine.balance_sheet(user.client_id)
        return SnapshotDTO(
            user_id=user.id,
            snapshot_date=self._current_date,
            total_equity=equity,
            total_fixed=fixed,
            total_cash=cash,
            total_contribution=self._contributed,
            total_debt=debt,
            total_networth=cash + equity + fixed - debt,
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
        O resumo do mês sai depois dos snapshots do dia. O resumo é um extra:
        um erro ao montá-lo não interrompe a partida.
        """
        try:
            self._summaries.on_month_turn(users, self._current_date)
        except Exception:
            logger.exception("Erro ao montar o resumo do mês")

    def get_goal_progress(self) -> GoalProgressDTO | None:
        return self._goal_progress

    def _track_goal(self, snapshots: list[StatisticsSnapshotEntryDTO]) -> None:
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
                    color=colors[entry.snapshot.user_id],
                    team=teams.get(entry.snapshot.user_id),
                    networth=entry.snapshot.total_networth,
                )
                for entry in snapshots
            ],
        )
        notify("goal_progress_update", self._goal_progress.to_json())
        self._goal_reached = goal_reached(
            {e.snapshot.user_id: e.snapshot.total_networth for e in snapshots},
            teams,
            goal,
            self.settings.player_grouping is PlayerGrouping.TEAMS,
        )

    def _live(self, life: LifeBudget, users: list[UserDTO], month_changed: bool):
        """
        No 1º pregão do mês o salário entra (menos depois de uma demissão) e a despesa
        sai; todo pregão pode sortear um imprevisto, o mesmo para todos.
        """
        day = self._current_date
        per_year = self.settings.unexpected_per_year
        if month_changed:
            skipped = salary_skipped(
                self._random_seed, day, per_year, self.settings.start_date
            )
            for user in users:
                if not skipped:
                    self._engine.pay_salary(user.client_id, life.salary_on(day))
                self._engine.pay_expense(user.client_id, life.expense_on(day))

        event = unexpected_on(self._random_seed, day, per_year)
        if event is None:
            return
        amount = event.expense_multiple * life.expense_on(day)
        for user in users:
            self._engine.charge_unexpected(user.client_id, amount, event.key)
        notify(
            "life_event",
            LifeEventDTO(
                key=event.key,
                label=event.label,
                effect=event.effect,
                amount=amount,
                event_date=day,
            ).to_json(),
        )

    def _charge_overdraft(self, users: list[UserDTO]):
        rate = _overdraft_rate()
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
        expense = self._life.expense_on(day)
        cash = self.get_cash(client_id)
        rate = _overdraft_rate()
        # A reserva soma o caixa e a liquidez diária líquida, e nunca fica negativa
        positions = list(self.get_fixed_positions(client_id).values())
        policy = self._tax_policy()
        daily_liquidity = total_redeemable(positions, day, policy)
        reserve = max(cash + daily_liquidity, Decimal(0))
        reserve_cash = max(cash, Decimal(0))
        return LifeStatusDTO(
            monthly_salary=self._life.salary_on(day),
            monthly_expense=expense,
            salary_skipped_by=layoff_in(
                seed, day.replace(day=1) - timedelta(days=1), per_year, start
            ),
            next_salary_skipped_by=layoff_in(seed, day, per_year, start, until=day),
            goal=self._life.goal_on(day),
            inflation_adjusted=self.settings.inflation_adjusted,
            withdrawal_rate=self.settings.withdrawal_rate,
            unexpected_per_year=per_year,
            overdraft_monthly_rate=rate,
            overdraft_daily_interest=overdraft_interest(cash, rate),
            reserve_months=reserve / expense,
            reserve_cash=reserve_cash,
            reserve_daily_liquidity=reserve - reserve_cash,
            overdraft_cover=overdraft_cover(cash, positions, day, policy),
        )

    @synchronized
    def get_current_date(self) -> date:
        return self._current_date

    @synchronized
    def next_statistics_update(self) -> date | None:
        """Dia em que as estatísticas fecham o mês de novo; nulo quando a partida acaba antes."""
        turn = next_month_turn(self._current_date)
        return turn if turn <= self.settings.end_date else None

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
    def get_economic_indicators(self) -> EconomicIndicatorsDTO:
        return EconomicIndicatorsDTO(
            ipca=annual_index_rate(IndicatorSeries.IPCA, self._current_date),
            selic=annual_index_rate(IndicatorSeries.SELIC, self._current_date),
            cdi=annual_index_rate(IndicatorSeries.CDI, self._current_date),
        )

    @synchronized
    def get_economy_panel(self) -> EconomyPanelDTO:
        return build_economy_panel(self.settings.start_date, self._current_date)

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
            months = self._engine.assess_income_tax(user.id)
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
        snapshots_payload = [self._snapshot_user(user) for user in users]

        if month_changed:
            self.statistics.clear()
            notify(
                event="statistics_snapshot_update",
                payload=StatisticsSnapshotUpdateEventDTO(
                    snapshots=snapshots_payload
                ).to_json(),
            )
        return snapshots_payload

    def _snapshot_user(self, user: UserDTO) -> StatisticsSnapshotEntryDTO:
        """Grava o snapshot do dia de `user`, avisa a carteira dele e devolve a linha das Estatísticas."""
        portfolio = self.get_portfolio(user.client_id)
        snapshot = repository.snapshot.create_snapshot(
            user_id=user.id,
            snapshot_date=self._current_date,
            total_equity=portfolio.variable_income_value,
            total_fixed=portfolio.fixed_income_value,
            total_debt=portfolio.debt,
        )

        notify(
            event="snapshot_update",
            payload=SnapshotUpdateEventDTO(
                snapshot=self._history_point(
                    PatrimonialHistoryDTO.model_validate(
                        snapshot.model_dump(
                            include=set(PatrimonialHistoryDTO.model_fields)
                        )
                    )
                )
            ).to_json(),
            to=user.client_id,
        )

        return StatisticsSnapshotEntryDTO(
            player_nickname=user.nickname, snapshot=snapshot
        )

    @synchronized
    def add_player(self, user: UserDTO) -> None:
        """
        Quem entra com a partida em andamento recebe o depósito inicial no dia corrente
        e o snapshot desse dia; o aporte mensal e os snapshots seguintes já o incluem
        porque `participants` lê a linha dele em `simulation_players`.
        """
        self._engine.add_cash(user.client_id, self.settings.starting_cash)
        EventManager.flush()
        self._snapshot_user(user)
        self.statistics.clear()
