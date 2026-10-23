from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.context import (
    FixedHolding,
    Holding,
    Indicators,
    Quote,
    StrategyContext,
)

TODAY = date(2004, 6, 1)


def closes(
    values: list[float],
    *,
    volumes: list[int] | None = None,
    highs: list[float] | None = None,
    lows: list[float] | None = None,
) -> pd.DataFrame:
    """Histórico OHLCV de pregões consecutivos que terminam em `TODAY`.

    Sem `highs`, `lows` e `volumes`, a máxima e a mínima são o fechamento e o volume é 1000."""
    index = pd.bdate_range(end=pd.Timestamp(TODAY), periods=len(values))
    return pd.DataFrame(
        {
            "open": values,
            "high": highs or values,
            "low": lows or values,
            "close": values,
            "volume": volumes or [1000] * len(values),
        },
        index=index,
    )


def offer(
    rate_index: RateIndexType = RateIndexType.CDI,
    interest_rate: str = "1.00",
    tax: str = "0.15",
    name: str = "CDB Teste",
    player_cap: str | None = None,
    daily_liquidity: bool = False,
) -> FixedIncomeOfferDTO:
    return FixedIncomeOfferDTO(
        asset_uuid=uuid.uuid4(),
        name=name,
        issuer="Banco",
        investment_type=FixedIncomeType.CDB,
        rate_index=rate_index,
        maturity_date=date(2006, 1, 2),
        interest_rate=Decimal(interest_rate),
        daily_liquidity=daily_liquidity,
        player_cap=None if player_cap is None else Decimal(player_cap),
        index_rate=Decimal("0.14"),
        effective_annual_rate=Decimal("0.14"),
        tax_exempt=False,
        income_tax_rate_at_maturity=Decimal(tax),
    )


def context(
    *,
    cash: str = "10000",
    history: dict[str, pd.DataFrame] | None = None,
    holdings: dict[str, Holding] | None = None,
    fixed_holdings: list[FixedHolding] | None = None,
    offers: list[FixedIncomeOfferDTO] | None = None,
) -> StrategyContext:
    frames = history or {}
    return StrategyContext(
        date=TODAY,
        cash=Decimal(cash),
        holdings=holdings or {},
        fixed_holdings=fixed_holdings or [],
        fixed_offers=offers or [],
        quotes={
            ticker: Quote(
                ticker, ticker, float(frame["close"].iloc[-1]), 1000, None, None
            )
            for ticker, frame in frames.items()
        },
        indicators=Indicators(Decimal("0.14"), Decimal("0.14"), Decimal("0.05")),
        open_orders=[],
        history_source=lambda ticker, days: frames[ticker].iloc[-days:],
    )


def first_day_with_intents(
    strategy: BaseStrategy,
    prices: list[float],
    params: dict[str, StrategyParamValue],
    *,
    start: int,
    **ctx_kwargs: Any,
) -> StrategyContext:
    """O contexto do primeiro dia da série, a partir de `start`, em que a estratégia enfileira ordens."""
    ctx: StrategyContext | None = None
    for end in range(start, len(prices) + 1):
        ctx = context(history={"AAA": closes(prices[:end])}, **ctx_kwargs)
        strategy.next(ctx, params)
        if ctx.intents:
            break
    assert ctx is not None
    return ctx
