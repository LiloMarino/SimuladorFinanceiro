from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend import config
from backend.core import repository
from backend.core.decorators import transactional_method
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.enum import IndicatorSeries
from backend.core.migration import drop_databases, ensure_database, migrate
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


@pytest.fixture
def pg_url() -> Iterator[str]:
    """Banco descartável no mesmo servidor do .env, apagado no fim."""
    if not config.env.postgres_url:
        pytest.skip("POSTGRES_DATABASE_URL não configurada")
    url = make_url(config.env.postgres_url).set(
        database=f"simfin_test_{uuid.uuid4().hex[:8]}"
    )
    try:
        ensure_database(url)
    except OperationalError:
        pytest.skip("PostgreSQL indisponível")
    yield url.render_as_string(hide_password=False)
    drop_databases(url, [str(url.database)])


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    engine = create_engine(pg_url, poolclass=NullPool)
    yield engine
    engine.dispose()


@pytest.fixture
def database(pg_url: str, engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Engine:
    """Banco descartável no head, servindo aos repositórios no lugar do .env."""
    migrate(pg_url)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    monkeypatch.setattr(transactional_method, "get_session_factory", lambda: factory)
    return engine
