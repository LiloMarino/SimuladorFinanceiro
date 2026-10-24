from __future__ import annotations

import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException

from backend.core import repository
from backend.core.dto.events.strategy import StrategyEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
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
    StrategyAction,
    StrategyLogKind,
    StrategyOrderStatus,
    StrategyView,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.indicators import annual_index_rate
from backend.core.repository.strategy import LogFilter
from backend.core.runtime.event_manager import EventManager
from backend.features.fixed_income.accrual import offer
from backend.features.fixed_income.liquidity import redeemable_today
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
from backend.features.strategy.intents import Intent
from backend.features.strategy.panel import build_panel
from backend.features.strategy.price_history import PriceHistory
from backend.features.strategy.registry import STRATEGIES, get_strategy
from backend.features.strategy.state import derive_state
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
class ActiveStrategy:
    cls: type[BaseStrategy]
    params: dict[str, StrategyParamValue]
    since: date


class StrategyRunner:
    """
    Estratégias ligadas dos jogadores e a fase do dia em que elas operam.

    Responsável por:
    - Guardar a estratégia ativa de cada jogador (ausente é o modo manual)
    - Rodar cada estratégia a cada dia, na ordem dos jogadores, e executar as intenções
    - Registrar ordens e mudanças de modo no registro da estratégia
    - Devolver ao manual o jogador cuja estratégia deu erro
    """

    def __init__(
        self, engine: SimulationEngine, price_impact: PriceImpact, end_date: date
    ) -> None:
        self._engine = engine
        self._history = PriceHistory(engine.simulation_id, end_date, price_impact)
        self._active: dict[UUID, ActiveStrategy] = {}
        # Chamado com o jogador, o dia e a mensagem quando a estratégia dele dá erro
        self.on_failure: Callable[[UserDTO, date, str], None] | None = None
        engine.matching_engine.on_order_closed = self._on_order_closed

    # =========================
    # Estado
    # =========================

    def load(self, users: list[UserDTO], resumed_on: date | None) -> None:
        """Retoma a estratégia de cada jogador a partir do registro gravado."""
        rows = repository.strategy.mode_rows(self._engine.simulation_id)
        for user in users:
            state = derive_state([r for r in rows if r.user_id == user.id])
            if state.key not in STRATEGIES or state.since is None:
                continue
            self._active[user.client_id] = ActiveStrategy(
                STRATEGIES[state.key], state.params or {}, state.since
            )
            if resumed_on is not None:
                self._push_mode(
                    user,
                    StrategyLogKind.RESUMED,
                    state.key,
                    state.params,
                    resumed_on,
                    reason=f"A partida foi retomada com {STRATEGIES[state.key].name} ligada",
                )

    def ensure_manual(self, client_id: UUID) -> None:
        """A boleta do jogador só vale no modo manual."""
        if client_id in self._active:
            raise ConflictError(
                "O automático está ligado. Volte ao manual para operar à mão."
            )

    # =========================
    # Consulta
    # =========================

    def infos(self, today: date) -> list[StrategyInfoDTO]:
        return catalog.infos(today, self._engine.simulation_id, self._engine.stocks)

    def mine(self, user: UserDTO, today: date) -> MyStrategyDTO:
        state = derive_state(
            repository.strategy.mode_rows(self._engine.simulation_id, user.id)
        )
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
                self._engine.matching_engine.order_book.orders_of(user.client_id)
            ),
            panel=build_panel(self._engine.simulation_id, user.id, active.since)
            if active
            else None,
        )

    def log(
        self, user: UserDTO, kind: LogFilter, offset: int, limit: int
    ) -> StrategyLogPageDTO:
        rows, total = repository.strategy.log_page(
            self._engine.simulation_id,
            user.id,
            kind,
            offset,
            min(limit, LOG_PAGE_LIMIT),
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
        user: UserDTO,
        key: str,
        params: dict[str, StrategyParamValue],
        today: date,
    ) -> StrategyViewDTO:
        """O ranking ou a alocação da estratégia sobre a carteira do jogador hoje, sem executar nada."""
        cls = get_strategy(key)
        merged = self._with_defaults(cls, params, today)
        errors = cls.validate(merged, set(self._engine.stocks))
        if errors or cls.view_kind not in (
            StrategyView.RANKING,
            StrategyView.ALLOCATION,
        ):
            return StrategyViewDTO(errors=errors, ranking=None, allocation=None)

        ctx = self._context(user, self._market(today), today)
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
        user: UserDTO,
        key: str | None,
        params: dict[str, StrategyParamValue],
        today: date,
    ) -> None:
        """Liga, troca, ajusta ou desliga a estratégia do jogador a partir do próximo dia."""
        previous = self._active.get(user.client_id)
        if key is None:
            if previous is None:
                return
            canceled = self._engine.matching_engine.cancel_all(user.client_id)
            del self._active[user.client_id]
            self._push_mode(
                user,
                StrategyLogKind.DISABLED,
                None,
                None,
                today,
                reason=f"Você voltou ao manual{_canceled_phrase(canceled, previous.cls.name)}",
                quantity=Decimal(canceled),
            )
            self._finish_mode_change(user, active=False)
            return

        cls = get_strategy(key)
        resolved = self._with_defaults(cls, params, today)
        errors = cls.validate(resolved, set(self._engine.stocks))
        if errors:
            raise UnprocessableEntityError(" ".join(errors.values()))
        if previous and previous.cls is cls and previous.params == resolved:
            return

        if previous and previous.cls is cls:
            self._active[user.client_id] = ActiveStrategy(cls, resolved, previous.since)
            self._push_mode(
                user,
                StrategyLogKind.PARAMS,
                key,
                resolved,
                today,
                reason=f"Você mudou os parâmetros de {cls.name}",
            )
        else:
            canceled = self._engine.matching_engine.cancel_all(user.client_id)
            self._active[user.client_id] = ActiveStrategy(cls, resolved, today)
            if previous:
                kind = StrategyLogKind.SWITCHED
                reason = f"Você trocou {previous.cls.name} por {cls.name}"
                reason += _canceled_phrase(canceled, previous.cls.name)
            else:
                kind = StrategyLogKind.ENABLED
                reason = f"Você ligou {cls.name}"
                reason += _canceled_phrase(canceled, None)
            self._push_mode(
                user,
                kind,
                key,
                resolved,
                today,
                reason=reason,
                quantity=Decimal(canceled),
            )
        self._finish_mode_change(user, active=True)

    def mark_error_seen(self, user: UserDTO, today: date) -> None:
        state = derive_state(
            repository.strategy.mode_rows(self._engine.simulation_id, user.id)
        )
        if state.error is None or state.error_seen:
            return
        self._push_mode(user, StrategyLogKind.ERROR_SEEN, None, None, today)
        EventManager.flush()

    # =========================
    # Fase do dia
    # =========================

    def run(self, users: list[UserDTO], today: date) -> None:
        """Roda a estratégia de cada jogador que a ligou, na ordem dos jogadores."""
        running = [
            u for u in sorted(users, key=lambda u: u.id) if u.client_id in self._active
        ]
        if not running:
            return

        market = self._market(today)
        for user in running:
            self._run_one(user, self._active[user.client_id], market, today)

    def _run_one(
        self,
        user: UserDTO,
        active: ActiveStrategy,
        market: _Market,
        today: date,
    ) -> None:
        ctx = self._context(user, market, today)
        try:
            active.cls().next(ctx, active.params)
            lines = [
                self._execute(user, active, intent, today) for intent in ctx.intents
            ]
        except Exception as exc:
            self._fail(user, active, exc, today)
            return

        if lines:
            notify(
                "strategy_orders",
                StrategyOrdersEventDTO(orders=lines).to_json(),
                to=user.client_id,
            )

    def _fail(
        self, user: UserDTO, active: ActiveStrategy, exc: Exception, today: date
    ) -> None:
        """A estratégia que dá erro volta o jogador ao manual, com a causa no registro."""
        logger.exception("Erro na estratégia %s", active.cls.key, exc_info=exc)
        cause = (
            str(exc.detail)
            if isinstance(exc, HTTPException)
            else "erro inesperado do aplicativo"
        )
        message = f"Voltou ao manual: {active.cls.name} deu erro ({cause})"
        self._engine.matching_engine.cancel_all(user.client_id)
        del self._active[user.client_id]
        self._push_mode(
            user,
            StrategyLogKind.ERROR,
            active.cls.key,
            active.params,
            today,
            reason=message,
            detail="".join(traceback.format_exception(exc)),
        )
        notify(
            "strategy_update",
            StrategyUpdateEventDTO(active=False, error=message).to_json(),
            to=user.client_id,
        )
        if self.on_failure is not None:
            self.on_failure(user, today, message)

    def _execute(
        self, user: UserDTO, active: ActiveStrategy, intent: Intent, today: date
    ) -> StrategyOrderLineDTO:
        """Executa a intenção; a recusa do mercado ou do caixa vira uma linha "Recusada"."""
        row = StrategyEventDTO(
            simulation_id=self._engine.simulation_id,
            user_id=user.id,
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
            row = self._submit(user, intent, row)
        except HTTPException as exc:
            row = row.model_copy(update={"detail": str(exc.detail)})

        EventManager.push_event(row)
        assert row.status is not None
        return StrategyOrderLineDTO(
            action=row.action or intent.action,
            ticker=row.ticker,
            asset_name=row.asset_name,
            quantity=row.quantity,
            price=row.price,
            status=row.status,
            reason=row.reason,
            asset_uuid=row.asset_uuid,
        )

    def _submit(
        self, user: UserDTO, intent: Intent, row: StrategyEventDTO
    ) -> StrategyEventDTO:
        engine = self._engine
        match intent.action:
            case StrategyAction.BUY | StrategyAction.SELL:
                assert intent.ticker and intent.quantity
                order: Order = (
                    LimitOrder(
                        client_id=user.client_id,
                        ticker=intent.ticker,
                        size=intent.quantity,
                        action=_order_action(intent.action),
                        price=intent.limit,
                        automatic=True,
                    )
                    if intent.limit is not None
                    else MarketOrder(
                        client_id=user.client_id,
                        ticker=intent.ticker,
                        size=intent.quantity,
                        action=_order_action(intent.action),
                        automatic=True,
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
                assert intent.order_id
                resting = engine.matching_engine.order_book.find(intent.order_id)
                if resting is None or not engine.matching_engine.cancel(
                    order_id=intent.order_id, client_id=user.client_id
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
                assert intent.asset_uuid and intent.value
                asset = engine.fixed_income_market.get_asset(str(intent.asset_uuid))
                if asset is None:
                    raise ConflictError("O título não está mais disponível")
                engine.fixed_broker.buy(user.client_id, asset, intent.value)
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
                assert intent.asset_uuid and intent.value
                asset = engine.fixed_income_market.get_asset(str(intent.asset_uuid))
                if asset is None:
                    raise ConflictError("O título não está mais disponível")
                net = intent.value.quantize(Decimal("0.01"))
                engine.fixed_broker.redeem(user.client_id, asset, net)
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

    def _market(self, today: date) -> _Market:
        engine = self._engine
        quotes: dict[str, Quote] = {}
        for ticker in engine.stocks:
            candle = engine.matching_engine.market_data.get_last(ticker)
            if candle is None:
                continue
            segment = engine.classification.get(ticker)
            quotes[ticker] = Quote(
                ticker,
                engine.stocks[ticker].name,
                candle.close,
                candle.volume,
                segment.sector if segment else None,
                segment.segment if segment else None,
            )
        return _Market(
            quotes=quotes,
            offers=[
                offer(asset, today)
                for asset in engine.fixed_income_market.get_available_assets()
                if asset.maturity_date > today
            ],
            indicators=Indicators(
                cdi=annual_index_rate(IndicatorSeries.CDI, today),
                selic=annual_index_rate(IndicatorSeries.SELIC, today),
                ipca=annual_index_rate(IndicatorSeries.IPCA, today),
            ),
        )

    def _context(self, user: UserDTO, market: _Market, today: date) -> StrategyContext:
        engine = self._engine
        client_id = user.client_id
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
                    p.current_value,
                    p.asset.daily_liquidity,
                    redeemable_today(p, today),
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
        user: UserDTO,
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
                user_id=user.id,
                event_date=today,
                kind=kind,
                strategy_key=key,
                params=params,
                reason=reason,
                detail=detail,
                quantity=quantity,
            )
        )

    def _finish_mode_change(self, user: UserDTO, *, active: bool) -> None:
        EventManager.flush()
        notify(
            "strategy_update",
            StrategyUpdateEventDTO(active=active).to_json(),
            to=user.client_id,
        )


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
        return {
            "order_id": order.id,
            "quantity": order.size,
            "price": average if done and average else to_money(order.price),
            "status": StrategyOrderStatus.EXECUTED
            if done
            else StrategyOrderStatus.OPEN,
        }
    return {
        "order_id": order.id,
        "quantity": executed,
        "price": average,
        "status": StrategyOrderStatus.EXECUTED
        if order.remaining == 0
        else StrategyOrderStatus.PARTIAL,
    }


def _canceled_phrase(count: int, strategy_name: str | None) -> str:
    """Quantas ordens abertas foram canceladas na mudança, ou nada quando nenhuma."""
    if count == 0:
        return ""
    noun = "1 ordem" if count == 1 else f"{count} ordens"
    if strategy_name is None:
        verb = "foi cancelada" if count == 1 else "foram canceladas"
        return (
            f" · {noun} sua, aberta, {verb}"
            if count == 1
            else (f" · {noun} suas, abertas, {verb}")
        )
    verb = "foi cancelada" if count == 1 else "foram canceladas"
    return f" · {noun} de {strategy_name} {verb}"
