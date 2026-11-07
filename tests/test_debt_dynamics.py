"""A dinâmica da dívida: o primário que a mantém parada."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.features.economy.debt import nominal_growth, stabilizing_primary
from backend.features.government.budget import step


def test_nominal_growth_compounds_the_real_growth_with_the_inflation() -> None:
    # 3% reais com 5% de inflação: 1,03 * 1,05 - 1 = 8,15%
    assert nominal_growth(Decimal("0.03"), Decimal("0.05")) == Decimal("0.0815")


def test_debt_of_eighty_percent_with_rate_above_growth_asks_for_a_surplus() -> None:
    # Dívida de 80% do PIB, taxa de 12% e PIB nominal crescendo 8%: 0,8 * 0,04 / 1,08
    primary = stabilizing_primary(Decimal("0.8"), Decimal("0.12"), Decimal("0.08"))

    assert primary == pytest.approx(Decimal("0.02963"), abs=Decimal("0.00001"))


def test_growth_above_the_rate_lets_the_debt_hold_with_a_deficit() -> None:
    primary = stabilizing_primary(Decimal("0.8"), Decimal("0.06"), Decimal("0.09"))

    assert primary < 0


def test_no_debt_needs_no_primary() -> None:
    assert stabilizing_primary(Decimal(0), Decimal("0.12"), Decimal("0.02")) == 0


def test_the_monthly_budget_holds_the_debt_with_the_stabilizing_primary() -> None:
    debt, rate = Decimal("0.8"), Decimal("0.12")
    real, inflation = Decimal("0.02"), Decimal("0.06")
    primary = stabilizing_primary(debt, rate, nominal_growth(real, inflation))

    after, _ = step(debt, rate, inflation, real, primary)

    # O mês compõe em 1/12 de ano e a fórmula é anual: a diferença é de segunda ordem
    assert after == pytest.approx(debt, abs=Decimal("0.0001"))
