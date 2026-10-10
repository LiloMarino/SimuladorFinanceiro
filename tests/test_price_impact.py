from __future__ import annotations

from datetime import date

import pytest

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.daily_equity_flow import DailyEquityFlowDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.enum import AssetClass
from backend.features.variable_income.price_impact import (
    MIN_FACTOR,
    PriceImpact,
    decay,
    impact,
)

MONDAY = date(2020, 1, 6)
TUESDAY = date(2020, 1, 7)
FRIDAY = date(2020, 1, 10)
NEXT_MONDAY = date(2020, 1, 13)

AVERAGE_VOLUME = 1_000_000.0
K = 0.02
DECAY_DAYS = 20


@pytest.fixture
def flows(monkeypatch: pytest.MonkeyPatch) -> list[DailyEquityFlowDTO]:
    """Fluxos que o repositório devolve; volume médio fixo em 1 milhão."""
    stored: list[DailyEquityFlowDTO] = []

    def _get_daily_equity_flow(
        simulation_id: int, since: date | None = None, ticker: str | None = None
    ) -> list[DailyEquityFlowDTO]:
        return [
            f
            for f in stored
            if (since is None or f.flow_date >= since)
            and (ticker is None or f.ticker == ticker)
        ]

    monkeypatch.setattr(
        repository.event, "get_daily_equity_flow", _get_daily_equity_flow
    )
    monkeypatch.setattr(
        repository.stock,
        "get_average_volume",
        lambda ticker, until, window: AVERAGE_VOLUME,
    )
    return stored


def _flow(quantity: int, flow_date: date = MONDAY) -> DailyEquityFlowDTO:
    return DailyEquityFlowDTO(ticker="ABCD", flow_date=flow_date, quantity=quantity)


def _candle(price_date: date = TUESDAY) -> CandleDTO:
    return CandleDTO(
        id=1,
        ticker="ABCD",
        name="Abcd",
        asset_class=AssetClass.STOCK,
        open=10.0,
        high=11.0,
        low=9.0,
        close=10.5,
        volume=500,
        price_date=price_date,
        change=0.5,
        change_pct="+5.00%",
    )


def _impact(enabled: bool = True) -> PriceImpact:
    return PriceImpact(1, enabled, K, DECAY_DAYS)


def test_impact_follows_square_root_of_volume_share():
    """10% do volume médio com k = 0,02 desloca 0,632%; venda desloca para baixo."""
    assert impact(100_000, AVERAGE_VOLUME, K) == pytest.approx(0.0063246, rel=1e-4)
    assert impact(-100_000, AVERAGE_VOLUME, K) == pytest.approx(-0.0063246, rel=1e-4)
    assert impact(400_000, AVERAGE_VOLUME, K) == pytest.approx(
        2 * impact(100_000, AVERAGE_VOLUME, K)
    )


def test_impact_without_average_volume_is_zero():
    """Ativo sem volume histórico não tem régua para medir a ordem."""
    assert impact(100, 0, K) == 0.0


@pytest.mark.parametrize(
    ("age", "expected"),
    [(-1, 0.0), (0, 1.0), (10, 0.25), (19, 0.0025), (20, 0.0), (30, 0.0)],
)
def test_decay_reaches_zero_at_decay_days(age: int, expected: float):
    """Cheio no primeiro dia afetado, 25% na metade e zero em T."""
    assert decay(age, DECAY_DAYS) == pytest.approx(expected)


def test_disabled_impact_keeps_history_without_reading_events(
    monkeypatch: pytest.MonkeyPatch,
):
    """Desligado, o candle sai igual e o repositório nem é consultado."""

    def _fail(*args, **kwargs):
        raise AssertionError("repositório consultado com impacto desligado")

    monkeypatch.setattr(repository.event, "get_daily_equity_flow", _fail)
    price_impact = _impact(enabled=False)
    price_impact.refresh(TUESDAY)

    assert price_impact.apply(_candle()) == _candle()


def test_order_moves_only_following_days(flows: list[DailyEquityFlowDTO]):
    """A compra de segunda não mexe na segunda; mexe cheia na terça."""
    flows.append(_flow(100_000))
    price_impact = _impact()

    price_impact.refresh(MONDAY)
    assert price_impact.apply(_candle(MONDAY)).close == 10.5

    price_impact.refresh(TUESDAY)
    assert price_impact.apply(_candle()).close == round(10.5 * 1.0063246, 2)


def test_impact_decays_across_weekend(flows: list[DailyEquityFlowDTO]):
    """Sexta → segunda é um pregão só: segunda ainda recebe o impacto cheio."""
    flows.append(_flow(100_000, FRIDAY))
    price_impact = _impact()
    price_impact.refresh(NEXT_MONDAY)

    assert price_impact.apply(_candle(NEXT_MONDAY)).close == round(10.5 * 1.0063246, 2)


def test_net_zero_day_does_not_move_price(flows: list[DailyEquityFlowDTO]):
    """Quantidade líquida zero (compra e venda iguais) não gera fluxo nem impacto."""
    price_impact = _impact()
    price_impact.refresh(TUESDAY)

    assert price_impact.apply(_candle()) == _candle()


def test_impacts_of_different_days_add_up(flows: list[DailyEquityFlowDTO]):
    """Duas compras em dias seguidos somam os deslocamentos ainda ativos."""
    flows.extend([_flow(100_000, MONDAY), _flow(100_000, TUESDAY)])
    price_impact = _impact()
    price_impact.refresh(date(2020, 1, 8))

    single = impact(100_000, AVERAGE_VOLUME, K)
    expected = 1 + single * decay(1, DECAY_DAYS) + single * decay(0, DECAY_DAYS)
    assert price_impact.apply(_candle()).close == round(10.5 * expected, 2)


def test_factor_never_goes_below_floor(flows: list[DailyEquityFlowDTO]):
    """Venda gigantesca leva o preço ao piso, nunca a zero ou negativo."""
    flows.append(_flow(-(10**13)))
    price_impact = _impact()
    price_impact.refresh(TUESDAY)

    assert price_impact.apply(_candle()).close == round(10.5 * MIN_FACTOR, 2)


def test_apply_scales_ohlc_and_keeps_change_pct(flows: list[DailyEquityFlowDTO]):
    """OHLC e variação absoluta escalam; volume e variação percentual ficam."""
    flows.append(_flow(1_000_000))
    price_impact = _impact()
    price_impact.refresh(TUESDAY)

    candle = price_impact.apply(_candle())

    assert (candle.open, candle.high, candle.low, candle.close) == (
        10.2,
        11.22,
        9.18,
        10.71,
    )
    assert candle.change == 0.51
    assert candle.change_pct == "+5.00%"
    assert candle.volume == 500


def test_history_uses_factor_of_each_day(flows: list[DailyEquityFlowDTO]):
    """Cada dia do histórico mostra o preço com o impacto daquele dia."""
    flows.append(_flow(1_000_000))
    days = [MONDAY, TUESDAY, date(2020, 1, 20)]
    history = [
        StockPriceHistoryDTO(
            price_date=d, open=10.0, high=10.0, low=10.0, close=10.0, volume=1
        )
        for d in days
    ]

    closes = [row.close for row in _impact().apply_history("ABCD", history)]

    # Segunda: a ordem é do próprio dia; terça: +2% cheio; dia 20: idade 9 → 30,25%
    assert closes == [10.0, 10.2, round(10 * (1 + 0.02 * decay(9, DECAY_DAYS)), 2)]
