"""Conta em dólar: rende o juro do Fed em US$, vale o saldo ao dólar de hoje e paga IR de 15% sobre o ganho em reais."""

from __future__ import annotations

import threading
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import (
    FixedIncomeEventType,
    FixedIncomeType,
    IndicatorSeries,
    RateIndexType,
)
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import (
    annual_to_daily_factor,
    daily_factor,
    offer,
)
from backend.features.fixed_income.fixed_broker import FixedBroker, load_fixed_assets
from backend.features.fixed_income.quotes import FixedIncomeQuotes
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.conftest import SetIndicator
from tests.fakes import FakeSimulationEngine, client, daily_series

INVESTOR = client("investor")
START = date(2020, 1, 6)  # segunda-feira
ASSET_ID = 7
CENT = Decimal("0.01")
IOF = DEFAULT_TAX_POLICY.fx_iof_rate


@pytest.fixture(autouse=True)
def fed(indicators: SetIndicator) -> None:
    """Juro do Fed a 5% ao ano, constante."""
    indicators(
        IndicatorSeries.FED_FUNDS,
        daily_series(date(2019, 1, 1), date(2025, 1, 1), "5"),
    )


@pytest.fixture(autouse=True)
def fixed_income_db(
    monkeypatch: pytest.MonkeyPatch, captured_events: list[BaseEventDTO]
) -> None:
    monkeypatch.setattr(
        repository.fixed_income, "get_events", lambda simulation_id, user_id: []
    )
    monkeypatch.setattr(
        repository.fixed_income,
        "get_or_create_asset",
        lambda simulation_id, asset: ASSET_ID,
    )


def dollar_account(percent: str = "1") -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        name="Conta em dólar",
        issuer="Banco Teste",
        investment_type=FixedIncomeType.DOLLAR_ACCOUNT,
        rate_index=RateIndexType.FED_FUNDS,
        maturity_date=date(2030, 1, 7),
        interest_rate=Decimal(percent),
        daily_liquidity=True,
    )


class Dollar:
    """O dólar do dia que o teste move à mão."""

    def __init__(self, value: str):
        self.value = Decimal(value)

    def __call__(self, _day: date) -> Decimal:
        return self.value


def broker_with(
    dollar: str = "5.00", cash: str = "100000"
) -> tuple[FixedBroker, FakeSimulationEngine, Dollar]:
    engine = FakeSimulationEngine(cash={INVESTOR: Decimal(cash)}, current_date=START)
    price = Dollar(dollar)
    engine.use_dollar_history(price)
    return FixedBroker(engine, threading.RLock()), engine, price


def move_dollar(engine: FakeSimulationEngine, price: Dollar, value: str) -> None:
    price.value = Decimal(value)
    engine.use_dollar_history(price)


def tick(broker: FixedBroker, engine: FakeSimulationEngine, days: int) -> None:
    for _ in range(days):
        engine.current_date = next_business_day(engine.current_date)
        broker.apply_daily_interest(engine.current_date)


def fixed_events(events: list[BaseEventDTO]) -> list[FixedIncomeEventDTO]:
    return [e for e in events if isinstance(e, FixedIncomeEventDTO)]


def held(broker: FixedBroker, asset: FixedIncomeAssetDTO):
    return broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]


def test_daily_factor_is_the_fed_rate_in_a_business_day():
    """5% ao ano a 100% do Fed rende (1,05)^(1/252) por dia útil."""
    index_rate = annual_to_daily_factor(Decimal("0.05")) - 1

    factor = daily_factor(dollar_account(), index_rate)

    assert factor == pytest.approx(annual_to_daily_factor(Decimal("0.05")))


def test_buy_converts_the_reais_net_of_iof_at_the_dollar_of_the_day(captured_events):
    """R$ 10.000 a R$ 5,00 com IOF de 1,1% viram US$ 1.978,00; o evento guarda os reais e o dólar."""
    broker, engine, _ = broker_with("5.00")
    asset = dollar_account()

    broker.buy(INVESTOR, asset, Decimal(10000))

    position = held(broker, asset)
    assert position.current_value == Decimal(10000) * (1 - IOF) / Decimal(5)
    assert position.current_value.quantize(CENT) == Decimal("1978.00")
    assert position.total_applied == Decimal(10000)
    assert engine.cash[INVESTOR] == Decimal(90000)
    [event] = fixed_events(captured_events)
    assert event.event_type is FixedIncomeEventType.BUY
    assert event.amount == Decimal(10000)
    assert event.fx_rate == Decimal("5.00")


def test_a_higher_dollar_raises_the_value_in_reais_by_the_same_share():
    """O saldo em US$ não muda: com o dólar a R$ 5,50 (10% acima) o valor em reais sobe 10%."""
    broker, engine, price = broker_with("5.00")
    asset = dollar_account()
    broker.buy(INVESTOR, asset, Decimal(10000))
    position = held(broker, asset)
    before = position.market_value(engine.current_date, engine.fixed_quotes())

    move_dollar(engine, price, "5.50")

    after = position.market_value(engine.current_date, engine.fixed_quotes())
    assert after / before == pytest.approx(Decimal("1.10"))
    assert position.current_value.quantize(CENT) == Decimal("1978.00")


def test_the_balance_in_dollars_earns_the_fed_every_business_day():
    """Em 20 dias úteis a 5% ao ano o saldo em US$ rende (1,05)^(20/252)."""
    broker, engine, _ = broker_with("5.00")
    asset = dollar_account()
    broker.buy(INVESTOR, asset, Decimal(10000))
    initial = held(broker, asset).current_value

    tick(broker, engine, 20)

    grown = held(broker, asset).current_value / initial
    assert float(grown) == pytest.approx(1.05 ** (20 / 252), rel=1e-9)


def test_redemption_withholds_15_percent_of_the_gain_in_reais(captured_events):
    """Dólar de R$ 5,00 a R$ 5,50: o ganho em reais paga 15% e o resto cai no caixa, sem IOF."""
    broker, engine, price = broker_with("5.00")
    asset = dollar_account()
    broker.buy(INVESTOR, asset, Decimal(10000))
    move_dollar(engine, price, "5.50")
    position = held(broker, asset)
    reais = position.current_value * Decimal("5.50")
    gain = reais - Decimal(10000)
    cash = engine.cash[INVESTOR]

    net = position.breakdown(
        engine.current_date, None, quotes=engine.fixed_quotes()
    ).net
    broker.redeem(INVESTOR, asset, net)

    assert net == pytest.approx(reais - gain * Decimal("0.15"), abs=CENT)
    assert engine.cash[INVESTOR] - cash == pytest.approx(net, abs=CENT)
    assert asset.asset_uuid not in broker.get_fixed_positions(INVESTOR)
    [_, redeem] = fixed_events(captured_events)
    assert redeem.event_type is FixedIncomeEventType.REDEEM
    assert redeem.tax_withheld == pytest.approx(gain * Decimal("0.15"), abs=CENT)
    assert redeem.fx_rate == Decimal("5.50")


def test_redemption_below_the_applied_pays_no_income_tax(captured_events):
    """Com o dólar a R$ 4,50 o saldo vale menos que os R$ 10.000 aplicados: sem ganho, sem IR."""
    broker, engine, price = broker_with("5.00")
    asset = dollar_account()
    broker.buy(INVESTOR, asset, Decimal(10000))
    move_dollar(engine, price, "4.50")
    position = held(broker, asset)

    breakdown = position.breakdown(
        engine.current_date, None, quotes=engine.fixed_quotes()
    )
    broker.redeem(INVESTOR, asset, breakdown.net)

    assert breakdown.net == breakdown.gross
    assert fixed_events(captured_events)[-1].tax_withheld == 0


def test_partial_redemption_takes_the_proportional_dollars(captured_events):
    """O resgate parcial tira do saldo os US$ do bruto (bruto em reais ÷ dólar) e o aplicado cai na mesma proporção."""
    broker, engine, price = broker_with("5.00")
    asset = dollar_account()
    broker.buy(INVESTOR, asset, Decimal(10000))
    move_dollar(engine, price, "5.50")
    position = held(broker, asset)
    dollars, applied = position.current_value, position.total_applied
    quotes = engine.fixed_quotes()
    breakdown = position.breakdown(engine.current_date, Decimal(3000), quotes=quotes)

    broker.redeem(INVESTOR, asset, Decimal(3000))

    after = held(broker, asset)
    taken = breakdown.gross / Decimal("5.50")
    assert after.current_value == pytest.approx(dollars - taken, abs=Decimal("1e-9"))
    assert after.total_applied == pytest.approx(
        applied * (1 - taken / dollars), abs=Decimal("1e-9")
    )
    redeem = fixed_events(captured_events)[-1]
    assert redeem.amount == taken.quantize(Decimal("0.000001"))
    assert redeem.fx_rate == Decimal("5.50")


def test_rebuilding_from_the_events_matches_the_live_game(
    captured_events, monkeypatch: pytest.MonkeyPatch
):
    """Compra, resgate parcial e nova compra com o dólar mudando: os eventos com `fx_rate` refazem a posição ao centavo."""
    broker, engine, price = broker_with("5.00")
    asset = dollar_account()

    broker.buy(INVESTOR, asset, Decimal(10000))
    tick(broker, engine, 30)
    move_dollar(engine, price, "5.40")
    broker.redeem(INVESTOR, asset, Decimal(2000))
    tick(broker, engine, 15)
    move_dollar(engine, price, "5.10")
    broker.buy(INVESTOR, asset, Decimal(4000))
    tick(broker, engine, 10)

    live = held(broker, asset)
    monkeypatch.setattr(
        repository.fixed_income,
        "get_events",
        lambda simulation_id, user_id: [
            (asset, e) for e in fixed_events(captured_events)
        ],
    )
    rebuilt = load_fixed_assets(1, INVESTOR, engine.current_date)[asset.asset_uuid]

    assert rebuilt.current_value.quantize(CENT) == live.current_value.quantize(CENT)
    assert rebuilt.total_applied.quantize(CENT) == live.total_applied.quantize(CENT)


def test_the_offer_carries_the_dollar_of_today_and_the_fx_iof():
    """A oferta da conta leva o dólar do dia e o IOF do câmbio; as demais ofertas não."""
    on_offer = offer(dollar_account(), START, DEFAULT_TAX_POLICY, Decimal("5.00"))
    cdb = FixedIncomeAssetDTO(
        name="CDB",
        issuer="Banco Teste",
        investment_type=FixedIncomeType.CDB,
        rate_index=RateIndexType.PREFIXADO,
        maturity_date=date(2022, 1, 6),
        interest_rate=Decimal("0.12"),
    )

    assert on_offer.fx_rate == Decimal("5.00")
    assert on_offer.fx_iof_rate == IOF
    assert offer(cdb, START, DEFAULT_TAX_POLICY, Decimal("5.00")).fx_rate is None


def test_quotes_default_to_a_dollar_at_one_real():
    assert FixedIncomeQuotes().dollar == 1
