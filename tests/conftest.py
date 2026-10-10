from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import IndicatorSeries
from backend.core.repository.economic import IndicatorHistory
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from tests.fakes import USER_ID


class _SilentRealtimeBroker:
    def notify(self, *_args: object, **_kwargs: object) -> None:
        pass


@pytest.fixture
def captured_events(monkeypatch: pytest.MonkeyPatch) -> list[BaseEventDTO]:
    """
    Isola o domínio dos singletons: realtime mudo, todo cliente é o usuário
    `USER_ID` (sem cadastro carregado) e os eventos que iriam ao banco ficam na
    lista devolvida.
    """
    events: list[BaseEventDTO] = []
    monkeypatch.setattr(EventManager, "push_event", events.append)
    monkeypatch.setattr(UserManager, "get_user", lambda _: None)
    monkeypatch.setattr(UserManager, "get_user_id", lambda _: USER_ID)
    monkeypatch.setattr(
        RealtimeBrokerManager, "get_broker", lambda: _SilentRealtimeBroker()
    )
    return events


type SetIndicator = Callable[[IndicatorSeries, dict[date, Decimal]], None]


@pytest.fixture
def indicators(monkeypatch: pytest.MonkeyPatch) -> SetIndicator:
    """
    Séries de indicadores em memória no lugar do banco: `indicators(série, valores)`
    define uma série; as não definidas ficam vazias.
    """
    histories: dict[IndicatorSeries, IndicatorHistory] = {}
    monkeypatch.setattr(
        repository.economic,
        "get_history",
        lambda series: histories.get(series, IndicatorHistory([], {})),
    )

    def _set(series: IndicatorSeries, values: dict[date, Decimal]) -> None:
        histories[series] = IndicatorHistory(sorted(values), values)

    return _set
