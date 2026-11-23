"""As regras do Autônomo: a curva de clientes e do mês vazio contra o preço, a faixa do preço e as constantes da política dos bots, em Decimal e sem estado."""

from decimal import ROUND_HALF_EVEN, Decimal
from itertools import pairwise

CENT = Decimal("0.01")

# Os clientes do mês no preço da referência, com o desemprego no neutro
REFERENCE_CLIENTS = Decimal(34)
# A chance do mês sem clientes no preço da referência; a da curva sobre ela escala o sorteio
REFERENCE_EMPTY_MONTH = Decimal("0.02")

# Os pontos da curva acima da referência: (desvio do preço, clientes, chance do mês vazio)
CURVE_POINTS: tuple[tuple[Decimal, Decimal, Decimal], ...] = (
    (Decimal(0), Decimal(34), Decimal("0.02")),
    (Decimal("0.09"), Decimal(32), Decimal("0.03")),
    (Decimal("0.21"), Decimal(27), Decimal("0.06")),
    (Decimal("0.33"), Decimal(21), Decimal("0.11")),
)
# Abaixo da referência o Autônomo ganha um cliente a cada 4% de desconto
CLIENTS_PER_DISCOUNT = Decimal(25)
# A perda de clientes acima da referência se multiplica pelo desemprego sobre o neutro, entre estes limites
MIN_UNEMPLOYMENT_FACTOR = Decimal("0.5")
MAX_UNEMPLOYMENT_FACTOR = Decimal(2)

# A faixa do novo preço, em fração da referência do dia
MIN_PRICE_DEVIATION = Decimal("-0.2")
MAX_PRICE_DEVIATION = Decimal("0.5")
# Os desvios que a tabela do bloco mostra, além da referência
TABLE_DEVIATIONS = (Decimal("0.09"), Decimal("0.21"), Decimal("0.33"))
# A partir deste atraso do preço contra a referência o bloco avisa que a inflação come a renda
STALE_DEVIATION = Decimal("-0.05")

# Política dos bots: o IPCA de 12 meses repassado uma vez por ano, mais este adicional com o desemprego abaixo do neutro
BOT_RAISE_MONTHS = 12
BOT_LOW_UNEMPLOYMENT_RAISE = Decimal("0.05")


def _curve_value(deviation: Decimal, column: int) -> Decimal:
    """O valor da coluna da curva acima da referência: linear entre os pontos e, depois do último, na inclinação do último trecho."""
    points = CURVE_POINTS
    for before, after in pairwise(points):
        if deviation <= after[0]:
            return _interpolate(before, after, deviation, column)
    return _interpolate(points[-2], points[-1], deviation, column)


def _interpolate(
    before: tuple[Decimal, Decimal, Decimal],
    after: tuple[Decimal, Decimal, Decimal],
    deviation: Decimal,
    column: int,
) -> Decimal:
    slope = (after[column] - before[column]) / (after[0] - before[0])
    return before[column] + slope * (deviation - before[0])


def curve_clients(deviation: Decimal) -> Decimal:
    """Os clientes do mês na curva, com o desemprego no neutro; fracionários e nunca negativos."""
    if deviation <= 0:
        return REFERENCE_CLIENTS - deviation * CLIENTS_PER_DISCOUNT
    return max(_curve_value(deviation, 1), Decimal(0))


def empty_month_chance(deviation: Decimal) -> Decimal:
    """A chance do mês sem clientes na curva; a da referência vale do preço da referência para baixo."""
    if deviation <= 0:
        return REFERENCE_EMPTY_MONTH
    return min(_curve_value(deviation, 2), Decimal(1))


def empty_month_weight(deviation: Decimal) -> Decimal:
    """Quantas vezes a chance do mês sem clientes pesa contra a do preço da referência."""
    return empty_month_chance(deviation) / REFERENCE_EMPTY_MONTH


def clients_on(deviation: Decimal, unemployment_ratio: Decimal) -> Decimal:
    """
    Os clientes do mês: a curva, com a perda acima da referência (34 menos os clientes
    da curva) multiplicada pelo desemprego sobre o neutro, de 0,5x a 2x. Abaixo da
    referência o ganho de clientes não depende do desemprego.
    """
    curve = curve_clients(deviation)
    if deviation <= 0:
        return curve
    factor = min(
        max(unemployment_ratio, MIN_UNEMPLOYMENT_FACTOR), MAX_UNEMPLOYMENT_FACTOR
    )
    return max(REFERENCE_CLIENTS - (REFERENCE_CLIENTS - curve) * factor, Decimal(0))


def price_range(reference: Decimal) -> tuple[Decimal, Decimal]:
    """O menor e o maior preço que o Autônomo salva com a referência dada, em centavos."""
    return (
        (reference * (1 + MIN_PRICE_DEVIATION)).quantize(CENT, ROUND_HALF_EVEN),
        (reference * (1 + MAX_PRICE_DEVIATION)).quantize(CENT, ROUND_HALF_EVEN),
    )
