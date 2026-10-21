"""
O app da demonstração: o backend de sempre, num banco próprio e com o config da demo.

Rodando do código-fonte, `config.toml`, `.env` e `logs/` vêm do diretório atual
(`backend/config/paths.py`). O servidor sobe numa pasta de trabalho com o
`config.toml` desta pasta, e o banco vem por `POSTGRES_DATABASE_URL` no ambiente.

Os bancos são dois. O banco-base, de `POSTGRES_DEMO_DATABASE_URL` no `.env`, guarda as
cotações e os indicadores entre uma gravação e outra, para o Banco Central só ser
consultado quando falta algo. Cada gravação roda numa cópia dele, apagada no fim, e
por isso começa sempre do mesmo estado.
"""

import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import make_url

from backend.core.migration import copy_database, drop_databases
from backend.core.utils import PROJECT_ROOT

DEMO_DIR = Path(__file__).parent
DEMO_CONFIG = DEMO_DIR / "config.toml"
STARTUP_TIMEOUT_SECONDS = 90
SHUTDOWN_TIMEOUT_SECONDS = 30


class DemoSetupError(RuntimeError):
    """Falta algo na máquina para gravar a demonstração."""


class DemoEnv(BaseSettings):
    base_database_url: str = Field(default="", alias="POSTGRES_DEMO_DATABASE_URL")

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


def demo_settings() -> dict:
    with DEMO_CONFIG.open("rb") as file:
        return tomllib.load(file)


def build_frontend() -> None:
    """O backend serve o front buildado em `backend/static`."""
    pnpm = shutil.which("pnpm")
    if pnpm is None:
        raise DemoSetupError("pnpm não encontrado no PATH.")
    subprocess.run([pnpm, "run", "build:frontend"], cwd=PROJECT_ROOT, check=True)


def base_database_url() -> str:
    url = DemoEnv().base_database_url
    if not url:
        raise DemoSetupError(
            "POSTGRES_DEMO_DATABASE_URL não configurada no .env: é o banco-base da "
            "demo, por exemplo a URL do POSTGRES_DATABASE_URL com o banco simfin_demo."
        )
    return url


@contextmanager
def recording_database() -> Iterator[str]:
    """Uma cópia do banco-base para uma gravação; na saída, a cópia é apagada."""
    base = make_url(base_database_url())
    copy = base.set(database=f"{base.database}_run")
    copy_database(base, str(copy.database))
    try:
        yield copy.render_as_string(hide_password=False)
    finally:
        drop_databases(base, [str(copy.database)])


def wait_until_up(base_url: str, process: subprocess.Popen, log_path: Path) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise DemoSetupError(
                f"O backend saiu com código {process.returncode}: veja {log_path}"
            )
        # Qualquer resposta HTTP, mesmo de erro, é o servidor de pé
        try:
            with urllib.request.urlopen(f"{base_url}/api/simulation/status"):
                return
        except urllib.error.HTTPError:
            return
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.5)
    raise DemoSetupError(
        f"O backend não respondeu em {STARTUP_TIMEOUT_SECONDS} s: veja {log_path}"
    )


def stop(process: subprocess.Popen) -> None:
    """Ctrl+Break no grupo do processo: o uvicorn desce pelo shutdown e solta o banco."""
    if process.poll() is not None:
        return
    if sys.platform == "win32":
        process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        process.send_signal(signal.SIGINT)
    try:
        process.wait(SHUTDOWN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@contextmanager
def demo_server(workdir: Path, database_url: str) -> Iterator[str]:
    """
    Sobe o backend no banco `database_url`, com `workdir` como diretório de trabalho,
    e devolve a URL do app. O log fica em `workdir/<banco>.log`.
    """
    port = demo_settings()["server"]["port"]
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            raise DemoSetupError(
                f"A porta {port} já está em uso: troque-a em {DEMO_CONFIG}."
            )
    base_url = f"http://127.0.0.1:{port}"

    workdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(DEMO_CONFIG, workdir / "config.toml")
    log_path = workdir / f"{make_url(database_url).database}.log"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "main.py")],
            cwd=workdir,
            env={
                **os.environ,
                "POSTGRES_DATABASE_URL": database_url,
                "PYTHONIOENCODING": "utf-8",
            },
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            if sys.platform == "win32"
            else 0,
        )
        try:
            wait_until_up(base_url, process, log_path)
            yield base_url
        finally:
            stop(process)
