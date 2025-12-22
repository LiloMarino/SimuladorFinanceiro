import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from uuid import UUID

from backend.core.dto.base import BaseDTO


class RateIndexType(Enum):
    CDI = "CDI"
    IPCA = "IPCA"
    SELIC = "SELIC"
    PREFIXADO = "Prefixado"

    @property
    def db_value(self) -> str:
        return {
            RateIndexType.CDI: "CDI",
            RateIndexType.IPCA: "IPCA",
            RateIndexType.SELIC: "SELIC",
            RateIndexType.PREFIXADO: "PREFIXADO",
        }[self]


class FixedIncomeType(Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO_DIRETO = "Tesouro Direto"

    @property
    def db_value(self) -> str:
        return {
            FixedIncomeType.CDB: "CDB",
            FixedIncomeType.LCI: "LCI",
            FixedIncomeType.LCA: "LCA",
            FixedIncomeType.TESOURO_DIRETO: "TESOURO_DIRETO",
        }[self]


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedIncomeAssetDTO(BaseDTO):
    asset_uuid: UUID = field(default_factory=uuid.uuid4)
    name: str
    issuer: str
    investment_type: FixedIncomeType
    rate_index: RateIndexType
    maturity_date: date
    interest_rate: float | None
