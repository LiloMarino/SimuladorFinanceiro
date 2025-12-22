from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from backend.core.dto.base import BaseDTO


class RateIndexType(Enum):
    CDI = "CDI"
    IPCA = "IPCA"
    SELIC = "SELIC"
    PREFIXADO = "Prefixado"


class FixedIncomeType(Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO_DIRETO = "Tesouro Direto"


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedIncomeAssetDTO(BaseDTO):
    asset_uuid: UUID
    name: str
    issuer: str
    rate_index: RateIndexType
    investment_type: FixedIncomeType
    maturity_date: date
    interest_rate: Decimal | None
