from __future__ import annotations

import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException

from backend.core import repository
from backend.core.dto.events.strategy import StrategyEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.dto.pending import PendingDTO
from backend.core.dto.strategy import (
    AllocationViewDTO,
    MyStrategyDTO,
    RankingViewDTO,
    SignalDTO,
    StrategyActiveDTO,
    StrategyErrorDTO,
    StrategyInfoDTO,
    StrategyLogPageDTO,
    StrategyOrderLineDTO,
    StrategyParamValue,
    StrategyViewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    IndicatorSeries,
    OrderAction,
    OrderStatus,
    PendingType,
    StrategyAction,
    StrategyLogKind,
    StrategyOrderStatus,
    StrategyView,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.fund_reference import FundReference, price_ceiling
from backend.core.indicators import annual_index_rate
from backend.core.repository.strategy import LogFilter
from backend.core.runtime.event_manager import EventManager
from backend.core.utils import required
from backend.features.fixed_income.accrual import offer
from backend.features.fixed_income.liquidity import redeemable_today
from backend.features.market_maker.account import bot_room
from backend.features.notifications import registry
from backend.features.realtime import notify
from backend.features.realtime.schemas import (
    StrategyOrdersEventDTO,
    StrategyUpdateEventDTO,
)
from backend.features.strategy import catalog
from backend.features.strategy.base_strategy import CHART_DAYS, BaseStrategy
from backend.features.strategy.context import (
    FixedHolding,
    Holding,
    Indicators,
    OpenOrder,
    Quote,
    StrategyContext,
)
from backend.features.strategy.fund_quotas import FundQuotas
from backend.features.strategy.intents import Intent
from backend.features.strategy.panel import build_panel
from backend.features.strategy.price_history import PriceHistory
from backend.features.strategy.registry import (
    STRATEGIES,
    ensure_available,
    get_strategy,
)
from backend.features.strategy.state import ModeState, derive_state
from backend.features.variable_income.broker import to_money
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    Order,
)
from backend.features.variable_income.price_impact import PriceImpact

if TYPE_CHECKING:
    from backend.features.simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)

LOG_PAGE_LIMIT = 100


@dataclass(frozen=True)
class StrategyAccount:
    """A conta que a estratégia opera: a pessoal do jogador ou a carteira de uma gestora."""

    # O jogador dono da conta; na gestora, quem ligou a estratégia
    user_id: int
    client_id: UUID
    # A gestora dona da conta; ausente, a conta é a pessoal do jogador
    fund_id: int | None = None
    # O apelido de quem age, que o registro da gestora cita no lugar de "Você"
    nickname: str = ""

    @classmethod
    def of_user(cls, user: UserDTO) -> StrategyAccount:
        return cls(user.id, user.client_id, nickname=user.nickname)

    @property
    def subject(self) -> str:
        """Quem liga, troca e desliga, como o registro conta: "Você" na conta pessoal."""
        return "Você" if self.fund_id is None else self.nickname

    @property
    def seed(self) -> int:
        """A semente do sorteio da estratégia; cada conta sorteia por si."""
        return self.user_id if self.fund_id is None else -self.fund_id


@dataclass(frozen=True)
class ActiveStrategy:
    cls: type[BaseStrategy]
    params: dict[str, StrategyParamValue]
    since: date
    account: StrategyAccount


class StrategyRunner:
    """
    Estratégias ligadas dos jogadores e das gestoras e a fase do dia em que elas operam.

    Responsável por:
    - Guardar a estratégia ativa de cada conta, pessoal ou de gestora (ausente é o modo manual)
    - Rodar cada estratégia a cada dia, as pessoais na ordem dos jogadores e depois as das gestoras, e executar as intenções
    - Registrar ordens e mudanças de modo no registro da estratégia
    - Devolver ao manual a conta cuja estratégia deu erro
    """

    def __init__(
        self,
        engine: SimulationEngine,
        price_impact: PriceImpact,
        end_date: date,
        funds_enabled: bool,
        government_enabled: bool,
    ) -> None:
        self._engine = engine
        # As expansões Gestoras e Governo da partida: só nelas valem as estratégias que as exigem
        self._funds_enabled = funds_enabled
        self._government_enabled = government_enabled
        self._history = PriceHistory(engine.simulation_id, end_date, price_impact)
        self._active: dict[UUID, ActiveStrategy] = {}
        # Chamado com o apelido do jogador, o dia e a mensagem quando a estratégia pessoal dele dá erro
        self.on_failure: Callable[[str, date, str], None] | None = None
        engine.matching_engine.on_order_closed = self._on_order_closed

    # =========================
    # Estado
    # =========================

    def load(self, users: list[UserDTO], resumed_on: date | None) -> None:
        """Retoma a estratégia de cada jogador a partir do registro gravado."""
        rows = repository.strategy.mode_rows(self._engine.simulation_id)
        for user in users:
            self._resume(
                StrategyAccount.of_user(user),
                derive_state([r for r in rows if r.user_id == user.id]),
                resumed_on,
            )

    def load_funds(self, clients: dict[int, UUID], resumed_on: date | None) -> None:
        """Retoma a estratégia de cada gestora (conta no motor por id da gestora) a partir do registro gravado."""
        rows = repository.strategy.fund_mode_rows(self._engine.simulation_id)
        for fund_id, client_id in clients.items():
            fund_rows = [r for r in rows if r.fund_id == fund_id]
            if fund_rows:
                account = StrategyAccount(fund_rows[-1].user_id, client_id, fund_id)
                self._resume(account, derive_state(fund_rows), resumed_on)

    def _resume(
        self, account: StrategyAccount, state: ModeState, resumed_on: date | None
    ) -> None:
        if state.key not in STRATEGIES or state.since is None:
            return
        self._active[account.client_id] = ActiveStrategy(
            STRATEGIES[state.key], state.params or {}, state.since, account
        )
        if resumed_on is not None:
            self._push_mode(
                account,
                StrategyLogKind.RESUMED,
                state.key,
                state.params,
                resumed_on,
                reason=f"A partida foi retomada com {STRATEGIES[state.key].name} ligada",
            )

    def is_active(self, client_id: UUID) -> bool:
        """Se a conta tem uma estratégia ligada."""
        return client_id in self._active

    def ensure_manual(self, client_id: UUID) -> None:
        """A boleta do jogador só vale no modo manual."""
        if client_id in self._active:
            raise ConflictError(
                "O automático está ligado. Volte ao manual para operar à mão."
            )

    # =========================
    # Consulta
    # =========================

    def infos(self, today: date, *, for_fund: bool = False) -> list[StrategyInfoDTO]:
        return catalog.infos(
            today,
            self._engine.simulation_id,
            self._engine.stocks,
            funds_enabled=self._funds_enabled,
            government_enabled=self._government_enabled,
            for_fund=for_fund,
        )

    def _state(self, account: StrategyAccount) -> ModeState:
        return derive_state(
            repository.strategy.mode_rows(
                self._engine.simulation_id,
                None if account.fund_id is not None else account.user_id,
                account.fund_id,
            )
        )

    def pending(self, user: UserDTO) -> list[PendingDTO]:
        """O erro que devolveu o jogador ao manual, até ele ligar uma estratégia de novo."""
        state = self._state(StrategyAccount.of_user(user))
        if state.error is None:
            return []
        return [
            registry.pending(
                PendingType.STRATEGY_ERROR, state.error.reason or "Sem detalhes do erro"
            )
        ]

    def mine(self, account: StrategyAccount, today: date) -> MyStrategyDTO:
        state = self._state(account)
        active = (
            StrategyActiveDTO(
                key=state.key, params=state.params or {}, since=state.since
            )
            if state.key and state.since
            else None
        )
        error = (
            StrategyErrorDTO(
                strategy_key=state.error.strategy_key,
                error_date=state.error.event_date,
                message=state.error.reason or "",
                traceback=state.error.detail,
                seen=state.error_seen,
            )
            if state.error
            else None
        )
        return MyStrategyDTO(
            active=active,
            error=error,
            resumed=state.resumed,
            open_orders=len(
                self._engine.matching_engine.order_book.orders_of(account.client_id)
            ),
            panel=build_panel(
                self._engine.simulation_id,
                account.user_id,
                active.since,
                account.fund_id,
            )
            if active
            else None,
        )

    def log(
        self, account: StrategyAccount, kind: LogFilter, offset: int, limit: int
    ) -> StrategyLogPageDTO:
        rows, total = repository.strategy.log_page(
            self._engine.simulation_id,
            account.user_id,
            kind,
            offset,
            min(limit, LOG_PAGE_LIMIT),
            account.fund_id,
        )
        return StrategyLogPageDTO(
            items=[
                row.model_copy(
                    update={
                        "strategy_name": STRATEGIES[row.strategy_key].name
                        if row.strategy_key in STRATEGIES
                        else None
                    }
                )
                for row in rows
            ],
            total=total,
        )

    def signal(
        self,
        key: str,
        params: dict[str, StrategyParamValue],
        ticker: str,
        today: date,
    ) -> SignalDTO:
        """O que a estratégia olha em `ticker`, ou os erros dos parâmetros."""
        cls = get_strategy(key)
        merged = self._with_defaults(cls, params, today)
        errors = cls.validate(merged, set(self._engine.stocks))
        needed = cls.needed_days(merged)
        if errors or ticker not in self._engine.stocks:
            return SignalDTO(
                errors=errors,
                lines=[],
                levels=[],
                markers=[],
                available_days=0,
                needed_days=needed,
            )

        frame = self._history.window(ticker, today, needed + CHART_DAYS)
        signal = cls().signal(frame, merged)
        return SignalDTO(
            errors={},
            lines=signal.lines if signal else [],
            levels=signal.levels if signal else [],
            markers=signal.markers if signal else [],
            available_days=len(frame),
            needed_days=needed,
        )

    def view(
        self,
        account: StrategyAccount,
        key: str,
        params: dict[str, StrategyParamValue],
        today: date,
    ) -> StrategyViewDTO:
        """O ranking ou a alocação da estratégia sobre a carteira da conta hoje, sem executar nada."""
        cls = get_strategy(key)
        merged = self._with_defaults(cls, params, today)
        errors = cls.validate(merged, set(self._engine.stocks))
        if errors or cls.view_kind not in (
            StrategyView.RANKING,
            StrategyView.ALLOCATION,
        ):
            return StrategyViewDTO(errors=errors, ranking=None, allocation=None)

        ctx = self._context(account, self._market(today, account), today)
        result = cls().view(ctx, merged)
        return StrategyViewDTO(
            errors={},
            ranking=result if isinstance(result, RankingViewDTO) else None,
            allocation=result if isinstance(result, AllocationViewDTO) else None,
        )

    # =========================
    # Mudança de modo
    # =========================

    def set_mode(
        self,
        account: StrategyAccount,
        key: str | None,
        params: dict[str, StrategyParamValue],
        today: date,
        reason: str | None = None,
    ) -> None:
        """
        Liga, troca, ajusta ou desliga a estratégia da conta a partir do próximo dia.
        `reason` conta no registro por que a conta voltou ao manual.
        """
        previous = self._active.get(account.client_id)
        if key is None:
            if previous is None:
                return
            canceled = self._engine.matching_engine.cancel_all(account.client_id)
            del self._active[account.client_id]
            self._push_mode(
                account,
                StrategyLogKind.DISABLED,
                None,
                None,
                today,
                reason=reason
                or f"{account.subject} voltou ao manual{_canceled_phrase(canceled, previous.cls.name, account)}",
                quantity=Decimal(canceled),
            )
            self._finish_mode_change(account, active=False)
            return

        cls = get_strategy(key)
        if account.fund_id is not None and not cls.fund_account:
            raise UnprocessableEntityError(
                f"{cls.name} não opera a carteira de uma gestora."
            )
        ensure_available(
            cls,
            funds_enabled=self._funds_enabled,
            government_enabled=self._government_enabled,
        )
        resolved = self._with_defaults(cls, params, today)
        errors = cls.validate(resolved, set(self._engine.stocks))
        if errors:
            raise UnprocessableEntityError(" ".join(errors.values()))
        if previous and previous.cls is cls and previous.params == resolved:
            return

        if previous and previous.cls is cls:
            self._active[account.client_id] = ActiveStrategy(
                cls, resolved, previous.since, account
            )
            self._push_mode(
                account,
                StrategyLogKind.PARAMS,
                key,
                resolved,
                today,
                reason=f"{account.subject} mudou os parâmetros de {cls.name}",
            )
        else:
            canceled = self._engine.matching_engine.cancel_all(account.client_id)
            self._active[account.client_id] = ActiveStrategy(
                cls, resolved, today, account
            )
            if previous:
                kind = StrategyLogKind.SWITCHED
                reason = f"{account.subject} trocou {previous.cls.name} por {cls.name}"
                reason += _canceled_phrase(canceled, previous.cls.name, account)
            else:
                kind = StrategyLogKind.ENABLED
                reason = f"{account.subject} ligou {cls.name}"
                reason += _canceled_phrase(canceled, None, account)
            self._push_mode(
                account,
                kind,
                key,
                resolved,
                today,
                reason=reason,
                quantity=Decimal(canceled),
            )
        self._finish_mode_change(account, active=True)

    def mark_error_seen(self, user: UserDTO, today: date) -> None:
        account = StrategyAccount.of_user(user)
        state = self._state(account)
        if state.error is None or state.error_seen:
            return
        self._push_mode(account, StrategyLogKind.ERROR_SEEN, None, None, today)
        EventManager.flush()

    # =========================
    # Fase do dia
    # =========================

    def run(self, users: list[UserDTO], today: date) -> None:
        """Roda a estratégia de cada conta que a ligou: as pessoais na ordem dos jogadores, depois as das gestoras."""
        personal = [
            self._active[u.client_id]
            for u in sorted(users, key=lambda u: u.id)
            if u.client_id in self._active
        ]
        funds = sorted(
            (a for a in self._active.values() if a.account.fund_id is not None),
            key=lambda a: required(a.account.fund_id),
        )
        running = personal + funds
        if not running:
            return

        market = self._market(today)
        for active in running:
            self._run_one(active, market, today)

    def _run_one(self, active: ActiveStrategy, market: _Market, today: date) -> None:
        account = active.account
        ctx = self._context(account, self._account_market(market, account), today)
        try:
            active.cls().next(ctx, active.params)
            lines = [
                self._execute(account, active, intent, today) for intent in ctx.intents
            ]
        # A estratégia é código de terceiro: qualquer erro dela volta a conta ao manual
        except Exception as exc:  # noqa: BLE001
            self._fail(active, exc, today)
            return

        if lines:
            for client_id in self._engine.audience(account.client_id)[0]:
                notify(
                    "strategy_orders",
                    StrategyOrdersEventDTO(orders=lines).to_json(),
                    to=client_id,
                )

    def _fail(self, active: ActiveStrategy, exc: Exception, today: date) -> None:
        """A estratégia que dá erro volta a conta ao manual, com a causa no registro."""
        account = active.account
        logger.error("Erro na estratégia %s", active.cls.key, exc_info=exc)
        cause = (
            str(exc.detail)
            if isinstance(exc, HTTPException)
            else "erro inesperado do aplicativo"
        )
        message = f"Voltou ao manual: {active.cls.name} deu erro ({cause})"
        self._engine.matching_engine.cancel_all(account.client_id)
        del self._active[account.client_id]
        self._push_mode(
            account,
            StrategyLogKind.ERROR,
            active.cls.key,
            active.params,
            today,
            reason=message,
            detail="".join(traceback.format_exception(exc)),
        )
        self._notify_update(
            account, StrategyUpdateEventDTO(active=False, error=message)
        )
        # O backtest só tem contas pessoais
        if self.on_failure is not None and account.fund_id is None:
            self.on_failure(account.nickname, today, message)

    def _execute(
        self,
        account: StrategyAccount,
        active: ActiveStrategy,
        intent: Intent,
        today: date,
    ) -> StrategyOrderLineDTO:
        """Executa a intenção; a recusa do mercado ou do caixa vira uma linha "Recusada"."""
        row = StrategyEventDTO(
            simulation_id=self._engine.simulation_id,
            user_id=account.user_id,
            fund_id=account.fund_id,
            event_date=today,
            kind=StrategyLogKind.ORDER,
            strategy_key=active.cls.key,
            action=intent.action,
            ticker=intent.ticker,
            quantity=intent.quantity,
            reason=intent.reason,
            status=StrategyOrderStatus.REFUSED,
        )
        try:
            row = self._submit(account, intent, row)
        except HTTPException as exc:
            row = row.model_copy(update={"detail": str(exc.detail)})

        EventManager.push_event(row)
        return StrategyOrderLineDTO(
            action=row.action or intent.action,
            ticker=row.ticker,
            asset_name=row.asset_name,
            quantity=row.quantity,
            price=row.price,
            status=required(row.status),
            reason=row.reason,
            asset_uuid=row.asset_uuid,
        )

    def _submit(
        self, account: StrategyAccount, intent: Intent, row: StrategyEventDTO
    ) -> StrategyEventDTO:
        engine = self._engine
        match intent.action:
            case StrategyAction.BUY | StrategyAction.SELL:
                if not intent.ticker or not intent.quantity:
                    raise ValueError("Compra e venda precisam de ativo e quantidade")
                quantity = self._quantity_allowed(account, intent)
                # Toda compra de cota de gestora respeita o teto de preço sobre o PL por cota
                reference = engine.fund_references.get(intent.ticker)
                ceiling = (
                    price_ceiling(reference.nav)
                    if reference is not None and intent.action == StrategyAction.BUY
                    else None
                )
                order: Order = (
                    LimitOrder(
                        placed_on=engine.current_date,
                        client_id=account.client_id,
                        ticker=intent.ticker,
                        size=quantity,
                        action=_order_action(intent.action),
                        price=intent.limit
                        if ceiling is None
                        else min(intent.limit, ceiling),
                        automatic=True,
                    )
                    if intent.limit is not None
                    else MarketOrder(
                        placed_on=engine.current_date,
                        client_id=account.client_id,
                        ticker=intent.ticker,
                        size=quantity,
                        action=_order_action(intent.action),
                        automatic=True,
                        price_cap=ceiling,
                    )
                )
                engine.matching_engine.submit(order)
                return row.model_copy(
                    update={
                        **_order_result(order),
                        "order_type": "limit" if intent.limit is not None else "market",
                    }
                )
            case StrategyAction.CANCEL:
                if not intent.order_id:
                    raise ValueError("Cancelamento precisa da ordem")
                resting = engine.matching_engine.order_book.find(intent.order_id)
                if resting is None or not engine.matching_engine.cancel(
                    order_id=intent.order_id, client_id=account.client_id
                ):
                    raise ConflictError("A ordem não está mais aberta")
                return row.model_copy(
                    update={
                        "ticker": resting.ticker,
                        "quantity": resting.size,
                        "price": to_money(resting.price),
                        "order_type": "limit",
                        "status": StrategyOrderStatus.CANCELED,
                    }
                )
            case StrategyAction.INVEST:
                if not intent.asset_uuid or not intent.value:
                    raise ValueError("Aplicação e resgate precisam de título e valor")
                asset = engine.fixed_income_market.get_asset(str(intent.asset_uuid))
                if asset is None:
                    raise ConflictError("O título não está mais disponível")
                engine.fixed_broker.buy(account.client_id, asset, intent.value)
                return row.model_copy(
                    update={
                        "asset_uuid": asset.asset_uuid,
                        "asset_name": asset.name,
                        # Nas aplicações, o preço é o valor aplicado
                        "price": intent.value,
                        "order_type": "market",
                        "status": StrategyOrderStatus.EXECUTED,
                    }
                )
            case StrategyAction.REDEEM:
                if not intent.asset_uuid or not intent.value:
                    raise ValueError("Aplicação e resgate precisam de título e valor")
                asset = engine.fixed_income_market.get_asset(str(intent.asset_uuid))
                if asset is None:
                    raise ConflictError("O título não está mais disponível")
                net = intent.value.quantize(Decimal("0.01"))
                engine.fixed_broker.redeem(account.client_id, asset, net)
                return row.model_copy(
                    update={
                        "asset_uuid": asset.asset_uuid,
                        "asset_name": asset.name,
                        # Nos resgates, o preço é o líquido que chegou ao caixa
                        "price": net,
                        "order_type": "market",
                        "status": StrategyOrderStatus.EXECUTED,
                    }
                )

    def _quantity_allowed(self, account: StrategyAccount, intent: Intent) -> Decimal:
        """A quantidade da intenção; a compra de papel de preço sintético cabe em BOT_QUOTA_LIMIT dos papéis.

        O teto desconta a posição do bot e as compras dele ainda abertas.
        """
        quantity = required(intent.quantity)
        ticker = required(intent.ticker)
        engine = self._engine
        maker = engine.broker.maker_accounts.get(ticker)
        if maker is None or intent.action is not StrategyAction.BUY:
            return quantity
        position = engine.broker.get_positions(account.client_id).get(ticker)
        held = position.size if position is not None else Decimal(0)
        resting = sum(
            (
                order.remaining
                for order in engine.matching_engine.order_book.orders_of(
                    account.client_id
                )
                if order.ticker == ticker and order.action is OrderAction.BUY
            ),
            Decimal(0),
        )
        room = bot_room(maker.quotas, held, resting)
        if room <= 0:
            raise ConflictError("A posição do bot no ativo já está no teto")
        return min(quantity, room)

    def leftover_demand(
        self,
        bots: list[UserDTO],
        today: date,
        ticker: str,
        reference: FundReference,
        bias: float,
        quotas: Decimal,
    ) -> Decimal:
        """As cotas de `ticker` que os `bots` com a estratégia de cotas compram no último pregão da sobra.

        Cada bot roda a estratégia de verdade sobre o próprio contexto de hoje, com a cota na
        `reference` do dia da decisão e a opinião `bias`; o teto de BOT_QUOTA_LIMIT conta
        sobre as `quotas` em circulação.
        """
        demand = Decimal(0)
        for bot in bots:
            active = self._active.get(bot.client_id)
            if active is None or active.cls is not FundQuotas:
                continue
            market = self._market(today, active.account)
            quote = market.quotes.get(ticker)
            if quote is None:
                continue
            market = replace(
                market,
                quotes={**market.quotes, ticker: replace(quote, fund=reference)},
            )
            ctx = self._context(active.account, market, today)
            FundQuotas().run(ctx, active.params, lambda _: bias)
            wanted = sum(
                (
                    required(intent.quantity)
                    for intent in ctx.intents
                    if intent.action is StrategyAction.BUY and intent.ticker == ticker
                ),
                Decimal(0),
            )
            held = ctx.holdings.get(ticker)
            room = bot_room(quotas, held.size if held else Decimal(0), Decimal(0))
            demand += max(Decimal(0), min(wanted, room))
        return demand

    def _on_order_closed(self, order: Order) -> None:
        """A ordem limitada de estratégia que saiu do book fecha a linha dela no registro."""
        status = (
            StrategyOrderStatus.CANCELED
            if order.status is OrderStatus.CANCELED
            else StrategyOrderStatus.EXECUTED
        )
        # A linha precisa estar gravada para a situação mudar
        EventManager.flush()
        repository.strategy.set_order_status(
            self._engine.simulation_id, order.id, status
        )

    # =========================
    # Contexto
    # =========================

    def _account_market(self, market: _Market, account: StrategyAccount) -> _Market:
        """O mercado que a conta enxerga: a gestora não negocia cota de gestora."""
        if account.fund_id is None:
            return market
        return _Market(
            quotes={
                ticker: quote
                for ticker, quote in market.quotes.items()
                if ticker not in self._engine.fund_references
            },
            offers=market.offers,
            indicators=market.indicators,
        )

    def _market(self, today: date, account: StrategyAccount | None = None) -> _Market:
        engine = self._engine
        quotes: dict[str, Quote] = {}
        for ticker in engine.stocks:
            candle = engine.matching_engine.market_data.get_last(ticker)
            if candle is None:
                continue
            segment = engine.classification.get(ticker)
            best_ask = engine.matching_engine.order_book.best_sell(ticker)
            best_bid = engine.matching_engine.order_book.best_buy(ticker)
            quotes[ticker] = Quote(
                ticker,
                engine.stocks[ticker].name,
                candle.close,
                candle.volume,
                segment.sector if segment else None,
                segment.segment if segment else None,
                engine.stocks[ticker].asset_class.fractional,
                best_ask.price if best_ask else None,
                best_bid.price if best_bid else None,
                engine.fund_references.get(ticker),
                engine.state_fair_values.get(ticker),
            )
        market = _Market(
            quotes=quotes,
            offers=[
                offer(asset, today, engine.tax_policy_on(today))
                for asset in engine.fixed_income_market.get_available_assets()
                if asset.maturity_date > today
            ],
            indicators=Indicators(
                cdi=annual_index_rate(IndicatorSeries.CDI, today),
                selic=annual_index_rate(IndicatorSeries.SELIC, today),
                ipca=annual_index_rate(IndicatorSeries.IPCA, today),
            ),
        )
        return market if account is None else self._account_market(market, account)

    def _context(
        self, account: StrategyAccount, market: _Market, today: date
    ) -> StrategyContext:
        engine = self._engine
        client_id = account.client_id
        return StrategyContext(
            date=today,
            cash=max(engine.get_cash(client_id), Decimal(0)),
            holdings={
                ticker: Holding(ticker, p.size, p.reserved, p.avg_price)
                for ticker, p in engine.broker.get_positions(client_id).items()
                if p.size > 0
            },
            fixed_holdings=[
                FixedHolding(
                    p.asset.asset_uuid,
                    p.asset.name,
                    p.market_value(today, engine.fixed_quotes()),
                    p.asset.daily_liquidity,
                    # O robô resgata só liquidez diária; o Tesouro fica até o vencimento
                    redeemable_today(
                        p, today, engine.tax_policy_on(today), engine.fixed_quotes()
                    )
                    if p.asset.daily_liquidity
                    else None,
                )
                for p in engine.fixed_broker.get_fixed_positions(client_id).values()
            ],
            fixed_offers=market.offers,
            quotes=market.quotes,
            indicators=market.indicators,
            open_orders=[
                OpenOrder(
                    o.id,
                    o.ticker,
                    o.action,
                    getattr(o, "price", None),
                    o.remaining,
                )
                for o in engine.matching_engine.order_book.orders_of(client_id)
            ],
            seed=account.seed,
            history_source=lambda ticker, days: self._history.window(
                ticker, today, days
            ),
        )

    # =========================
    # Apoio
    # =========================

    def _with_defaults(
        self,
        cls: type[BaseStrategy],
        params: dict[str, StrategyParamValue],
        today: date,
    ) -> dict[str, StrategyParamValue]:
        return catalog.with_defaults(
            cls, params, today, self._engine.simulation_id, self._engine.stocks
        )

    def _push_mode(
        self,
        account: StrategyAccount,
        kind: StrategyLogKind,
        key: str | None,
        params: dict | None,
        today: date,
        *,
        reason: str | None = None,
        detail: str | None = None,
        quantity: Decimal | None = None,
    ) -> None:
        EventManager.push_event(
            StrategyEventDTO(
                simulation_id=self._engine.simulation_id,
                user_id=account.user_id,
                fund_id=account.fund_id,
                event_date=today,
                kind=kind,
                strategy_key=key,
                params=params,
                reason=reason,
                detail=detail,
                quantity=quantity,
            )
        )

    def _finish_mode_change(self, account: StrategyAccount, *, active: bool) -> None:
        EventManager.flush()
        self._notify_update(account, StrategyUpdateEventDTO(active=active))

    def _notify_update(
        self, account: StrategyAccount, event: StrategyUpdateEventDTO
    ) -> None:
        """A conta pessoal avisa o jogador; a gestora avisa quem opera a carteira dela."""
        for client_id in self._engine.audience(account.client_id)[0]:
            notify("strategy_update", event.to_json(), to=client_id)


@dataclass(frozen=True)
class _Market:
    """O que vale para todos os jogadores no dia, montado uma vez."""

    quotes: dict[str, Quote]
    offers: list[FixedIncomeOfferDTO]
    indicators: Indicators


def _order_action(action: StrategyAction) -> OrderAction:
    return OrderAction.BUY if action is StrategyAction.BUY else OrderAction.SELL


def _order_result(order: Order) -> dict:
    """Situação, quantidade e preço da ordem logo depois de enviada."""
    executed = order.size - order.remaining
    average = to_money(order.notional / float(executed)) if executed else None
    if isinstance(order, LimitOrder):
        done = order.remaining == 0
        if order.status is OrderStatus.CANCELED:
            status = StrategyOrderStatus.CANCELED
        else:
            status = StrategyOrderStatus.EXECUTED if done else StrategyOrderStatus.OPEN
        return {
            "order_id": order.id,
            "quantity": order.size,
            "price": average if done and average else to_money(order.price),
            "status": status,
        }
    return {
        "order_id": order.id,
        "quantity": executed,
        "price": average,
        "status": StrategyOrderStatus.EXECUTED
        if order.remaining == 0
        else StrategyOrderStatus.PARTIAL,
    }


def _canceled_phrase(
    count: int, strategy_name: str | None, account: StrategyAccount
) -> str:
    """Quantas ordens abertas foram canceladas na mudança, ou nada quando nenhuma."""
    if count == 0:
        return ""
    noun = "1 ordem" if count == 1 else f"{count} ordens"
    if strategy_name is None:
        verb = "foi cancelada" if count == 1 else "foram canceladas"
        if account.fund_id is not None:
            return (
                f" · {noun} da gestora, {'aberta' if count == 1 else 'abertas'}, {verb}"
            )
        return (
            f" · {noun} sua, aberta, {verb}"
            if count == 1
            else (f" · {noun} suas, abertas, {verb}")
        )
    verb = "foi cancelada" if count == 1 else "foram canceladas"
    return f" · {noun} de {strategy_name} {verb}"
