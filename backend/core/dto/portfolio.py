from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.position import PortfolioPositionDTO


class PortfolioDTO(BaseDTO):
    starting_cash: Decimal
    cash: Decimal
    total_networth: Decimal
    invested_value: Decimal
    variable_income_value: Decimal
    fixed_income_value: Decimal
    # Frações (0.25 = 25%): investido sobre o patrimônio; RV e RF sobre o investido
    invested_pct: Decimal
    variable_income_pct: Decimal
    fixed_income_pct: Decimal
    # Retorno sobre o capital aportado (caixa inicial + aportes mensais)
    total_return_pct: Decimal
    # IR da renda variável: o que já saiu do caixa e o apurado que ainda vai sair
    income_tax_paid: Decimal
    income_tax_due: Decimal
    variable_income: list[PortfolioPositionDTO]
    fixed_income: list[FixedIncomePositionDTO]
