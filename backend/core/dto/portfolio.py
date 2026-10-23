from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.position import PortfolioPositionDTO
from backend.core.dto.sector import SectorAllocationDTO


class PortfolioDTO(BaseDTO):
    starting_cash: Decimal
    cash: Decimal
    total_networth: Decimal
    invested_value: Decimal
    variable_income_value: Decimal
    fixed_income_value: Decimal
    # Frações (0.25 = 25%): investido sobre os ativos; RV e RF sobre o investido
    invested_pct: Decimal
    variable_income_pct: Decimal
    fixed_income_pct: Decimal
    # Retorno sobre o capital aportado (caixa inicial + aportes mensais)
    capital_provided: Decimal
    total_return_value: Decimal
    total_return_pct: Decimal
    # Frações dos ativos em renda variável, renda fixa e caixa (somam 1)
    variable_income_networth_pct: Decimal
    fixed_income_networth_pct: Decimal
    cash_pct: Decimal
    # Patrimônio é sempre o líquido: caixa, ações e renda fixa menos a dívida
    assets_value: Decimal
    debt: Decimal
    # Parcela em atraso ou prestes a vencer sem caixa para cobri-la
    credit_alert: bool
    # IR da renda variável: o que já saiu do caixa e o apurado que ainda vai sair
    income_tax_paid: Decimal
    income_tax_due: Decimal
    # Vencimento do próximo DARF ainda não pago
    income_tax_due_date: date | None
    # Vendas de ações no mês da simulação e o teto da isenção mensal
    month_stock_sales: Decimal
    stock_sales_exemption: Decimal
    variable_income: list[PortfolioPositionDTO]
    # Renda variável por setor e segmento; as frações são sobre a renda variável
    sectors: list[SectorAllocationDTO]
    # Número efetivo de setores (1 ÷ Σ fração²); sem ações, não existe
    effective_sectors: Decimal | None
    fixed_income: list[FixedIncomePositionDTO]
