"""As cotações do dia que marcam a renda fixa a mercado."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class FixedIncomeQuotes:
    """
    O que o mercado diz hoje sobre a renda fixa: o prêmio de risco do país, que marca o
    Tesouro Prefixado e IPCA+, e o dólar em reais, que marca a conta em dólar.
    """

    premium: Decimal = Decimal(0)
    dollar: Decimal = Decimal(1)


# Sem prêmio e com o dólar a R$ 1: o título vale a curva
NO_QUOTES = FixedIncomeQuotes()
