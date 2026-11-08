from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache

import pytest

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.daily_equity_flow import DailyEquityFlowDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.enum import AssetClass
from backend.core.utils import (
    business_days_between,
    next_business_day,
)
from backend.features.variable_income.price_impact import (
    MIN_FACTOR,
    PREVIEW_AVERAGE_VOLUME,
    PREVIEW_VOLUME_SHARE,
    PriceImpact,
    decay,
    impact,
    preview_curve,
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
        "get_average_volumes",
        lambda ticker, days, window, simulation_id=None: dict.fromkeys(
            days, AVERAGE_VOLUME
        ),
    )
    return stored


def _flow(quantity: int, flow_date: date = MONDAY) -> DailyEquityFlowDTO:
    return DailyEquityFlowDTO(
        ticker="ABCD", flow_date=flow_date, quantity=Decimal(quantity)
    )


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
        change_pct=0.05,
    )


def _impact(enabled: bool = True) -> PriceImpact:
    return PriceImpact(1, enabled, K, DECAY_DAYS)


def test_impact_follows_square_root_of_volume_share():
    """10% do volume médio com k = 0,02 desloca 0,632%; venda desloca para baixo."""
    assert impact(Decimal(100_000), AVERAGE_VOLUME, K) == pytest.approx(
        0.0063246, rel=1e-4
    )
    assert impact(Decimal(-100_000), AVERAGE_VOLUME, K) == pytest.approx(
        -0.0063246, rel=1e-4
    )
    assert impact(Decimal(400_000), AVERAGE_VOLUME, K) == pytest.approx(
        2 * impact(Decimal(100_000), AVERAGE_VOLUME, K)
    )


def test_impact_without_average_volume_is_zero():
    """Ativo sem volume histórico não tem régua para medir a ordem."""
    assert impact(Decimal(100), 0, K) == 0.0


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

    single = impact(Decimal(100_000), AVERAGE_VOLUME, K)
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
    assert candle.change_pct == 0.05
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


class Market:
    """O efeito das medidas de gasto na bolsa: o nível do mercado elevado ao beta de cada ativo."""

    def __init__(self, factor: float):
        self.factor = factor

    def adjust(self, series, history):
        return history

    def stock_factor(self, ticker: str, day: date) -> float:
        return self.factor if ticker == "ABCD" else 1.0


@pytest.fixture
def market_effect(monkeypatch: pytest.MonkeyPatch):
    def use(factor: float) -> None:
        monkeypatch.setattr(repository.economic, "_adjustments", {1: Market(factor)})

    return use


def test_the_government_effect_moves_the_candle_even_with_the_impact_off(
    market_effect,
):
    market_effect(0.97)
    price_impact = _impact(enabled=False)
    price_impact.refresh(TUESDAY)

    candle = price_impact.apply(_candle())

    assert candle.close == round(10.5 * 0.97, 2)
    assert candle.open == round(10.0 * 0.97, 2)


def test_the_government_effect_multiplies_the_factor_of_the_orders(
    flows: list[DailyEquityFlowDTO], market_effect
):
    flows.append(_flow(100_000))
    market_effect(0.9)
    price_impact = _impact()

    orders_only = price_impact._factor_on(flows, TUESDAY)

    assert price_impact.factors_on("ABCD", [TUESDAY])[TUESDAY] == pytest.approx(
        orders_only * 0.9
    )
    # O ativo sem efeito de mercado fica só com o das ordens
    assert price_impact.factors_on("OTHER", [TUESDAY])[TUESDAY] == 1.0


def test_the_history_carries_the_government_effect_of_each_day(market_effect):
    market_effect(0.95)
    row = StockPriceHistoryDTO(
        price_date=TUESDAY,
        open=10.0,
        high=11.0,
        low=9.0,
        close=10.5,
        volume=500,
    )

    [scaled] = _impact(enabled=False).apply_history("ABCD", [row])

    assert scaled.close == round(10.5 * 0.95, 2)


def _full_factor(flows: list[DailyEquityFlowDTO], on: date) -> float:
    """O fator refeito de todos os fluxos da partida, um por um."""
    total = 0.0
    for flow in flows:
        remaining = decay(business_days_between(flow.flow_date, on) - 1, DECAY_DAYS)
        if remaining > 0:
            total += impact(flow.quantity, AVERAGE_VOLUME, K) * remaining
    return max(1 + total, MIN_FACTOR)


def _match_flows(days: int) -> list[DailyEquityFlowDTO]:
    """Compras e vendas de tamanhos variados em quase todo pregão, com alguns dias sem ordem."""
    flows = []
    day = MONDAY
    for n in range(days):
        if n % 7 != 3:
            quantity = (n * 7919) % 200_000 - 90_000
            flows.append(_flow(quantity or 1, day))
        day = next_business_day(day)
    return flows


def test_the_window_of_each_day_matches_the_full_recalculation(
    flows: list[DailyEquityFlowDTO], monkeypatch: pytest.MonkeyPatch
):
    """Dia a dia, como o motor: o fator da janela é o mesmo de refazer tudo, e cada dia é lido do banco uma vez."""
    match = _match_flows(300)
    price_impact = _impact()
    reads = 0
    stored_flows = repository.event.get_daily_equity_flow

    def _counted(simulation_id, since=None, ticker=None):
        nonlocal reads
        reads += ticker is not None
        return stored_flows(simulation_id, since, ticker)

    monkeypatch.setattr(repository.event, "get_daily_equity_flow", _counted)
    # As janelas se sobrepõem: o recálculo completo de cada dia é feito uma vez só
    expected = cache(lambda on: _full_factor(match, on))

    # Retomada no meio da partida: a primeira janela pega dias de antes do primeiro refresh
    played = [f.flow_date for f in match[:85]]
    day = next_business_day(played[-1])
    while day <= match[-1].flow_date:
        flows[:] = [f for f in match if f.flow_date < day]
        price_impact.refresh(day)
        played.append(day)
        window = played[-60:]

        factors = price_impact.factors_on("ABCD", window)

        assert factors == {d: expected(d) for d in window}
        day = next_business_day(day)

    assert reads == 1


def test_days_before_the_first_refresh_come_from_the_events(
    flows: list[DailyEquityFlowDTO],
):
    """Um histórico inteiro pedido de uma vez bate com o recálculo completo em todo dia."""
    flows.extend(_match_flows(300))
    days = [f.flow_date for f in flows] + [next_business_day(flows[-1].flow_date)]

    factors = _impact().factors_on("ABCD", days)

    assert factors == {d: _full_factor(flows, d) for d in days}


def test_preview_curve_follows_the_impact_and_decay_of_a_ten_percent_buy():
    first_day = impact(
        Decimal(round(PREVIEW_VOLUME_SHARE * PREVIEW_AVERAGE_VOLUME)),
        PREVIEW_AVERAGE_VOLUME,
        K,
    )

    curve = preview_curve(K, DECAY_DAYS)

    assert curve == [
        first_day * decay(age, DECAY_DAYS) for age in range(DECAY_DAYS + 1)
    ]
    assert curve[0] == first_day
    assert curve[-1] == 0
