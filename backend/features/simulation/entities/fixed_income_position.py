from dataclasses import dataclass, field
from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.fixed_income_position import RateIndexType


@dataclass
class FixedIncomePosition:
    asset: FixedIncomeAssetDTO
    total_applied: float
    current_value: float = field(init=False)

    def invest(self, value: float):
        self.total_applied += value

    def apply_daily_interest(self, current_date: date):
        """
        Aplica juros diários. Para prefixado usa interest_rate,
        para pós-fixado precisa de uma função que retorne a taxa atual do índice.
        """
        if self.asset.rate_index == RateIndexType.PREFIXADO:
            if self.asset.interest_rate is None:
                raise ValueError("Taxa de prefixado não definida")
            daily_rate = self.asset.interest_rate / 252
        else:
            annual_rate = self.get_index_rate(current_date, self.asset.rate_index)
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
                if self.asset.interest_rate is not None:
                    return self.asset.interest_rate
                else:
                    raise ValueError("Taxa de prefixado não definida")
