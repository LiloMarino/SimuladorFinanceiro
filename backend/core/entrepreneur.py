"""As regras do reinvestimento do Empreendedor: o rendimento do capital pelo PIB, a divisão do lucro, a venda com desconto e as constantes da política dos bots, em Decimal e sem estado."""

from collections.abc import Sequence
from decimal import Decimal

from backend.core.clt import cents

# O rendimento do capital ao mês é uma reta pelo zero em cada lado do PIB de 12 meses: com o PIB
# em `GROWTH_UP_REFERENCE` rende `RATE_UP_REFERENCE`; com o PIB em -`GROWTH_DOWN_REFERENCE` rende -`RATE_DOWN_REFERENCE`
GROWTH_UP_REFERENCE = Decimal("0.014")
RATE_UP_REFERENCE = Decimal("0.009")
GROWTH_DOWN_REFERENCE = Decimal("0.012")
RATE_DOWN_REFERENCE = Decimal("0.014")

# A fração reinvestida do lucro vai de 0 a 1, em passos de 1%
REINVEST_STEP = Decimal("0.01")

# As frações do capital que a venda aceita
SALE_SHARES = (Decimal("0.1"), Decimal("0.25"), Decimal("0.5"), Decimal(1))
# Da parte vendida entra no caixa esta fração: o desconto da venda é de 20%
SALE_PROCEEDS_RATE = Decimal("0.8")

# Quantos pagamentos o estado guarda do capital, para o bloco comparar com "há 3 meses"
CAPITAL_HISTORY_MONTHS = 3

# Política dos bots: reinveste com o PIB de 12 meses acima do neutro e vende depois de dois trimestres negativos
BOT_REINVEST_SHARE = Decimal("0.3")
BOT_SELL_SHARE = Decimal("0.25")
BOT_RECESSION_QUARTERS = 2


def capital_rate(growth: Decimal) -> Decimal:
    """A taxa do capital ao mês com o PIB de 12 meses `growth` (fração): positiva com PIB positivo, negativa com PIB negativo e zero no zero."""
    if growth > 0:
        return growth * RATE_UP_REFERENCE / GROWTH_UP_REFERENCE
    return growth * RATE_DOWN_REFERENCE / GROWTH_DOWN_REFERENCE


def capital_income(capital: Decimal, growth: Decimal) -> Decimal:
    """O rendimento do mês sobre o capital do dia, em centavos; negativo quando o PIB está negativo."""
    return cents(capital * capital_rate(growth))


def split_profit(profit: Decimal, share: Decimal) -> tuple[Decimal, Decimal]:
    """O lucro dividido entre a parte que volta para a empresa e a que cai no caixa; as duas somam o lucro."""
    reinvested = cents(profit * share)
    return reinvested, profit - reinvested


def after_payment(
    capital: Decimal, growth: Decimal, profit: Decimal, share: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    """
    O pagamento do mês sobre o capital do dia: o capital depois, a parte do lucro
    reinvestida e o rendimento. Rendimento positivo é renda do caixa; o negativo
    encolhe o capital, que nunca passa de zero para baixo. O lucro reinvestido entra
    no capital depois do rendimento.
    """
    income = capital_income(capital, growth)
    reinvested, _ = split_profit(profit, share)
    shrunk = max(capital + min(income, Decimal(0)), Decimal(0))
    return shrunk + reinvested, reinvested, income


def sale_share_valid(share: Decimal) -> bool:
    return share in SALE_SHARES


def sale_part(capital: Decimal, share: Decimal) -> Decimal:
    """A parte do capital que a venda de `share` tira da empresa, em centavos."""
    return cents(capital * share)


def sale_proceeds(part: Decimal) -> Decimal:
    """O que entra no caixa com a venda da `part` do capital, já com o desconto."""
    return cents(part * SALE_PROCEEDS_RATE)


def negative_quarters(quarters: Sequence[Decimal]) -> int:
    """Quantos trimestres seguidos, do mais recente para trás, fecharam com o PIB de 12 meses negativo; `quarters` vem em ordem de data."""
    count = 0
    for growth in reversed(quarters):
        if growth >= 0:
            break
        count += 1
    return count
