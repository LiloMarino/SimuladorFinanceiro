# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.core.fund_reference import FundReference
from backend.features.funds.fund_book import FundBook
from backend.features.funds.fund_estimate import IssuanceEstimator
from backend.features.strategy.fair_value_trading import OPINION_RANGE
from tests.test_fund_book import MemoryFunds, isolated, memory
from tests.test_fund_issuance import NAV, QUOTAS, TICKER, _issuable


def estimator(setup, demand: dict[float, int]) -> IssuanceEstimator:
    """Estimador com os bots dados por opinião (cotas que compram) e comissão de 1% sobre o que eles pagam."""
    setup.engine.offer_commission_on = lambda amount: amount * Decimal("0.01")
    return IssuanceEstimator(
        setup.book,
        setup.engine,
        lambda ticker, reference, bias, quotas: Decimal(demand[bias]),
    )


def estimate(setup, demand, photo: Decimal | None, leftover: int = 200):
    fund = setup.book.get(TICKER)
    return estimator(setup, demand).estimate(fund, Decimal(leftover), NAV, photo)


@pytest.fixture(autouse=True)
def flat_performance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        FundBook, "_performance", lambda self, fund, nav, today: Decimal(0)
    )


NO_BOTS = {-OPINION_RANGE: 0, OPINION_RANGE: 0}


def test_the_maker_alone_fills_the_same_amount_at_both_extremes(memory: MemoryFunds):
    """Ágio de 10% (limite de 20%) leva metade da sobra de 200: 100 cotas a R$ 100, sem comissão."""
    result = estimate(_issuable(memory), NO_BOTS, Decimal("110"))

    assert result is not None
    assert (result.quotas_min, result.quotas_max) == (100, 100)
    assert (result.raised_min, result.raised_max) == (10000, 10000)
    assert (result.commission_min, result.commission_max) == (0, 0)
    assert result.premium == pytest.approx(0.10)
    assert result.performance == 0


def test_the_bots_buy_first_and_the_maker_takes_a_fraction_of_what_is_left(
    memory: MemoryFunds,
):
    demand = {-OPINION_RANGE: 30, OPINION_RANGE: 60}

    result = estimate(_issuable(memory), demand, Decimal("110"))

    assert result is not None
    # Mínimo: 30 dos bots + metade dos 170 que sobram; máximo: 60 + metade dos 140
    assert (result.quotas_min, result.quotas_max) == (30 + 85, 60 + 70)
    # Entra no caixa o que os dois pagam menos a comissão de 1% sobre o que os bots pagam
    assert (result.raised_min, result.raised_max) == (11500 - 30, 13000 - 60)
    assert (result.commission_min, result.commission_max) == (30, 60)


def test_the_bots_never_buy_more_than_the_leftover(memory: MemoryFunds):
    demand = {-OPINION_RANGE: 500, OPINION_RANGE: 500}

    result = estimate(_issuable(memory), demand, None)

    assert result is not None
    assert (result.quotas_min, result.quotas_max) == (200, 200)


def test_without_demand_the_range_is_zero_and_says_why(memory: MemoryFunds):
    """Sem foto e com o CDI rendendo igual, a faixa é zero e o desempenho e o ágio explicam."""
    result = estimate(_issuable(memory), NO_BOTS, None)

    assert result is not None
    assert (result.quotas_min, result.quotas_max) == (0, 0)
    assert (result.raised_min, result.raised_max) == (0, 0)
    assert (result.performance, result.premium) == (0.0, 0.0)


def test_no_leftover_has_no_estimate(memory: MemoryFunds):
    assert estimate(_issuable(memory), NO_BOTS, Decimal("110"), leftover=0) is None


def test_the_bots_decide_on_the_last_session_with_the_photo_and_the_extreme_opinions(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    seen: list[tuple[str, FundReference, float, Decimal]] = []

    def demand(ticker: str, reference: FundReference, bias: float, quotas: Decimal):
        seen.append((ticker, reference, bias, quotas))
        return Decimal(0)

    setup.engine.offer_commission_on = lambda amount: Decimal(0)
    IssuanceEstimator(setup.book, setup.engine, demand).estimate(
        setup.book.get(TICKER), Decimal(200), NAV, Decimal("110")
    )

    assert [(t, b, q) for t, _, b, q in seen] == [
        (TICKER, -OPINION_RANGE, QUOTAS),
        (TICKER, OPINION_RANGE, QUOTAS),
    ]
    reference = seen[0][1]
    assert reference.fixed_price == 100.0
    assert reference.fixed_price_last_session
    assert reference.book_price == 110.0
