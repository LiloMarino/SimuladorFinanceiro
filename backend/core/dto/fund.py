from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class FundDTO(BaseDTO):
    """Uma gestora da partida, como a linha de `funds` a guarda."""

    id: int
    stock_id: int
    portfolio_id: int
    client_id: uuid.UUID
    ticker: str
    founder_user_id: int
    manager_user_id: int
    name: str
    quotas: Decimal
    maker_quotas: Decimal
    maker_cash: Decimal
    offer_remaining: Decimal | None
    listed_on: date | None
    management_fee: Decimal
    performance_fee: Decimal
    pending_management_fee: Decimal | None
    pending_performance_fee: Decimal | None
    pending_from: date | None
    high_water_mark: Decimal | None
    high_water_mark_on: date | None
    last_performance_on: date | None


class FundDayDTO(BaseDTO):
    """O fechamento de uma gestora num pregão."""

    day: date
    nav: Decimal
    quotas: Decimal
    traded_quantity: Decimal
    traded_value: Decimal
    ranking_price: Decimal
