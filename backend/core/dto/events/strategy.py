from decimal import Decimal
from uuid import UUID

from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import StrategyAction, StrategyLogKind, StrategyOrderStatus


class StrategyEventDTO(BaseEventDTO):
    """Uma linha do registro da estratégia: ordem enviada ou mudança de modo."""

    kind: StrategyLogKind
    strategy_key: str | None = None
    # Parâmetros em vigor, nas linhas que ligam, trocam ou mudam a estratégia
    params: dict | None = None
    action: StrategyAction | None = None
    ticker: str | None = None
    # Título de renda fixa, nas aplicações
    asset_uuid: UUID | None = None
    asset_name: str | None = None
    # Quantidade da ordem; nas linhas de modo, quantas ordens abertas foram canceladas
    quantity: Decimal | None = None
    price: Decimal | None = None
    order_type: str | None = None
    order_id: str | None = None
    reason: str | None = None
    status: StrategyOrderStatus | None = None
    # Mensagem da recusa ou traceback do erro
    detail: str | None = None
