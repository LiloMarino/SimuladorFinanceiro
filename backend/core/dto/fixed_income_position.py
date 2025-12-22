from dataclasses import dataclass
from enum import Enum

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO


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
class FixedIncomePositionDTO(FixedIncomeAssetDTO):
    total_applied: float
