from decimal import Decimal

from backend.core.rates import Percent, compose, compound, from_percent, period_rate


def test_compound_grows_the_rate_by_the_number_of_periods() -> None:
    assert compound(Decimal("0.10"), 2) == Decimal("0.21")


def test_compound_accepts_a_fraction_of_a_period() -> None:
    assert compound(Decimal("0.44"), Decimal("0.5")) == Decimal("0.2")


def test_period_rate_undoes_compound() -> None:
    monthly = period_rate(Decimal("0.12"), 12)

    assert abs(compound(monthly, 12) - Decimal("0.12")) < Decimal("1e-20")


def test_compose_chains_the_rates_one_after_the_other() -> None:
    assert compose(Decimal("0.03"), Decimal("0.05")) == Decimal("0.0815")


def test_compose_of_nothing_is_zero() -> None:
    assert compose() == 0


def test_from_percent_turns_the_published_value_into_a_fraction() -> None:
    assert from_percent(Percent(Decimal("0.0551"))) == Decimal("0.000551")
