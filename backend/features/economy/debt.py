"""A dinâmica da dívida pública: o primário que a mantém parada contra o juro e o crescimento."""

from decimal import Decimal


def nominal_growth(real_growth: Decimal, inflation: Decimal) -> Decimal:
    """O crescimento do PIB em reais correntes, em fração ao ano: o real composto com a inflação."""
    return (1 + real_growth) * (1 + inflation) - 1


def stabilizing_primary(
    debt: Decimal, rate: Decimal, nominal_growth: Decimal
) -> Decimal:
    """
    O resultado primário, em fração do PIB ao ano, que mantém a dívida ÷ PIB onde está:
    s = d * (r - g) / (1 + g), com `rate` a taxa média que a dívida paga e `nominal_growth`
    o crescimento do PIB em reais correntes. Negativo é déficit que ainda deixa a dívida parada.
    """
    return debt * (rate - nominal_growth) / (1 + nominal_growth)
