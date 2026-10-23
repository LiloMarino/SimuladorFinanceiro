from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.core.enum import StrategyAction


@dataclass(frozen=True)
class Intent:
    """O que a estratégia quer fazer; o motor executa e registra o resultado."""

    action: StrategyAction
    # Frase em português para a coluna "Por quê" do registro
    reason: str
    ticker: str | None = None
    quantity: int | None = None
    # Sem limite, a ordem é a mercado
    limit: float | None = None
    order_id: str | None = None
    asset_uuid: UUID | None = None
    value: Decimal | None = None


def buy(ticker: str, quantity: int, reason: str, limit: float | None = None) -> Intent:
    return Intent(StrategyAction.BUY, reason, ticker, quantity, limit)


def sell(ticker: str, quantity: int, reason: str, limit: float | None = None) -> Intent:
    return Intent(StrategyAction.SELL, reason, ticker, quantity, limit)


def cancel(order_id: str, reason: str) -> Intent:
    return Intent(StrategyAction.CANCEL, reason, order_id=order_id)


def redeem(asset_uuid: UUID, value: Decimal, reason: str) -> Intent:
    """Resgate de liquidez diária; `value` é o líquido que a estratégia quer no caixa."""
    return Intent(StrategyAction.REDEEM, reason, asset_uuid=asset_uuid, value=value)


def invest(asset_uuid: UUID, value: Decimal, reason: str) -> Intent:
    return Intent(StrategyAction.INVEST, reason, asset_uuid=asset_uuid, value=value)
