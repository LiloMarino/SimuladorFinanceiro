from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pandas as pd
import pytest
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend import config
from backend.core import repository
from backend.core.decorators import transactional_method
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, DataOrigin, IndicatorSeries, PlayerGrouping
from backend.core.migration import (
    copy_database,
    drop_databases,
    ensure_database,
    migrate,
)
from backend.core.models.models import Base, StockPriceHistory
from backend.core.repository.economic import IndicatorHistory
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.types import ClientID, Event, JSONValue
from tests.fakes import USER_ID, client, simulation_settings
from tests.test_synthetic_series import build_history


class _SilentRealtimeBroker:
    def notify(
        self, event: Event, payload: JSONValue, to: ClientID | None = None
    ) -> None:
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
        lambda series, _simulation_id=None, *, stored=False: histories.get(
            series, IndicatorHistory([], {})
        ),
    )

    def _set(series: IndicatorSeries, values: dict[date, Decimal]) -> None:
        histories[series] = IndicatorHistory(sorted(values), values)

    return _set


def _scratch_url(server: URL) -> URL:
    return server.set(database=f"simfin_test_{uuid.uuid4().hex[:8]}")


@pytest.fixture(scope="session")
def pg_server() -> URL:
    """O servidor do .env; cada teste e cada modelo ganha um banco próprio nele."""
    if not config.env.postgres_url:
        pytest.skip("POSTGRES_DATABASE_URL não configurada")
    return make_url(config.env.postgres_url)


@pytest.fixture(scope="session")
def migrated_template(pg_server: URL) -> Iterator[URL]:
    """Banco no head, migrado uma vez por sessão; os testes recebem cópias dele."""
    url = pg_server.set(database=f"simfin_tpl_{uuid.uuid4().hex[:8]}")
    try:
        ensure_database(url)
    except OperationalError:
        pytest.skip("PostgreSQL indisponível")
    try:
        migrate(url.render_as_string(hide_password=False))
        yield url
    finally:
        drop_databases(url, [str(url.database)])


@pytest.fixture(scope="session")
def market_template(pg_server: URL, migrated_template: URL) -> Iterator[URL]:
    """
    O histórico sintético de 2000 a 2004 gravado como real, com os ativos
    classificados, montado uma vez por sessão sobre uma cópia do banco migrado.
    """
    url = pg_server.set(database=f"simfin_mkt_{uuid.uuid4().hex[:8]}")
    copy_database(migrated_template, str(url.database))
    engine = create_engine(url, poolclass=NullPool)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(transactional_method, "get_session_factory", lambda: factory)
            _store_market()
        engine.dispose()
        yield url
    finally:
        engine.dispose()
        drop_databases(url, [str(url.database)])


def _store_market() -> None:
    history = build_history()
    for ticker, asset in history.assets.items():
        stock = repository.stock.add_stock(ticker, ticker, AssetClass.STOCK)
        repository.stock.classify(
            ticker,
            StockSegmentDTO(sector=asset.sector or "", segment=asset.segment or ""),
        )
        repository.stock.save_real_prices(
            stock.id,
            [
                StockPriceHistory(
                    stock_id=stock.id,
                    price_date=day,
                    open=open_,
                    high=high,
                    low=low,
                    close=close,
                    volume=int(volume),
                    origin=DataOrigin.REAL.value,
                )
                for day, (open_, high, low, close, volume) in zip(
                    _days_of(asset.bars), asset.bars.to_numpy(dtype=float), strict=True
                )
            ],
        )
    for series, values in history.indicators.items():
        repository.economic.save_history(
            series,
            [
                (day, Decimal(str(round(value, 8))))
                for day, value in zip(
                    _days_of(values), values.to_numpy(dtype=float), strict=True
                )
            ],
        )


@dataclass(frozen=True)
class WorkingCopy:
    """
    Cópia do modelo que serve a sessão inteira e volta ao estado do modelo depois de
    cada teste. Um gatilho por tabela anota em `_seed.dirty` onde o teste escreveu, e
    o reset esvazia e regrava só essas tabelas e as que apontam para elas.
    """

    engine: Engine
    tables: tuple[str, ...]
    seeded: frozenset[str]
    referenced_by: dict[str, frozenset[str]]
    sequences: tuple[tuple[str, int, bool], ...]

    def reset(self) -> None:
        # O pool fecha antes, e as conexões que um teste deixou abertas caem, para o
        # TRUNCATE não esperar por trava de ninguém.
        self.engine.dispose()
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = current_database() AND pid <> pg_backend_pid()"
                )
            )
            dirty = set(
                connection.execute(text("SELECT name FROM _seed.dirty")).scalars()
            )
            if dirty:
                self._restore(connection, self._with_dependents(dirty))
        self.engine.dispose()

    def _with_dependents(self, dirty: set[str]) -> list[str]:
        """As tabelas sujas e, por chave estrangeira, todas as que apontam para elas."""
        pending, closure = list(dirty), set(dirty)
        while pending:
            for child in self.referenced_by.get(pending.pop(), frozenset()):
                if child not in closure:
                    closure.add(child)
                    pending.append(child)
        return [table for table in self.tables if table in closure]

    def _restore(self, connection: Connection, tables: list[str]) -> None:
        # Sem CASCADE: a lista já fecha as chaves estrangeiras, e o Postgres recusa o
        # TRUNCATE se faltar alguma tabela que aponta para outra da lista.
        quoted = ", ".join(f'"{table}"' for table in tables)
        connection.execute(text(f"TRUNCATE {quoted}"))
        # As linhas voltam na ordem das chaves estrangeiras e com os ids originais,
        # inclusive nas colunas de identidade.
        for table in tables:
            if table in self.seeded:
                seed = (
                    f'INSERT INTO "{table}" OVERRIDING SYSTEM VALUE '  # noqa: S608
                    f'SELECT * FROM _seed."{table}"'
                )
                connection.execute(text(seed))
        for sequence, last_value, is_called in self.sequences:
            connection.execute(
                text("SELECT setval(:sequence, :value, :called)"),
                {"sequence": f'"{sequence}"', "value": last_value, "called": is_called},
            )
        # O próprio reset dispara os gatilhos; a anotação zera por último.
        connection.execute(text("TRUNCATE _seed.dirty"))


def _working_copy_of(template: URL, server: URL) -> Iterator[WorkingCopy]:
    """
    Copia o modelo uma vez e guarda, num schema à parte, as linhas que ele já traz,
    a posição de cada sequência e as chaves estrangeiras entre as tabelas. Cada
    tabela ganha o gatilho que anota as escritas.
    """
    url = _scratch_url(server)
    copy_database(template, str(url.database))
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            existing = set(
                connection.execute(
                    text(
                        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                        "AND tablename <> 'alembic_version'"
                    )
                ).scalars()
            )
            ordered = [
                t.name for t in Base.metadata.sorted_tables if t.name in existing
            ]
            tables = tuple(ordered + sorted(existing - set(ordered)))
            connection.execute(text("CREATE SCHEMA _seed"))
            seeded: set[str] = set()
            for table in tables:
                has_rows = f'SELECT EXISTS (SELECT 1 FROM "{table}")'  # noqa: S608
                if connection.execute(text(has_rows)).scalar():
                    connection.execute(
                        text(f'CREATE TABLE _seed."{table}" AS TABLE "{table}"')
                    )
                    seeded.add(table)
            referenced_by: dict[str, set[str]] = {}
            for child, parent in connection.execute(
                text(
                    "SELECT child.relname, parent.relname FROM pg_constraint fk "
                    "JOIN pg_class child ON child.oid = fk.conrelid "
                    "JOIN pg_class parent ON parent.oid = fk.confrelid "
                    "WHERE fk.contype = 'f' AND fk.connamespace = 'public'::regnamespace"
                )
            ):
                referenced_by.setdefault(parent, set()).add(child)
            sequences = tuple(
                (name, int(value), bool(called))
                for name, value, called in connection.execute(
                    text(
                        "SELECT sequencename, coalesce(last_value, start_value), "
                        "last_value IS NOT NULL FROM pg_sequences WHERE schemaname = 'public'"
                    )
                )
            )
            _install_dirty_triggers(connection, tables)
        yield WorkingCopy(
            engine,
            tables,
            frozenset(seeded),
            {parent: frozenset(children) for parent, children in referenced_by.items()},
            sequences,
        )
    finally:
        engine.dispose()
        drop_databases(url, [str(url.database)])


def _install_dirty_triggers(connection: Connection, tables: tuple[str, ...]) -> None:
    connection.execute(text("CREATE TABLE _seed.dirty (name text PRIMARY KEY)"))
    connection.execute(
        text(
            "CREATE FUNCTION _seed.mark_dirty() RETURNS trigger "
            "LANGUAGE plpgsql AS $$ BEGIN "
            "INSERT INTO _seed.dirty VALUES (TG_TABLE_NAME) ON CONFLICT DO NOTHING; "
            "RETURN NULL; END $$"
        )
    )
    for table in tables:
        connection.execute(
            text(
                f'CREATE TRIGGER mark_dirty AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON "{table}" '
                f"FOR EACH STATEMENT EXECUTE FUNCTION _seed.mark_dirty()"
            )
        )


def _serve(copy: WorkingCopy, monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    """A cópia de trabalho serve aos repositórios no lugar do .env e volta ao modelo no fim."""
    factory = sessionmaker(bind=copy.engine, autocommit=False, autoflush=False)
    monkeypatch.setattr(transactional_method, "get_session_factory", lambda: factory)
    try:
        yield copy.engine
    finally:
        copy.reset()


@pytest.fixture(scope="session")
def migrated_copy(pg_server: URL, migrated_template: URL) -> Iterator[WorkingCopy]:
    yield from _working_copy_of(migrated_template, pg_server)


@pytest.fixture(scope="session")
def market_copy(pg_server: URL, market_template: URL) -> Iterator[WorkingCopy]:
    yield from _working_copy_of(market_template, pg_server)


@pytest.fixture
def database(
    migrated_copy: WorkingCopy, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Engine]:
    """Banco no head, servindo aos repositórios no lugar do .env."""
    yield from _serve(migrated_copy, monkeypatch)


@pytest.fixture
def market(
    market_copy: WorkingCopy, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Engine]:
    """Banco com o histórico sintético já gravado."""
    yield from _serve(market_copy, monkeypatch)


def _days_of(data: pd.Series | pd.DataFrame) -> list[date]:
    return data.index.to_numpy().astype("datetime64[D]").tolist()


type Join = Callable[[str], UserDTO]


@pytest.fixture
def team_room(monkeypatch: pytest.MonkeyPatch) -> Join:
    """Sala vazia, em equipes e sem partida; `join("Ana")` conecta um jogador."""
    monkeypatch.setattr(UserManager, "_active_players", {})
    monkeypatch.setattr(UserManager, "_colors", {})
    monkeypatch.setattr(UserManager, "_saved_colors", {})
    monkeypatch.setattr(UserManager, "_teams", {})
    monkeypatch.setattr(UserManager, "_saved_teams", {})
    monkeypatch.setattr(UserManager, "_bots", {})
    monkeypatch.setattr(UserManager, "_parked_bots", {})
    monkeypatch.setattr(SimulationManager, "_active_simulation", None)
    monkeypatch.setattr(SimulationManager, "_simulation_id", None)
    monkeypatch.setattr(
        SettingsManager, "_settings", simulation_settings(PlayerGrouping.TEAMS)
    )
    monkeypatch.setattr(SettingsManager, "_selected_simulation_id", None)
    # Equipes exercitam as regras em memória; a persistência tem cobertura própria.
    monkeypatch.setattr(repository.last_simulation_settings, "save", lambda _: None)
    monkeypatch.setattr(
        RealtimeBrokerManager, "get_broker", lambda: _SilentRealtimeBroker()
    )
    users: dict[str, UserDTO] = {}

    def _join(nickname: str) -> UserDTO:
        user = users.setdefault(
            nickname,
            UserDTO(id=len(users) + 1, client_id=client(nickname), nickname=nickname),
        )
        UserManager._client_user_cache[user.client_id] = user
        UserManager.player_auth(user.client_id)
        return user

    return _join
