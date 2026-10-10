from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.features.fixed_income.accrual import (
    daily_factor,
    income_tax_rate,
    index_daily_rate_on,
    net_redemption,
    redemption_date,
)


@dataclass
class FixedIncomePosition:
    asset: FixedIncomeAssetDTO
    total_applied: Decimal  # Capital aplicado (C)
    first_applied_date: date  # Data do primeiro aporte
    current_value: Decimal = field(init=False)  # Montante (M)
    # Último dia útil cujo rendimento já está em `current_value`
    last_accrual_date: date = field(init=False)

    def __post_init__(self):
        self.current_value = self.total_applied
        self.last_accrual_date = self.first_applied_date

    @property
    def redemption_date(self) -> date:
        return redemption_date(self.asset.maturity_date)

    def invest(self, value: Decimal):
        """
        Aporta mais capital:
        - aumenta o capital aplicado (C)
        - aumenta o montante (M)
        """
        self.total_applied += value
        self.current_value += value

    def accrue(self, day: date):
        """
        Aplica o rendimento do dia útil `day` sobre o montante (M).

        Cada dia rende uma única vez e nada rende depois do resgate, então o tick
        e a reconstrução por eventos podem chamar para o mesmo dia sem somar duas vezes.
        """
        if day <= self.last_accrual_date or day > self.redemption_date:
            return

        # O dia útil anterior ao tick é o que remunerou a noite até `day`
        index_rate = index_daily_rate_on(self.asset.rate_index, self.last_accrual_date)
        self.current_value *= daily_factor(self.asset, index_rate)
        self.last_accrual_date = day

    def net_redemption_value(self) -> Decimal:
        """Valor creditado no resgate, já descontado o IR."""
        days_held = (self.redemption_date - self.first_applied_date).days
        tax_rate = income_tax_rate(self.asset.investment_type, days_held)
        return net_redemption(self.current_value, self.total_applied, tax_rate)
