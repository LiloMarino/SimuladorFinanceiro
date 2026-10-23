from __future__ import annotations

import threading
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType, FixedIncomeType, RateIndexType
from backend.core.exceptions import InsufficentCashError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import project
from backend.features.fixed_income.fixed_broker import FixedBroker, load_fixed_assets
from tests.fakes import FakeSimulationEngine, client

INVESTOR = client("investor")
BUY_DATE = date(2020, 1, 6)  # segunda-feira
ASSET_ID = 7


@pytest.fixture
def fixed_income_db(
    monkeypatch: pytest.MonkeyPatch, captured_events: list[BaseEventDTO]
) -> None:
    """Banco de renda fixa em memória: sem histórico."""
    monkeypatch.setattr(
        repository.fixed_income, "get_events", lambda simulation_id, user_id: []
    )
    monkeypatch.setattr(
        repository.fixed_income, "get_or_create_asset", lambda asset: ASSET_ID
    )


def _asset(maturity: date = date(2021, 1, 6)) -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        name="CDB Teste",
        issuer="Banco Teste",
        investment_type=FixedIncomeType.CDB,
        rate_index=RateIndexType.PREFIXADO,
        maturity_date=maturity,
        interest_rate=Decimal("0.12"),
    )


def _broker(cash: str = "1000") -> tuple[FixedBroker, FakeSimulationEngine]:
    engine = FakeSimulationEngine(cash={INVESTOR: Decimal(cash)}, current_date=BUY_DATE)
    return FixedBroker(engine, threading.RLock()), engine


def _fixed_events(events: list[BaseEventDTO]) -> list[FixedIncomeEventDTO]:
    return [e for e in events if isinstance(e, FixedIncomeEventDTO)]


@pytest.mark.parametrize("value", ["0", "-10"])
def test_non_positive_value_is_rejected(fixed_income_db, value: str):
    """Aplicação de valor zero ou negativo é rejeitada como entrada inválida."""
    broker, _ = _broker()

    with pytest.raises(UnprocessableEntityError):
        broker.buy(INVESTOR, _asset(), Decimal(value))


def test_matured_asset_is_rejected(fixed_income_db):
    """Título com vencimento até a data atual não pode ser comprado."""
    broker, _ = _broker()

    with pytest.raises(ConflictError):
        broker.buy(INVESTOR, _asset(maturity=BUY_DATE), Decimal("100"))


def test_buy_without_cash_is_rejected(fixed_income_db, captured_events):
    """Aplicação acima do saldo falha sem debitar, abrir posição ou emitir evento."""
    broker, engine = _broker(cash="50")

    with pytest.raises(InsufficentCashError):
        broker.buy(INVESTOR, _asset(), Decimal("100"))

    assert engine.cash[INVESTOR] == Decimal("50")
    assert broker.get_fixed_positions(INVESTOR) == {}
    assert captured_events == []


def test_second_buy_adds_to_same_position(fixed_income_db, captured_events):
    """Aportes no mesmo título somam na mesma posição e cada um vira um evento BUY."""
    broker, engine = _broker()
    asset = _asset()

    broker.buy(INVESTOR, asset, Decimal("300"))
    broker.buy(INVESTOR, asset, Decimal("200.50"))

    position = broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]
    assert engine.cash[INVESTOR] == Decimal("499.50")
    assert position.total_applied == Decimal("500.50")
    assert position.first_applied_date == BUY_DATE
    assert [(e.event_type, e.amount) for e in _fixed_events(captured_events)] == [
        (FixedIncomeEventType.BUY, Decimal("300")),
        (FixedIncomeEventType.BUY, Decimal("200.50")),
    ]


def test_daily_interest_before_redemption_only_accrues(fixed_income_db):
    """Antes do resgate o tick só rende: a posição continua aberta."""
    broker, _ = _broker()
    asset = _asset()
    broker.buy(INVESTOR, asset, Decimal("1000"))

    broker.apply_daily_interest(next_business_day(BUY_DATE))

    position = broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]
    assert position.current_value > Decimal("1000")


def test_redemption_credits_projected_net_value(fixed_income_db, captured_events):
    """No dia do resgate credita o líquido projetado na compra, fecha a posição e emite REDEEM."""
    asset = _asset(maturity=date(2020, 1, 10))
    broker, engine = _broker()
    broker.buy(INVESTOR, asset, Decimal("1000"))
    expected = project(asset, Decimal("1000"), BUY_DATE).net_amount

    day = BUY_DATE
    while day < asset.maturity_date:
        day = next_business_day(day)
        broker.apply_daily_interest(day)

    redeem = _fixed_events(captured_events)[-1]
    assert engine.cash[INVESTOR] == expected
    assert broker.get_fixed_positions(INVESTOR) == {}
    # O evento guarda o que saiu do título (bruto); o caixa recebeu o líquido
    assert redeem.event_type is FixedIncomeEventType.REDEEM
    assert redeem.amount > expected


# =========================================================
# ======== Liquidez diária: resgate, teto e oferta rara
# =========================================================
def _liquid(**changes) -> FixedIncomeAssetDTO:
    return _asset(maturity=date(2022, 1, 6)).model_copy(
        update={"daily_liquidity": True, **changes}
    )


def _tick(broker: FixedBroker, engine: FakeSimulationEngine, days: int) -> None:
    for _ in range(days):
        engine.current_date = next_business_day(engine.current_date)
        broker.apply_daily_interest(engine.current_date)


def test_partial_redemption_credits_exact_net_and_keeps_proportions(
    fixed_income_db, captured_events
):
    """O resgate parcial deixa no caixa o líquido pedido ao centavo e reduz C e M na mesma proporção."""
    broker, engine = _broker(cash="10000")
    asset = _liquid()
    broker.buy(INVESTOR, asset, Decimal("10000"))
    _tick(broker, engine, 100)
    position = broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]
    before_value, before_applied = position.current_value, position.total_applied
    cash_before = engine.cash[INVESTOR]

    broker.redeem(INVESTOR, asset, Decimal("2000"))

    assert engine.cash[INVESTOR] - cash_before == Decimal("2000.00")
    redeem = _fixed_events(captured_events)[-1]
    assert redeem.event_type is FixedIncomeEventType.REDEEM
    assert redeem.amount > Decimal("2000")
    assert position.current_value == before_value - redeem.amount
    assert position.total_applied / position.current_value == pytest.approx(
        before_applied / before_value
    )


def test_full_redemption_removes_the_position(fixed_income_db):
    """Pedir o líquido máximo resgata tudo e fecha a posição."""
    broker, engine = _broker(cash="1000")
    asset = _liquid()
    broker.buy(INVESTOR, asset, Decimal("1000"))
    _tick(broker, engine, 60)
    position = broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]
    maximum = position.breakdown(engine.current_date, None).net

    broker.redeem(INVESTOR, asset, maximum)

    assert broker.get_fixed_positions(INVESTOR) == {}
    assert engine.cash[INVESTOR] == maximum


def test_redeem_errors(fixed_income_db):
    """Sem liquidez é 409, sem posição é 404 e acima do máximo é 422; nada é creditado."""
    broker, engine = _broker(cash="1000")
    illiquid, asset = _asset(), _liquid()
    broker.buy(INVESTOR, illiquid, Decimal("100"))

    with pytest.raises(ConflictError):
        broker.redeem(INVESTOR, illiquid, Decimal("10"))
    with pytest.raises(NotFoundError):
        broker.redeem(INVESTOR, asset, Decimal("10"))

    broker.buy(INVESTOR, asset, Decimal("500"))
    cash = engine.cash[INVESTOR]
    with pytest.raises(UnprocessableEntityError, match=r"até R\$"):
        broker.redeem(INVESTOR, asset, Decimal("501"))
    with pytest.raises(UnprocessableEntityError):
        broker.redeem(INVESTOR, asset, Decimal(0))
    assert engine.cash[INVESTOR] == cash


def test_player_cap_counts_applied_capital_and_a_redemption_frees_room(
    fixed_income_db,
):
    """O teto vale sobre o capital aplicado da posição: passar dele é 422 e resgatar libera espaço."""
    broker, _ = _broker(cash="30000")
    asset = _liquid(player_cap=Decimal("20000"))
    broker.buy(INVESTOR, asset, Decimal("15000"))

    with pytest.raises(UnprocessableEntityError, match=r"cabem mais R\$ 5.000,00"):
        broker.buy(INVESTOR, asset, Decimal("5001"))

    broker.redeem(INVESTOR, asset, Decimal("7500"))
    broker.buy(INVESTOR, asset, Decimal("12000"))
    assert broker.get_fixed_positions(INVESTOR)[asset.asset_uuid].total_applied > 0


def test_offer_out_of_catalog_refuses_buy_but_allows_redeem(fixed_income_db):
    """Depois de `offered_until` não entra aporte novo, mas o resgate continua valendo."""
    broker, engine = _broker(cash="1000")
    asset = _liquid(offered_until=date(2020, 1, 31))
    broker.buy(INVESTOR, asset, Decimal("500"))
    engine.current_date = date(2020, 2, 3)

    with pytest.raises(ConflictError, match="01/02/2020"):
        broker.buy(INVESTOR, asset, Decimal("100"))
    broker.redeem(INVESTOR, asset, Decimal("100"))


def test_rebuild_from_events_matches_the_live_game(
    fixed_income_db, captured_events, monkeypatch: pytest.MonkeyPatch
):
    """Compra, resgate parcial, resgate total e recompra reconstruídos dos eventos igualam o jogo ao vivo."""
    broker, engine = _broker(cash="30000")
    asset = _liquid()

    broker.buy(INVESTOR, asset, Decimal("10000"))
    _tick(broker, engine, 40)
    broker.redeem(INVESTOR, asset, Decimal("3000"))
    _tick(broker, engine, 25)
    position = broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]
    broker.redeem(INVESTOR, asset, position.breakdown(engine.current_date, None).net)
    assert broker.get_fixed_positions(INVESTOR) == {}
    _tick(broker, engine, 3)
    broker.buy(INVESTOR, asset, Decimal("4000"))
    _tick(broker, engine, 10)
    broker.redeem(INVESTOR, asset, Decimal("500"))
    _tick(broker, engine, 5)

    live = broker.get_fixed_positions(INVESTOR)[asset.asset_uuid]
    monkeypatch.setattr(
        repository.fixed_income,
        "get_events",
        lambda simulation_id, user_id: [
            (asset, e) for e in _fixed_events(captured_events)
        ],
    )
    rebuilt = load_fixed_assets(1, INVESTOR, engine.current_date)[asset.asset_uuid]

    assert rebuilt.current_value.quantize(
        Decimal("0.01")
    ) == live.current_value.quantize(Decimal("0.01"))
    assert rebuilt.total_applied.quantize(
        Decimal("0.01")
    ) == live.total_applied.quantize(Decimal("0.01"))
    assert rebuilt.first_applied_date == live.first_applied_date
