from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pandas as pd

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.strategy.context import (
    Holding,
    Indicators,
    Quote,
    StrategyContext,
)

TODAY = date(2004, 6, 1)


def closes(values: list[float]) -> pd.DataFrame:
    """Histórico OHLCV de pregões consecutivos que terminam em `TODAY`."""
    index = pd.bdate_range(end=pd.Timestamp(TODAY), periods=len(values))
    return pd.DataFrame(
        {
            "open": values,
            "high": values,
            "low": values,
            "close": values,
            "volume": [1000] * len(values),
        },
        index=index,
    )


def offer(
    rate_index: RateIndexType = RateIndexType.CDI,
    interest_rate: str = "1.00",
    tax: str = "0.15",
    name: str = "CDB Teste",
    player_cap: str | None = None,
) -> FixedIncomeOfferDTO:
    return FixedIncomeOfferDTO(
        asset_uuid=uuid.uuid4(),
        name=name,
        issuer="Banco",
        investment_type=FixedIncomeType.CDB,
        rate_index=rate_index,
        maturity_date=date(2006, 1, 2),
        interest_rate=Decimal(interest_rate),
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
    offers: list[FixedIncomeOfferDTO] | None = None,
) -> StrategyContext:
    frames = history or {}
    return StrategyContext(
        date=TODAY,
        cash=Decimal(cash),
        holdings=holdings or {},
        fixed_holdings=[],
        fixed_offers=offers or [],
        quotes={
            ticker: Quote(ticker, float(frame["close"].iloc[-1]), 1000, None, None)
            for ticker, frame in frames.items()
        },
        indicators=Indicators(Decimal("0.14"), Decimal("0.14"), Decimal("0.05")),
        open_orders=[],
        history_source=lambda ticker, days: frames[ticker].iloc[-days:],
    )
