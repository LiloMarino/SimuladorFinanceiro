"""
A política do consignado do Servidor-bot: contrata quando o Ibovespa cai fundo e quita
quando ele volta perto do topo. Só funções do que o bot vê, sem o motor.
"""

from decimal import Decimal
from enum import Enum

from backend.features.credit.price import affordable_principal

# O Ibovespa 20% ou mais abaixo do topo dos últimos 12 meses abre a compra
TAKE_DRAWDOWN = Decimal("0.20")
# De volta a menos de 5% abaixo do topo, o consignado é quitado
PAY_OFF_DRAWDOWN = Decimal("0.05")
PAYROLL_TERM_MONTHS = 24
# A parcela do consignado novo é esta fração da margem livre
MARGIN_SHARE = Decimal("0.5")


class PayrollMove(Enum):
    TAKE = "TAKE"
    PAY_OFF = "PAY_OFF"


def payroll_policy(drawdown: Decimal | None, has_payroll: bool) -> PayrollMove | None:
    """
    Contrata quando não há consignado e o Ibovespa está `TAKE_DRAWDOWN` ou mais abaixo do
    topo de 12 meses; quita quando há consignado e ele voltou a menos de
    `PAY_OFF_DRAWDOWN` abaixo do topo. `drawdown` é a fração abaixo do topo (nula sem série).
    """
    if drawdown is None:
        return None
    if has_payroll:
        return PayrollMove.PAY_OFF if drawdown < PAY_OFF_DRAWDOWN else None
    return PayrollMove.TAKE if drawdown >= TAKE_DRAWDOWN else None


def payroll_amount(free_margin: Decimal, annual_rate: Decimal) -> Decimal:
    """O valor do consignado novo: o que a parcela de `MARGIN_SHARE` da margem livre sustenta em `PAYROLL_TERM_MONTHS`."""
    return affordable_principal(
        free_margin * MARGIN_SHARE, annual_rate, PAYROLL_TERM_MONTHS
    )
