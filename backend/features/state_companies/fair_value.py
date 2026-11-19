"""Valor justo da estatal fundada: retorno anual sorteado pela semente em volta de uma média, mais o que o crescimento do PIB acima da tendência soma a cada mês."""

import random
from collections.abc import Sequence
from decimal import Decimal

# A média fica abaixo do juro real histórico por este desconto
MEAN_RETURN_DISCOUNT = Decimal("0.02")

# Desvio-padrão do retorno de cada ano
ANNUAL_VOLATILITY = 0.06

# Pontos de retorno ao ano que cada ponto de crescimento do PIB acima da tendência soma:
# 1 ponto a mais de crescimento rende 2 pontos a mais ao valor justo
GDP_GAIN = 2.0

# Piso do retorno anualizado de um mês: o fator mensal nunca fica sem base real
MIN_MONTH_RATE = -0.99

# Limites do retorno de um ano
MIN_ANNUAL_RETURN = -0.5
MAX_ANNUAL_RETURN = 1.0


def mean_annual_return(real_interest: Decimal) -> Decimal:
    """Média do retorno anual: sempre abaixo do juro real histórico."""
    return real_interest - MEAN_RETURN_DISCOUNT


def annual_return(seed: int, year: int, mean: Decimal) -> float:
    """Retorno do ano: o mesmo (seed, year) dá sempre o mesmo valor."""
    draw = random.Random(f"{seed}:{year}").gauss(float(mean), ANNUAL_VOLATILITY)
    return min(max(draw, MIN_ANNUAL_RETURN), MAX_ANNUAL_RETURN)


def fair_value(
    invested: Decimal,
    seed: int,
    mean: Decimal,
    months: int,
    size_path: Sequence[Decimal] = (),
    growth_path: Sequence[Decimal] = (),
) -> Decimal:
    """
    Valor justo depois de `months` meses: o retorno do ano é diluído em fatores mensais
    iguais, e cada ano usa o seu próprio sorteio. O porte efetivo de cada mês
    (`size_path`, 1 é o porte original) soma ao retorno a média vezes o quanto o porte
    passa de 1: reinvestir cresce o valor mais que o sorteio e apertar o dividendo cresce
    menos. Mês sem porte informado fica no porte original. O crescimento de cada mês
    (`growth_path`, o do PIB menos a tendência, em fração ao ano) soma ao retorno o ganho
    do PIB vezes o excesso: crescer acima da tendência valoriza a empresa e crescer abaixo
    a desvaloriza. Mês sem crescimento informado fica na tendência.
    """
    value = invested
    for month in range(months):
        rate = annual_return(seed, month // 12, mean)
        size = size_path[month] if month < len(size_path) else Decimal(1)
        rate += float(mean) * float(size - 1)
        if month < len(growth_path):
            rate += GDP_GAIN * float(growth_path[month])
        rate = max(rate, MIN_MONTH_RATE)
        value *= Decimal(str((1 + rate) ** (1 / 12)))
    return value


def expected_monthly_profit(value: Decimal, mean: Decimal) -> Decimal:
    """O lucro de um mês sobre o valor justo pelo retorno médio, sem o sorteio da semente."""
    monthly = Decimal(str((1 + float(mean)) ** (1 / 12))) - 1
    return value * monthly
