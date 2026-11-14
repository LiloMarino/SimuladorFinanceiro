from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.features.funds.fees import management_fee, performance_charge

LISTED = date(2020, 1, 2)


def _charge(
    nav: str,
    *,
    mark: str = "100",
    mark_on: date = LISTED,
    today: date = date(2020, 7, 1),
    cdi_growth: str = "1.05",
    quotas: str = "1000",
    outside: str = "900",
    rate: str = "0.20",
):
    return performance_charge(
        nav=Decimal(nav),
        quotas=Decimal(quotas),
        outside_quotas=Decimal(outside),
        rate=Decimal(rate),
        high_water_mark=Decimal(mark),
        high_water_mark_on=mark_on,
        today=today,
        cdi_growth=Decimal(cdi_growth),
    )


def test_management_fee_excludes_maker_quotas():
    """A taxa de administração incide sobre as cotas fora do formador: 2% ao ano sobre
    R$ 100 x 900 cotas dá R$ 150 no mês, e não R$ 166,66 sobre as 1.000."""
    fee = management_fee(Decimal(100), Decimal(900), Decimal("0.02"))

    assert fee == Decimal("150.00")


def test_management_fee_is_zero_when_everything_is_in_maker_hands():
    """Antes da oferta não há negócio; com todas as cotas no formador a base é zero."""
    assert management_fee(Decimal(100), Decimal(0), Decimal("0.02")) == 0


def test_performance_fee_not_charged_when_quota_falls_and_recovers():
    """A cota cai de R$ 100 para R$ 80 e volta a R$ 100: a linha d'água, corrigida pelo CDI,
    fica acima de R$ 100 e não há taxa; marca e data ficam como estavam."""
    fall = _charge("80")
    assert fall.fee == 0
    assert (fall.high_water_mark, fall.high_water_mark_on) == (Decimal(100), LISTED)

    recovery = _charge("100", today=date(2021, 1, 4), cdi_growth="1.12")

    assert recovery.fee == 0
    assert (recovery.high_water_mark, recovery.high_water_mark_on) == (
        Decimal(100),
        LISTED,
    )


def test_performance_fee_is_rate_on_excess_over_the_line_for_outside_quotas():
    """Com a cota a R$ 130 e a linha a R$ 105, a taxa é 20% do excedente de R$ 25 sobre as
    900 cotas fora do formador: R$ 4.500; a marca d'água passa a ser o PL depois da taxa."""
    result = _charge("130")

    assert result.fee == Decimal("4500.00")
    assert result.high_water_mark == Decimal("130") - Decimal("4500") / 1000
    assert result.high_water_mark_on == date(2020, 7, 1)


def test_performance_fee_ignores_maker_quotas_in_the_base():
    """As cotas do formador não entram na base: a mesma alta rende menos com o formador
    maior."""
    small_maker = _charge("130", outside="900")
    big_maker = _charge("130", outside="500")

    assert big_maker.fee < small_maker.fee
    assert big_maker.fee == Decimal("2500.00")


def test_performance_fee_uses_the_new_mark_next_semester():
    """Depois da cobrança a marca sobe e o semestre seguinte só cobra o que passar dela
    corrigida pelo CDI."""
    first = _charge("130")
    flat = _charge(
        "126.40",
        mark=str(first.high_water_mark),
        mark_on=first.high_water_mark_on,
        today=date(2021, 1, 4),
        cdi_growth="1.06",
    )

    assert first.high_water_mark == Decimal("125.5")
    assert flat.fee == 0
    assert flat.high_water_mark == first.high_water_mark
    assert flat.high_water_mark_on == first.high_water_mark_on
