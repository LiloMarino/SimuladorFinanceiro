"""
Os avisos por ativo da página do ativo: o servidor entrega pronto o que a tela mostra,
inclusive o que ele calcula a partir de outro dado.

- Prévia da ordem e indicadores técnicos derivam do pedido do cliente (assinatura com
  parâmetro): a rota HTTP registra o último pedido dele no ativo e cada publicação
  recalcula para quem ainda assina, entregando só àquele cliente.
- Padrões de vela são iguais para todos: calculados uma vez por ativo assinado.
- A estatal do ativo vai a cada assinante, com a parte "você" dele.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException

from backend.core.dto.candle import CandleDTO
from backend.core.dto.order_preview import OrderPreviewDTO, OrderPreviewRequest
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.dto.technical_indicators import (
    IndicatorsRequestDTO,
    TechnicalIndicatorsDTO,
)
from backend.core.runtime.user_manager import UserManager
from backend.features.realtime import notify, subscribed_clients
from backend.features.realtime.client_requests import ClientRequests
from backend.features.realtime.schemas import (
    IndicatorsUpdateEventDTO,
    OrderPreviewEventDTO,
    StateCompanyUpdateEventDTO,
)
from backend.features.simulation.feed_support import (
    guarded,
    refusal_mark,
    refusal_reason,
)
from backend.features.technical_analysis.patterns import build_candle_patterns_update
from backend.features.technical_analysis.summary import (
    build_indicators_update,
    build_technical_indicators,
    price_frame,
)

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation

CANDLE_PATTERNS_EVENT = "candle_patterns_update"
STATE_COMPANY_EVENT = "state_company_update"


@dataclass
class WatchedPreview:
    """O último pedido de prévia do cliente no ativo e a marca do que o último envio mostrou."""

    requester: UUID
    account: int | None
    request: OrderPreviewRequest
    seen: tuple | None = None


class AssetPageFeed:
    """Os avisos por ativo de uma partida; todos os métodos rodam com o lock da simulação."""

    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        self._previews = ClientRequests[WatchedPreview]("order_preview")
        self._indicators = ClientRequests[IndicatorsRequestDTO]("indicators_update")
        # Ativos com prévia registrada: a varredura fora do dia só olha para eles
        self._previewed: set[str] = set()

    # Prévia da ordem

    def watch_preview(
        self,
        requester: UUID,
        account: int | None,
        ticker: str,
        request: OrderPreviewRequest,
    ) -> OrderPreviewDTO:
        """Calcula a prévia, responde e deixa o pedido registrado para os próximos avisos."""
        acting = self._simulation.acting_client(requester, account)
        watched = WatchedPreview(requester, account, request)
        try:
            preview = self._preview(acting, ticker, request)
        except HTTPException as exc:
            # Só a recusa de regra registra o pedido: o aviso traz o motivo e a prévia que voltar a caber
            reason = refusal_reason(exc)
            if reason is not None:
                watched.seen = refusal_mark(reason)
                self._register(ticker, requester, watched)
            raise
        watched.seen = self._fingerprint(acting, ticker, request)
        self._register(ticker, requester, watched)
        return preview

    def _register(self, ticker: str, requester: UUID, watched: WatchedPreview) -> None:
        self._previews.remember(ticker, requester, watched)
        self._previewed.add(ticker)

    def refresh_previews(self) -> None:
        """Manda de novo a prévia que o caixa, a posição ou o preço estimado mudaram fora do dia."""
        for ticker in list(self._previewed):
            for client_id, watched in self._previews.pending(ticker).items():
                guarded(
                    partial(
                        self._send_preview,
                        ticker,
                        client_id,
                        watched,
                        only_changed=True,
                    ),
                    "a prévia da ordem",
                )

    def _send_preview(
        self,
        ticker: str,
        client_id: UUID,
        watched: WatchedPreview,
        *,
        only_changed: bool,
    ) -> None:
        preview: OrderPreviewDTO | None = None
        refused: str | None = None
        try:
            acting = self._simulation.acting_client(watched.requester, watched.account)
            seen = self._fingerprint(acting, ticker, watched.request)
            if only_changed and seen == watched.seen:
                return
            preview = self._preview(acting, ticker, watched.request)
        except HTTPException as exc:
            refused = refusal_reason(exc)
            if refused is None:
                raise
            seen = refusal_mark(refused)
            if only_changed and seen == watched.seen:
                return
        watched.seen = seen
        self._previews.send(
            ticker,
            client_id,
            OrderPreviewEventDTO(
                request=watched.request,
                account=watched.account,
                preview=preview,
                refused=refused,
            ),
        )

    def _preview(
        self, acting: UUID, ticker: str, request: OrderPreviewRequest
    ) -> OrderPreviewDTO:
        return self._simulation.preview_order(
            acting,
            ticker,
            request.action,
            request.quantity,
            request.limit_price,
            request.amount,
            bool(request.max_size),
        )

    def _fingerprint(
        self, acting: UUID, ticker: str, request: OrderPreviewRequest
    ) -> tuple:
        """O que a prévia lê e muda fora do dia: o caixa, a posição no ativo e o preço estimado."""
        engine = self._simulation._engine
        position = engine.broker.get_positions(acting).get(ticker)
        held: tuple[Decimal, ...] = (
            (position.size, position.reserved, position.avg_price) if position else ()
        )
        return (
            engine.get_cash(acting),
            held,
            engine.estimated_price(ticker, request.action, request.limit_price),
        )

    # Indicadores técnicos

    def watch_indicators(
        self, requester: UUID, ticker: str, request: IndicatorsRequestDTO
    ) -> TechnicalIndicatorsDTO | None:
        """Calcula os indicadores inteiros, responde e registra o pedido para os avisos do dia."""
        details = self._simulation.get_stock_details(ticker)
        if details is None:
            return None
        result = build_technical_indicators(price_frame(details.history), request)
        self._indicators.remember(ticker, requester, request)
        return result

    # Publicação do dia

    def publish_day(self, candles: Iterable[CandleDTO]) -> None:
        """A cada pregão, entrega o dado novo de cada ativo a quem o assina."""
        hints = self._simulation.settings.show_chart_hints
        for candle in candles:
            ticker = candle.ticker
            self._publish_previews(ticker)
            self._publish_chart(ticker, candle, hints)
            self._publish_state_company(ticker)

    def _publish_previews(self, ticker: str) -> None:
        pending = self._previews.pending(ticker)
        for client_id, watched in pending.items():
            guarded(
                partial(
                    self._send_preview, ticker, client_id, watched, only_changed=False
                ),
                "a prévia da ordem",
            )
        if not pending:
            self._previewed.discard(ticker)

    def _publish_chart(self, ticker: str, candle: CandleDTO, hints: bool) -> None:
        pending = self._indicators.pending(ticker)
        patterns_event = f"{CANDLE_PATTERNS_EVENT}:{ticker}"
        patterns_wanted = hints and bool(subscribed_clients(patterns_event))
        if not pending and not patterns_wanted:
            return
        frame = price_frame(self._history(ticker, candle))
        previous = frame.index[-2].date() if len(frame) > 1 else None
        for client_id, request in pending.items():
            self._indicators.send(
                ticker,
                client_id,
                IndicatorsUpdateEventDTO(
                    request=request,
                    previous_date=previous,
                    update=build_indicators_update(frame, request),
                ),
            )
        if patterns_wanted:
            notify(patterns_event, build_candle_patterns_update(frame).to_json())

    def _publish_state_company(self, ticker: str) -> None:
        event = f"{STATE_COMPANY_EVENT}:{ticker}"
        for client_id in subscribed_clients(event):
            user = UserManager.get_user(client_id)
            if user is None:
                continue
            detail = self._simulation.get_state_company_detail(user, ticker)
            if detail is not None:
                notify(
                    event,
                    StateCompanyUpdateEventDTO(detail=detail).to_json(),
                    to=client_id,
                )

    def _history(self, ticker: str, candle: CandleDTO) -> list[StockPriceHistoryDTO]:
        """O histórico que o gráfico lê, com o pregão de hoje mesmo quando ainda não está salvo (cotas e estatais)."""
        details = self._simulation.get_stock_details(ticker)
        history = list(details.history) if details is not None else []
        if not history or history[-1].price_date < candle.price_date:
            history.append(
                StockPriceHistoryDTO(
                    price_date=candle.price_date,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                )
            )
        return history
