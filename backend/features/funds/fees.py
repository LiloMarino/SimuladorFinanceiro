from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

CENT = Decimal("0.01")
MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class PerformanceCharge:
    """A cobrança de um semestre e a marca d'água que vale depois dela."""

    fee: Decimal
    high_water_mark: Decimal
    high_water_mark_on: date


def management_fee(
    nav: Decimal, outside_quotas: Decimal, annual_rate: Decimal
) -> Decimal:
    """A taxa de administração de um mês: `taxa anual / 12 x PL por cota x cotas fora do
    formador`. As cotas do formador foram pagas com dinheiro sintético e não rendem taxa."""
    fee = annual_rate / MONTHS_PER_YEAR * nav * outside_quotas
    return fee.quantize(CENT, ROUND_DOWN)


def split_payable(fee: Decimal, cash: Decimal) -> tuple[Decimal, Decimal]:
    """A taxa dividida em (paga, a pagar): o caixa positivo cobre o que alcança e o resto fica devido."""
    paid = min(fee, max(cash, Decimal(0)))
    return paid, fee - paid


def performance_charge(
    *,
    nav: Decimal,
    quotas: Decimal,
    outside_quotas: Decimal,
    rate: Decimal,
    high_water_mark: Decimal,
    high_water_mark_on: date,
    today: date,
    cdi_growth: Decimal,
    drained_per_quota: Decimal = Decimal(0),
) -> PerformanceCharge:
    """A taxa de performance de um semestre, sobre o que passou do CDI.

    A medida é o retorno total por cota: o PL por cota mais o que os rendimentos tiraram da
    cota desde a data da marca (`drained_per_quota`). Distribuir lucro tira dinheiro da cota e
    o põe no bolso do cotista, e a soma dos dois não muda, então distribuir mais ou menos não
    muda a taxa. A linha d'água é a marca d'água corrigida pelo CDI acumulado desde a data dela
    (`cdi_growth`, o fator: 1,05 é 5% acumulados). A taxa é `taxa x max(0, retorno total -
    linha) x cotas fora do formador`. Com cobrança, a marca d'água passa a ser o retorno
    total por cota depois da taxa (que sai do patrimônio das `quotas` em circulação) e a data
    dela, hoje; sem cobrança, marca e data ficam como estavam.
    """
    total = nav + drained_per_quota
    line = high_water_mark * cdi_growth
    fee = (rate * max(Decimal(0), total - line) * outside_quotas).quantize(
        CENT, ROUND_DOWN
    )
    if fee <= 0:
        return PerformanceCharge(Decimal(0), high_water_mark, high_water_mark_on)
    return PerformanceCharge(fee, total - fee / quotas, today)
