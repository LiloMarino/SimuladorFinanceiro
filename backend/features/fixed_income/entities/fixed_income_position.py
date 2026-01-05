from dataclasses import dataclass, field
from datetime import date

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType


@dataclass
class FixedIncomePosition:
    asset: FixedIncomeAssetDTO
    total_applied: float  # Capital inicial (C)
    current_value: float = field(init=False)  # Montante (M)
    first_applied_date: date  # Data do primeiro aporte

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
        annual_rate = self.get_index_rate(current_date, self.asset.rate_index)
        daily_rate = self.annual_to_daily_rate(annual_rate)
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
                return self.asset.interest_rate

    def annual_to_daily_rate(self, annual_rate: float) -> float:
        return (1 + annual_rate) ** (1 / 252) - 1

    def calculate_ir(self, current_date: date) -> float:
        if self.asset.investment_type in (FixedIncomeType.LCI, FixedIncomeType.LCA):
            return 0

        days = (current_date - self.first_applied_date).days

        if days <= 180:
            rate = 0.225
        elif days <= 360:
            rate = 0.20
        elif days <= 720:
            rate = 0.175
        else:
            rate = 0.15

        profit = self.current_value - self.total_applied
        return profit * rate
