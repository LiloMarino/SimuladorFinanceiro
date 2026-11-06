from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO


class FixedIncomePositionDTO(BaseDTO):
    asset: FixedIncomeAssetDTO
    total_applied: Decimal
    # O montante da curva (o aplicado mais o que rendeu)
    current_value: Decimal
    # O que vale vendido hoje: a curva mais a marcação; só o Tesouro marca
    market_value: Decimal
    # Marcação a mercado: mercado menos curva, positiva ou negativa
    mark: Decimal
    first_applied_date: date
    return_value: Decimal
    return_pct: Decimal
    portfolio_pct: Decimal
    # Líquido que o resgate de hoje manda ao caixa; None em título sem liquidez diária
    redeemable_today: Decimal | None
