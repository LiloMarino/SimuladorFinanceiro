import uuid
from datetime import date
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
    interest_rate: float
