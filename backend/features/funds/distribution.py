from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

from backend.core.dto.fund import FundDistributionDTO

CENT = Decimal("0.01")
PER_QUOTA_STEP = Decimal("0.000001")


@dataclass(frozen=True)
class MonthSettlement:
    """O fechamento do mês na data-com: o lucro realizado e o que ele rende por cota."""

    realized_profit: Decimal
    per_quota: Decimal


def realized_profit(
    dividends: Decimal, interest: Decimal, sales_gain: Decimal, fees: Decimal
) -> Decimal:
    """O lucro realizado do mês: dividendos + juros da renda fixa + ganho nas vendas - taxas pagas.

    A valorização do que segue na carteira fica na cota e não entra aqui.
    """
    return dividends + interest + sales_gain - fees


def settle_month(
    *,
    dividends: Decimal,
    interest: Decimal,
    sales_gain: Decimal,
    fees: Decimal,
    rate: Decimal,
    outside_quotas: Decimal,
) -> MonthSettlement:
    """O rendimento do mês por cota: `parte distribuída x lucro realizado / cotas fora do formador`.

    Mês sem lucro realizado (zero ou negativo) não distribui e o prejuízo não passa para o
    mês seguinte. O formador de mercado não recebe: a divisão é só entre as cotas de fora.
    """
    profit = realized_profit(dividends, interest, sales_gain, fees)
    if profit <= 0 or outside_quotas <= 0:
        return MonthSettlement(profit, Decimal(0))
    per_quota = (rate * profit / outside_quotas).quantize(PER_QUOTA_STEP, ROUND_DOWN)
    return MonthSettlement(profit, per_quota)


def payout_per_quota(
    per_quota: Decimal, outside_quotas: Decimal, cash: Decimal
) -> Decimal:
    """O que é pago por cota: o apurado, ou o caixa dividido pelas cotas quando o caixa não cobre.

    A diferença que o caixa não cobriu não é devida em meses futuros.
    """
    if per_quota <= 0 or outside_quotas <= 0 or cash <= 0:
        return Decimal(0)
    owed = per_quota * outside_quotas
    if cash >= owed:
        return per_quota
    return (cash / outside_quotas).quantize(PER_QUOTA_STEP, ROUND_DOWN)


def holder_payment(quotas: Decimal, paid_per_quota: Decimal) -> Decimal:
    """O rendimento de um cotista em reais, arredondado para baixo no centavo."""
    return (quotas * paid_per_quota).quantize(CENT, ROUND_DOWN)


def paid_since(distributions: Iterable[FundDistributionDTO], day: date) -> Decimal:
    """O rendimento por cota pago depois de `day`: a parte do retorno total que já saiu da cota."""
    return sum(
        (
            d.paid_per_quota
            for d in distributions
            if d.paid_per_quota is not None
            and d.paid_on is not None
            and d.paid_on > day
        ),
        Decimal(0),
    )


def drained_since(
    distributions: Iterable[FundDistributionDTO], day: date, quotas: Decimal
) -> Decimal:
    """O que saiu do caixa em rendimentos depois de `day`, por cota em circulação.

    É a queda que o pagamento causou no PL por cota: o formador não recebe, então a queda é
    menor que o rendimento pago por cota quando ele tem cotas.
    """
    if quotas <= 0:
        return Decimal(0)
    paid = sum(
        (
            d.paid
            for d in distributions
            if d.paid is not None and d.paid_on is not None and d.paid_on > day
        ),
        Decimal(0),
    )
    return paid / quotas
