from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

import pandas as pd

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.enum import OrderAction
from backend.features.strategy import intents
from backend.features.strategy.intents import Intent


@dataclass(frozen=True)
class Quote:
    ticker: str
    name: str
    close: float
    volume: int
    sector: str | None
    segment: str | None


@dataclass(frozen=True)
class Holding:
    ticker: str
    size: Decimal
    # Parte da posição presa em ordens abertas
    reserved: Decimal
    avg_price: Decimal


@dataclass(frozen=True)
class FixedHolding:
    asset_uuid: UUID
    name: str
    current_value: Decimal
    daily_liquidity: bool
    # Líquido que o resgate de hoje manda ao caixa; nulo sem liquidez diária
    redeemable: Decimal | None


@dataclass(frozen=True)
class OpenOrder:
    id: str
    ticker: str
    action: OrderAction
    # Nulo é ordem a mercado
    price: float | None
    remaining: Decimal


@dataclass(frozen=True)
class Indicators:
    """Taxas anuais conhecidas no dia (0.149 = 14,9% a.a.)."""

    cdi: Decimal
    selic: Decimal
    ipca: Decimal


@dataclass(frozen=True)
class StrategyContext:
    """
    O que a estratégia enxerga do jogador e do mercado num dia da partida.

    Tudo é dado simples montado da memória do motor, sem acesso ao banco, e as
    intenções ficam na fila do contexto até o motor executá-las.
    """

    date: date
    # Caixa disponível; o saldo negativo (cheque especial) conta como zero
    cash: Decimal
    holdings: dict[str, Holding]
    fixed_holdings: list[FixedHolding]
    # Ofertas de renda fixa do dia, com a taxa real (sem a máscara da assistência)
    fixed_offers: list[FixedIncomeOfferDTO]
    quotes: dict[str, Quote]
    indicators: Indicators
    open_orders: list[OpenOrder]
    history_source: Callable[[str, int], pd.DataFrame]
    intents: list[Intent] = field(default_factory=list)

    def history(self, ticker: str, days: int) -> pd.DataFrame:
        """Os últimos `days` pregões do ativo até hoje (OHLCV), do mais antigo ao mais novo."""
        return self.history_source(ticker, days)

    def buy(
        self,
        ticker: str,
        quantity: Decimal | int,
        reason: str,
        limit: float | None = None,
    ) -> None:
        self.intents.append(intents.buy(ticker, quantity, reason, limit))

    def sell(
        self,
        ticker: str,
        quantity: Decimal | int,
        reason: str,
        limit: float | None = None,
    ) -> None:
        self.intents.append(intents.sell(ticker, quantity, reason, limit))

    def cancel(self, order_id: str, reason: str) -> None:
        self.intents.append(intents.cancel(order_id, reason))

    def invest(self, asset_uuid: UUID, value: Decimal, reason: str) -> None:
        self.intents.append(intents.invest(asset_uuid, value, reason))

    def redeem(self, asset_uuid: UUID, value: Decimal, reason: str) -> None:
        self.intents.append(intents.redeem(asset_uuid, value, reason))
