from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar
from uuid import UUID

from backend import config
from backend.core import repository
from backend.core.dto.candle import CandleDTO, MarketQuoteDTO
from backend.core.dto.credit import (
    CreditOverviewDTO,
    LoanQuoteDTO,
    PrepaymentPreviewDTO,
)
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO, FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import FixedIncomeQuoteDTO
from backend.core.dto.goal import GoalProgressDTO, GoalRunnerDTO
from backend.core.dto.life import LifeEventDTO, LifeStatusDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.order_preview import OrderPreviewDTO
from backend.core.dto.patrimonial_history import (
    PatrimonialHistoryDTO,
    PortfolioHistoryPointDTO,
)
from backend.core.dto.position import PositionDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.snapshot import SnapshotDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.strategy import (
    MyStrategyDTO,
    SignalDTO,
    StrategyInfoDTO,
    StrategyLogPageDTO,
    StrategyParamValue,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    GameType,
    IndicatorSeries,
    OrderAction,
    PlayerGrouping,
    PrepaymentMode,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import annual_index_rate
from backend.core.life_budget import LifeBudget
from backend.core.repository.strategy import LogFilter
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.features.achievements.catalog import Achievement
from backend.features.achievements.evaluator import (
    AchievementEvaluator,
    match_result,
    unlocked_event,
)
from backend.features.credit.overview import (
    build_overview,
    build_prepayment_preview,
)
from backend.features.credit.overview import build_quote as build_loan_quote
from backend.features.fixed_income.accrual import income_tax_brackets, offer, project
from backend.features.fixed_income.assistance import (
    apply_offer_assistance,
    build_quote,
)
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    PortfolioUpdateEventDTO,
    SimulationTickUpdateEventDTO,
    SnapshotUpdateEventDTO,
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
from backend.features.statistics.goal import goal_on, goal_reached
from backend.features.strategy.runner import StrategyRunner
from backend.features.variable_income.entities.order import Order
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
    ):
        """
        `resume_from` é o último dia já processado de uma simulação retomada; o
        primeiro tick é o dia útil seguinte. Sem ele, o primeiro tick é o `start_date`.
        `random_seed` é a semente gravada na partida, de onde saem os imprevistos.
        """
        self._speed = 0
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

        # Fora da Clássica: onde cada um está na meta e se alguém já chegou
        self._goal_progress: GoalProgressDTO | None = None
        self._goal_reached = False

        # Os snapshots do último pregão são a base da avaliação final das conquistas
        self._achievements = AchievementEvaluator(settings)
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
        self._strategies.ensure_manual(order.client_id)
        try:
            self._engine.matching_engine.submit(order)
        finally:
            # Mesmo uma execução parcial precisa aparecer sem esperar outro tick.
            EventManager.flush()

    @synchronized
    def cancel_order(self, *, order_id: str, client_id: UUID) -> bool:
        self._strategies.ensure_manual(client_id)
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
        self._strategies.ensure_manual(client_id)
        self._engine.fixed_broker.buy(client_id, asset, value)
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
    def get_strategy_log(
        self, user: UserDTO, kind: LogFilter, offset: int, limit: int
    ) -> StrategyLogPageDTO:
        return self._strategies.log(user, kind, offset, limit)

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
            apply_offer_assistance(offer(a, self._current_date), self.settings)
            for a in self.get_fixed_assets()
        ]

    @synchronized
    def get_fixed_offer(self, asset_uuid: str) -> FixedIncomeOfferDTO | None:
        asset = self.get_fixed_asset(asset_uuid)
        if not asset:
            return None
        return apply_offer_assistance(offer(asset, self._current_date), self.settings)

    @synchronized
    def quote_fixed_income(
        self, client_id: UUID, asset: FixedIncomeAssetDTO, amount: Decimal
    ) -> FixedIncomeQuoteDTO:
        if self._current_date >= asset.maturity_date:
            raise ConflictError("Esse título já venceu. Escolha uma oferta atual.")
        cash = self.get_cash(client_id)
        return build_quote(
            project(asset, amount, self._current_date),
            self.settings,
            cash_before=cash,
            cash_after=cash - amount,
            max_amount=cash,
            income_tax_brackets=income_tax_brackets(),
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
        self._collect_income_tax(users)
        if self._life is not None:
            self._charge_overdraft(users)
        EventManager.flush()

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
        if self.settings.game_type is not GameType.CLASSIC:
            self._track_goal(snapshots)

        self._last_snapshots = {e.snapshot.user_id: e.snapshot for e in snapshots}
        self._unlock_achievements(
            users,
            lambda: self._achievements.on_tick(self._last_snapshots, month_changed),
        )

    def end_match(self) -> None:
        """
        Conquistas que dependem do resultado: roda com a partida ainda ativa, depois
        do último flush.
        """
        users = repository.simulation_player.participants(self.settings.id)
        self._unlock_achievements(
            users,
            lambda: self._achievements.on_match_end(
                self._last_snapshots,
                match_result(self.settings.id, users, self._goal_reached),
            ),
        )

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

    def get_goal_progress(self) -> GoalProgressDTO | None:
        return self._goal_progress

    def _track_goal(self, snapshots: list[StatisticsSnapshotEntryDTO]) -> None:
        """Avisa onde cada um está na meta e marca o fim da partida quando alguém chega."""
        colors = repository.simulation_player.colors(self.settings.id)
        teams = repository.simulation_player.teams(self.settings.id)
        goal = goal_on(self.settings, self._current_date)
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
            reserve_months=max(cash, Decimal(0)) / expense,
        )

    @synchronized
    def get_current_date(self) -> date:
        return self._current_date

    def get_current_date_formatted(self) -> str:
        return self._current_date.strftime("%d/%m/%Y")

    @synchronized
    def set_speed(self, speed: int):
        logger.info("Velocidade da simulação alterada para %sx", speed)
        self._speed = speed

    def get_speed(self) -> int:
        return self._speed

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
                size=0,
                reserved=0,
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
    def preview_order(
        self,
        client_id: UUID,
        ticker: str,
        action: OrderAction,
        quantity: int,
        limit_price: float | None,
    ) -> OrderPreviewDTO:
        return self._engine.preview_order(
            client_id, ticker, action, quantity, limit_price
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
        inteiro de novo, então sai só na virada do mês; `snapshot_update` é um merge
        por data no cache da Carteira e sai todo dia.
        """
        snapshots_payload = [self._snapshot_user(user) for user in users]

        if month_changed:
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
