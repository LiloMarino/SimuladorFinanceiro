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
    UnprocessableEntityError,
)
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import project
from backend.features.fixed_income.fixed_broker import FixedBroker
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
    assert (redeem.event_type, redeem.amount) == (FixedIncomeEventType.REDEEM, expected)
