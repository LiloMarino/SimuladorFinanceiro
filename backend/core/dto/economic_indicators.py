from decimal import Decimal

from backend.core.dto.base import BaseDTO


class EconomicIndicatorsDTO(BaseDTO):
    ipca: Decimal
    selic: Decimal
    cdi: Decimal
    # O juro americano (Fed Funds) ao ano, que rende a conta em dólar
    fed: Decimal
