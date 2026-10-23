from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    StrategyAction,
    StrategyGroup,
    StrategyLogKind,
    StrategyOrderStatus,
    StrategyParamKind,
)

# Valor de um parâmetro: número (dias, percentual) ou lista de tickers
type StrategyParamValue = int | list[str]


class StrategyParamDTO(BaseDTO):
    key: str
    label: str
    kind: StrategyParamKind
    default: StrategyParamValue
    min: int | None = None
    max: int | None = None
    unit: str | None = None
    # Como o parâmetro muda o que a estratégia faz
    hint: str


class StrategyInfoDTO(BaseDTO):
    key: str
    name: str
    # Uma linha, para a lista
    summary: str
    # A regra completa, para o detalhe
    description: str
    group: StrategyGroup
    params: list[StrategyParamDTO]


class StrategyActiveDTO(BaseDTO):
    key: str
    params: dict[str, StrategyParamValue]
    # Dia da partida em que o jogador ligou esta estratégia
    since: date


class StrategyErrorDTO(BaseDTO):
    strategy_key: str | None
    error_date: date
    # A causa em português
    message: str
    # Rastro técnico do erro, para copiar e investigar
    traceback: str | None
    seen: bool


class StrategyLastOrderDTO(BaseDTO):
    action: StrategyAction
    ticker: str | None
    asset_name: str | None
    quantity: int | None
    order_date: date
    order_type: str | None


class StrategyPanelDTO(BaseDTO):
    """O que a estratégia fez desde que o jogador a ligou."""

    orders_total: int
    executed: int
    partial: int
    open: int
    canceled: int
    refused: int
    # Retorno do patrimônio sem os aportes, e o Ibovespa no mesmo período (0.0382 = +3,82%)
    return_pct: Decimal | None
    ibov_pct: Decimal | None
    last_order: StrategyLastOrderDTO | None


class MyStrategyDTO(BaseDTO):
    # Nulo é o modo manual
    active: StrategyActiveDTO | None
    # Presente quando a última coisa que aconteceu foi um erro que devolveu ao manual
    error: StrategyErrorDTO | None
    # A partida foi retomada com a estratégia ligada
    resumed: bool
    # Ordens abertas do jogador no mercado, canceladas ao ligar, trocar ou desligar
    open_orders: int
    panel: StrategyPanelDTO | None


class SetStrategyRequestDTO(BaseDTO):
    # Nulo volta ao manual
    key: str | None
    params: dict[str, StrategyParamValue] = Field(default_factory=dict)


class SignalRequestDTO(BaseDTO):
    params: dict[str, StrategyParamValue]
    ticker: str


class SignalPointDTO(BaseDTO):
    date: date
    value: float


class SignalLineDTO(BaseDTO):
    key: Literal["price", "short", "long"]
    label: str
    points: list[SignalPointDTO]


class SignalMarkerDTO(BaseDTO):
    date: date
    side: Literal["buy", "sell"]


class SignalDTO(BaseDTO):
    """O que a estratégia olha num ativo: as linhas do gráfico e onde ela compraria e venderia."""

    # Erros por campo, em português; com erro não há linhas
    errors: dict[str, str]
    lines: list[SignalLineDTO]
    markers: list[SignalMarkerDTO]
    # Dias de histórico que o ativo tem e quantos a estratégia pede
    available_days: int
    needed_days: int


class StrategyLogRowDTO(BaseDTO):
    id: int
    event_date: date
    kind: StrategyLogKind
    strategy_key: str | None
    strategy_name: str | None
    action: StrategyAction | None
    ticker: str | None
    asset_name: str | None
    quantity: int | None
    price: Decimal | None
    order_type: str | None
    reason: str | None
    status: StrategyOrderStatus | None
    # Por que o mercado ou o caixa recusou a ordem
    detail: str | None


class StrategyLogPageDTO(BaseDTO):
    items: list[StrategyLogRowDTO]
    total: int


class StrategyOrderLineDTO(BaseDTO):
    action: StrategyAction
    ticker: str | None
    asset_name: str | None
    quantity: int | None
    price: Decimal | None
    status: StrategyOrderStatus
    reason: str | None
    asset_uuid: UUID | None = None
