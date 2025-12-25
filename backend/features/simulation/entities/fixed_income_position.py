from dataclasses import dataclass, field
from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import RateIndexType


@dataclass
class FixedIncomePosition:
    asset: FixedIncomeAssetDTO
    total_applied: float  # Capital inicial (C)
    current_value: float = field(init=False)  # Montante (M)

    def __post_init__(self):
        self.current_value = self.total_applied

    def invest(self, value: float):
        """
        Aporta mais capital:
        - aumenta o capital aplicado (C)
        - aumenta o montante (M)
        """
        self.total_applied += value
        self.current_value += value

    def apply_daily_interest(self, current_date: date):
        """
        Aplica juros diários sobre o montante (M).
        """
        if self.asset.rate_index == RateIndexType.PREFIXADO:
            if self.asset.interest_rate is None:
                raise ValueError("Taxa de prefixado não definida")
            daily_rate = self.asset.interest_rate / 252
        else:
            annual_rate = self.get_index_rate(current_date, self.asset.rate_index)
            daily_rate = annual_rate / 252

        self.current_value *= 1 + daily_rate

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
                raise ValueError("Taxa de prefixado não definida")
