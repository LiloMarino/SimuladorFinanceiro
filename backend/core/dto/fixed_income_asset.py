import uuid
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from backend.core.dto.base import BaseDTO
from backend.core.enum import FixedIncomeType, RateIndexType


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedIncomeAssetDTO(BaseDTO):
    asset_uuid: UUID = field(default_factory=uuid.uuid4)
    name: str
    issuer: str
    investment_type: FixedIncomeType
    rate_index: RateIndexType
    maturity_date: date
    interest_rate: float | None
