"""Banco do executável: o do .env quando configurado, senão o Postgres embarcado.

Os testes que sobem o servidor usam os arquivos de `pnpm build:postgres`; apontam para
eles com `SIMFIN_POSTGRES_DIST=postgres_dist` e rodam só no Windows.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from backend import config
from backend.core import embedded_postgres
from backend.core.embedded_postgres import (
    EmbeddedPostgres,
    EmbeddedPostgresError,
    resolve_database_url,
)
from backend.core.migration import ensure_database

DIST = (
    Path(os.environ["SIMFIN_POSTGRES_DIST"])
    if "SIMFIN_POSTGRES_DIST" in os.environ
    else None
)

needs_server_files = pytest.mark.skipif(
    sys.platform != "win32" or DIST is None or not DIST.exists(),
    reason="rode `pnpm build:postgres` e defina SIMFIN_POSTGRES_DIST",
)


# App que sobe o servidor, informa a URL e fica vivo até ser morto pelo teste
RUNNING_APP = """
import sys, time
from pathlib import Path
from backend.core.embedded_postgres import EmbeddedPostgres

url = EmbeddedPostgres(Path(sys.argv[1]), Path(sys.argv[2])).start()
print(url, flush=True)
time.sleep(600)
"""


@pytest.fixture(autouse=True)
def fresh_resolution() -> Iterator[None]:
    resolve_database_url.cache_clear()
    yield
    resolve_database_url.cache_clear()


def test_configured_url_is_used_and_no_server_starts(monkeypatch: pytest.MonkeyPatch):
    def never_started(_self: EmbeddedPostgres) -> str:
        raise AssertionError("o servidor embarcado não deveria subir")

    monkeypatch.setattr(config.env, "postgres_url", "postgresql+psycopg://x/y")
    monkeypatch.setattr(EmbeddedPostgres, "start", never_started)

    assert resolve_database_url() == "postgresql+psycopg://x/y"


def test_missing_url_without_the_server_files_is_refused(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(config.env, "postgres_url", "")
    monkeypatch.setattr(embedded_postgres, "is_available", lambda: False)

    with pytest.raises(EmbeddedPostgresError, match="POSTGRES_DATABASE_URL"):
        resolve_database_url()


def test_missing_visual_cpp_dll_points_to_the_redistributable(tmp_path: Path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "postgres.version").write_text("18.6", "utf-8")
    instance = EmbeddedPostgres(dist, tmp_path / "SimuladorFinanceiro")
    # O Windows devolve STATUS_DLL_NOT_FOUND quando o processo nem chega a iniciar
    instance._process = SimpleNamespace(poll=lambda: 0xC0000135)  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(EmbeddedPostgresError, match="vc_redist"):
        instance._wait_until_ready(5432)


@pytest.fixture
def server(tmp_path: Path) -> Iterator[EmbeddedPostgres]:
    assert DIST is not None
    instance = EmbeddedPostgres(DIST, tmp_path / "SimuladorFinanceiro")
    yield instance
    instance.stop()


@needs_server_files
def test_first_start_creates_a_database_that_only_accepts_the_password(
    server: EmbeddedPostgres,
):
    url = server.start()

    engine = create_engine(url.replace("/simulador_financeiro", "/postgres"))
    with engine.connect() as connection:
        assert connection.execute(text("select 1")).scalar() == 1
    engine.dispose()

    parsed = make_url(url)
    with pytest.raises(psycopg.OperationalError):
        psycopg.connect(
            host="127.0.0.1",
            port=parsed.port,
            user="postgres",
            dbname="postgres",
            connect_timeout=5,
        )


@needs_server_files
def test_data_survives_a_restart(tmp_path: Path):
    assert DIST is not None
    root = tmp_path / "SimuladorFinanceiro"

    first = EmbeddedPostgres(DIST, root)
    url = first.start()
    ensure_database(make_url(url))
    engine = create_engine(url, poolclass=NullPool)
    with engine.begin() as connection:
        connection.execute(text("create table saved (id int, name text)"))
        connection.execute(text("insert into saved values (1, 'ação')"))
    first.stop()

    second = EmbeddedPostgres(DIST, root)
    try:
        restarted = create_engine(second.start(), poolclass=NullPool)
        with restarted.connect() as connection:
            rows = connection.execute(text("select id, name from saved")).all()
        assert [tuple(row) for row in rows] == [(1, "ação")]
    finally:
        second.stop()


@needs_server_files
def test_server_ends_when_the_app_is_killed(tmp_path: Path):
    assert DIST is not None
    app = subprocess.Popen(
        [
            sys.executable,
            "-c",
            RUNNING_APP,
            str(DIST),
            str(tmp_path / "SimuladorFinanceiro"),
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    assert app.stdout is not None
    port = make_url(app.stdout.readline().strip()).port

    # Queda do app sem nenhum encerramento limpo
    app.kill()
    app.wait()

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=1).close()
        except OSError:
            return
        time.sleep(0.3)
    pytest.fail("o servidor embarcado continuou de pé depois da queda do app")
