"""Somas do caixa e da renda fixa de um jogador que explicam de onde veio o retorno."""

from decimal import Decimal

from backend.core.dto.base import BaseDTO


class ReturnFlowsDTO(BaseDTO):
    """Totais da partida até o último snapshot; todo valor é positivo, o sentido vem do nome."""

    dividends: Decimal = Decimal(0)
    overdraft_interest: Decimal = Decimal(0)
    loan_proceeds: Decimal = Decimal(0)
    loan_payment: Decimal = Decimal(0)
    campaign: Decimal = Decimal(0)
    # Renda fixa: aplicado, resgatado (bruto) e retido de IR e IOF nos resgates
    fixed_bought: Decimal = Decimal(0)
    fixed_redeemed: Decimal = Decimal(0)
    fixed_tax_withheld: Decimal = Decimal(0)
