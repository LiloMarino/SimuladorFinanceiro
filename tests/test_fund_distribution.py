from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.fund import FundDistributionDTO
from backend.features.funds.distribution import (
    drained_since,
    holder_payment,
    paid_since,
    payout_per_quota,
    realized_profit,
    settle_month,
)


def _settle(
    *,
    dividends: str = "0",
    interest: str = "0",
    sales_gain: str = "0",
    fees: str = "0",
    rate: str = "0.95",
    outside: str = "900",
):
    return settle_month(
        dividends=Decimal(dividends),
        interest=Decimal(interest),
        sales_gain=Decimal(sales_gain),
        fees=Decimal(fees),
        rate=Decimal(rate),
        outside_quotas=Decimal(outside),
    )


def _row(paid_per_quota: str | None, paid_on: date | None) -> FundDistributionDTO:
    return FundDistributionDTO(
        data_com=date(2020, 1, 31),
        realized_profit=Decimal(0),
        rate=Decimal("0.95"),
        quotas=Decimal(900),
        per_quota=Decimal(0),
        paid_per_quota=Decimal(paid_per_quota) if paid_per_quota else None,
        paid=None,
        paid_on=paid_on,
    )


def test_realized_profit_sums_the_gains_and_subtracts_the_fees():
    """R$ 600 de dividendos + R$ 300 de juros + R$ 200 de ganho nas vendas - R$ 100 de
    taxas dão R$ 1.000 realizados."""
    profit = realized_profit(Decimal(600), Decimal(300), Decimal(200), Decimal(100))

    assert profit == Decimal(1000)


def test_month_distributes_the_rate_over_the_outside_quotas():
    """95% de R$ 900 de lucro realizado, divididos entre 900 cotas fora do formador, rendem
    R$ 0,95 por cota."""
    result = _settle(dividends="900")

    assert result.realized_profit == Decimal(900)
    assert result.per_quota == Decimal("0.95")


def test_per_quota_is_rounded_down_to_six_places():
    """R$ 100 divididos entre 3 cotas dão R$ 33,333333…: o sexto decimal arredonda para baixo,
    para a soma paga nunca passar do que foi apurado."""
    result = _settle(dividends="100", rate="1", outside="3")

    assert result.per_quota == Decimal("33.333333")


def test_zero_rate_distributes_nothing():
    assert _settle(dividends="900", rate="0").per_quota == 0


def test_losing_month_distributes_nothing_and_keeps_the_loss():
    """Taxas de R$ 100 e nenhum ganho dão lucro de -R$ 100: não rende e o prejuízo fica no mês."""
    result = _settle(fees="100")

    assert result.realized_profit == Decimal(-100)
    assert result.per_quota == 0


def test_month_without_outside_quotas_distributes_nothing():
    """Com todas as cotas no formador não há cotista para receber."""
    assert _settle(dividends="900", outside="0").per_quota == 0


def test_payout_is_the_whole_amount_when_the_cash_covers_it():
    """R$ 0,95 x 900 cotas = R$ 855; com R$ 1.000 em caixa paga tudo."""
    paid = payout_per_quota(Decimal("0.95"), Decimal(900), Decimal(1000))

    assert paid == Decimal("0.95")


def test_payout_is_cash_over_quotas_when_the_cash_falls_short():
    """Devendo R$ 855 com R$ 450 em caixa, cada uma das 900 cotas recebe R$ 0,50."""
    paid = payout_per_quota(Decimal("0.95"), Decimal(900), Decimal(450))

    assert paid == Decimal("0.5")


def test_payout_is_zero_without_cash():
    assert payout_per_quota(Decimal("0.95"), Decimal(900), Decimal(0)) == 0


def test_holder_payment_is_rounded_down_to_the_cent():
    """7 cotas x R$ 0,333333 = R$ 2,333331: o cotista recebe R$ 2,33."""
    assert holder_payment(Decimal(7), Decimal("0.333333")) == Decimal("2.33")


def test_paid_since_sums_only_what_was_paid_after_the_day():
    """Rendimentos pagos depois da marca d'água entram; o pago nela ou antes já estava no PL."""
    rows = [
        _row("1.00", date(2020, 2, 3)),
        _row("0.50", date(2020, 3, 2)),
        _row(None, None),
    ]

    assert paid_since(rows, date(2020, 2, 3)) == Decimal("0.50")
    assert paid_since(rows, date(2020, 1, 1)) == Decimal("1.50")


def test_drained_is_the_cash_paid_over_the_quotas_in_circulation():
    """R$ 900 pagos a cotistas por uma gestora de 1.000 cotas (100 delas do formador, que não
    recebe) tiram R$ 0,90 do PL de cada cota, e não os R$ 1,00 pagos por cota de fora."""
    row = _row("1.00", date(2020, 2, 3)).model_copy(update={"paid": Decimal(900)})

    assert drained_since([row], date(2020, 1, 1), Decimal(1000)) == Decimal("0.9")
    assert drained_since([row], date(2020, 2, 3), Decimal(1000)) == 0
