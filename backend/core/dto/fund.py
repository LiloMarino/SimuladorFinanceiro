from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO

# Quatro letras e o 11 das cotas
FundTicker = Annotated[str, StringConstraints(pattern=r"^[A-Z]{4}11$")]
FundName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=30)
]
# Taxa ao ano em fração: 0,02 é 2%
FeeRate = Annotated[Decimal, Field(ge=0, le=1, decimal_places=4)]


class FundTermsDTO(BaseDTO):
    """O que a gestora mostra a quem a vê: cotas, oferta, taxas e marca d'água."""

    id: int
    ticker: str
    founder_user_id: int
    manager_user_id: int
    name: str
    quotas: Decimal
    maker_quotas: Decimal
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


class FundDTO(FundTermsDTO):
    """Uma gestora da partida, como a linha de `funds` a guarda."""

    stock_id: int
    portfolio_id: int
    client_id: uuid.UUID
    maker_cash: Decimal


class FundDayDTO(BaseDTO):
    """O fechamento de uma gestora num pregão."""

    day: date
    nav: Decimal
    quotas: Decimal
    traded_quantity: Decimal
    traded_value: Decimal
    ranking_price: Decimal


class FundSummaryDTO(FundTermsDTO):
    """A gestora na lista da partida, com o PL por cota de agora e o preço de ranking."""

    nav: Decimal | None
    ranking_price: Decimal | None


class FundDetailsDTO(FundSummaryDTO):
    """A gestora com a série de fechamentos dos pregões, do mais antigo ao mais recente."""

    days: list[FundDayDTO]


class FundFoundRequest(BaseDTO):
    name: FundName
    ticker: FundTicker
    management_fee: FeeRate
    performance_fee: FeeRate


class FundContributionStockRequest(BaseDTO):
    ticker: str
    quantity: Decimal = Field(gt=0, decimal_places=8)


class FundContributionRequest(BaseDTO):
    cash: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    stocks: list[FundContributionStockRequest] = Field(default_factory=list)


class FundContributionResponse(BaseDTO):
    quotas: Decimal


class FundOfferRequest(BaseDTO):
    quotas: int = Field(gt=0)


class FundFeesRequest(BaseDTO):
    management_fee: FeeRate
    performance_fee: FeeRate
