from __future__ import annotations

from decimal import Decimal

from backend.core.dto.base import BaseDTO


class PositionDTO(BaseDTO):
    ticker: str
    size: Decimal
    reserved: Decimal
    total_cost: Decimal
    avg_price: Decimal
    current_price: Decimal
    current_value: Decimal
    return_value: Decimal
    return_pct: Decimal


class PortfolioPositionDTO(PositionDTO):
    name: str
    portfolio_pct: Decimal
    # Fração (0.06 = 6%) do provento por ação dos últimos 12 meses sobre o preço de hoje;
    # nula na cripto, que não paga
    dividend_yield_12m: Decimal | None
    # O mesmo provento sobre o preço médio do jogador
    yield_on_cost: Decimal | None
    # Tudo que o ativo pagou ao jogador na partida, mesmo com venda e recompra no meio
    dividends_received: Decimal
