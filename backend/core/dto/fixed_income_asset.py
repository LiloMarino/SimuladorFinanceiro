import uuid
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.enum import FixedIncomeType, RateIndexType


class FixedIncomeAssetDTO(BaseDTO):
    asset_uuid: UUID = Field(default_factory=uuid.uuid4)
    name: str
    issuer: str
    investment_type: FixedIncomeType
    rate_index: RateIndexType
    maturity_date: date
    interest_rate: Decimal


class FixedIncomeOfferDTO(FixedIncomeAssetDTO):
    """O título com o que ele rende hoje e o IR que paga se levado ao vencimento."""

    index_rate: Decimal
    # Taxa do título combinada com o indexador do dia: o que ele rende ao ano hoje
    effective_annual_rate: Decimal
    tax_exempt: bool
    income_tax_rate_at_maturity: Decimal
