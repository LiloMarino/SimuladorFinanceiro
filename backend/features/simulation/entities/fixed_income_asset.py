import uuid
from dataclasses import asdict, dataclass, field
from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeType, RateIndexType
from backend.types import JSONValue


@dataclass
class FixedIncomeAsset:
    name: str
    issuer: str
    interest_rate: float | None
    rate_index: RateIndexType
    investment_type: FixedIncomeType
    maturity_date: date | None = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def apply_daily_interest(self, current_date: date):
        """
        Aplica juros diários. Para prefixado usa interest_rate,
        para pós-fixado precisa de uma função que retorne a taxa atual do índice.
        """
        if self.rate_index == RateIndexType.PREFIXADO:
            if self.interest_rate is None:
                raise ValueError("Taxa de prefixado não definida")
            daily_rate = self.interest_rate / 252
        else:
            annual_rate = self.get_index_rate(current_date, self.rate_index)
            daily_rate = annual_rate / 252

        self.invested_amount *= 1 + daily_rate

    def get_index_rate(self, current_date: date, rate_index: RateIndexType) -> float:
        match rate_index:
            case RateIndexType.CDI:
                return repository.economic.get_cdi_rate(current_date)
            case RateIndexType.IPCA:
                return repository.economic.get_ipca_rate(current_date)
            case RateIndexType.SELIC:
                return repository.economic.get_selic_rate(current_date)
            case RateIndexType.PREFIXADO:
                if self.interest_rate is not None:
                    return self.interest_rate
                else:
                    raise ValueError("Taxa de prefixado não definida")

    def to_dict(self) -> dict[str, JSONValue]:
        data = asdict(self)
        data["rate_index"] = self.rate_index.value
        data["investment_type"] = self.investment_type.value
        data["maturity_date"] = (
            self.maturity_date.isoformat() if self.maturity_date else None
        )
        return data
