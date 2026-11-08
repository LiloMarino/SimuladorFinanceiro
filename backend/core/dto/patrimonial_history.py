from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import AssetClass


class PatrimonialHistoryDTO(BaseDTO):
    snapshot_date: date
    total_networth: Decimal
    total_equity: Decimal
    total_fixed: Decimal
    total_cash: Decimal
    total_contribution: Decimal
    total_debt: Decimal = Decimal(0)
    # A renda variável por tipo; nula na leitura que não a carrega
    equity_by_class: dict[AssetClass, Decimal] | None = None


class PortfolioHistoryPointDTO(PatrimonialHistoryDTO):
    # Saldo inicial + aportes até o dia: a linha do "aportado" no gráfico da carteira
    total_provided: Decimal
