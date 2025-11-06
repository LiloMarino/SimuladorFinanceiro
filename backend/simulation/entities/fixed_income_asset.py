from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.data_provider import get_cdi_rate, get_ipca_rate, get_selic_rate


class FixedIncomeType(Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO_DIRETO = "Tesouro Direto"


class RateIndexType(Enum):
    CDI = "CDI"
    IPCA = "IPCA"
    SELIC = "SELIC"
    PREFIXADO = "Prefixado"


@dataclass
class FixedIncomeAsset:
    name: str
    issuer: str
    interest_rate: float | None
    rate_index: RateIndexType
    investment_type: FixedIncomeType
    maturity_date: datetime | None = None

    def apply_daily_interest(self):
        """
        Aplica juros diários. Para prefixado usa interest_rate,
        para pós-fixado precisa de uma função que retorne a taxa atual do índice.
        """
        if self.rate_index == RateIndexType.PREFIXADO:
            if self.interest_rate is None:
                raise ValueError("Taxa de prefixado não definida")
            daily_rate = self.interest_rate / 252
        else:
            annual_rate = self.get_index_rate(self.rate_index)
            daily_rate = annual_rate / 252

        self.invested_amount *= 1 + daily_rate

    def get_index_rate(self, rate_index: RateIndexType) -> float:
        match rate_index:
            case RateIndexType.CDI:
                return get_cdi_rate()
            case RateIndexType.IPCA:
                return get_ipca_rate()
            case RateIndexType.SELIC:
                return get_selic_rate()
            case RateIndexType.PREFIXADO:
                if self.interest_rate is not None:
                    return self.interest_rate
                else:
                    raise ValueError("Taxa de prefixado não definida")
