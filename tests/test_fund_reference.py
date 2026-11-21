"""A referência da cota: o prêmio do desempenho, o ágio da foto e a fração da sobra que o Mercado compra."""

from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.fund_reference import (
    FundReference,
    maker_attractiveness,
    maker_leftover,
    performance_premium,
)


def reference(
    performance: float = 0.0, book_price: float | None = None
) -> FundReference:
    return FundReference(100.0, performance, 100.0, True, book_price)


def test_performance_premium_is_twice_the_performance_limited_to_twenty_percent():
    assert performance_premium(0.03) == pytest.approx(0.06)
    assert performance_premium(0.50) == 0.20
    assert performance_premium(-0.50) == -0.20


def test_premium_is_the_photo_over_the_nav_minus_one():
    assert reference(book_price=110.0).premium == pytest.approx(0.10)
    assert reference(book_price=90.0).premium == pytest.approx(-0.10)


def test_a_quota_without_photo_has_no_premium():
    assert reference().premium == 0.0


def test_attractiveness_is_the_larger_of_the_performance_premium_and_the_premium():
    # Desempenho de 3 pontos dá 6%; o ágio de 10% é maior
    assert maker_attractiveness(reference(0.03, 110.0)) == pytest.approx(0.10)
    # Desempenho de 8 pontos dá 16%; o ágio de 10% é menor
    assert maker_attractiveness(reference(0.08, 110.0)) == pytest.approx(0.16)
    # Sem foto o ágio é zero: o prêmio negativo do desempenho não puxa a atratividade para baixo
    assert maker_attractiveness(reference(-0.02)) == 0.0
    # Com deságio e desempenho abaixo do CDI, a atratividade fica negativa
    assert maker_attractiveness(reference(-0.02, 95.0)) == pytest.approx(-0.04)


def test_the_maker_takes_attractiveness_over_the_limit_of_the_leftover():
    # 10% de atratividade, sobre o limite de 20%, leva metade da sobra
    assert maker_leftover(Decimal(200), 0.10) == 100
    assert maker_leftover(Decimal(200), 0.05) == 50


def test_the_maker_takes_whole_quotas_rounded_down():
    assert maker_leftover(Decimal(7), 0.10) == 3


def test_the_maker_takes_at_most_the_whole_leftover():
    assert maker_leftover(Decimal(200), 0.20) == 200
    assert maker_leftover(Decimal(200), 0.50) == 200


@pytest.mark.parametrize("attractiveness", [0.0, -0.04])
def test_the_maker_does_not_buy_without_positive_attractiveness(attractiveness):
    assert maker_leftover(Decimal(200), attractiveness) == 0
