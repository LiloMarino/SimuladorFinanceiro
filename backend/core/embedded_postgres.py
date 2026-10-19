"""
Servidor Postgres embarcado no executável do Windows.

O executável leva o zip dos binários oficiais e o zip de um banco vazio já inicializado
(`scripts/build_postgres.py`). Na primeira abertura os dois são extraídos na pasta de
dados do usuário; a cada abertura o servidor sobe numa porta livre, só em 127.0.0.1, e
desce ao fechar. Com `POSTGRES_DATABASE_URL` definida nada disso roda e o banco é o externo.
"""

import atexit
import ctypes
import logging
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import zipfile
from ctypes import wintypes
from functools import cache
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql

from backend import config
from backend.config.paths import user_data_dir
from backend.core.logger import TERMINAL
from backend.core.utils import resource_path

logger = logging.getLogger(__name__)

DATABASE_NAME = "simulador_financeiro"
SUPERUSER = "postgres"
STARTUP_TIMEOUT_SECONDS = 60
SHUTDOWN_TIMEOUT_SECONDS = 30

# STATUS_DLL_NOT_FOUND: o Windows não achou uma DLL, a do Visual C++ numa instalação limpa
MISSING_DLL_EXIT_CODE = 0xC0000135
VC_REDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"

# SQLSTATE de "o servidor está subindo"; sem SQLSTATE, a porta ainda não aceita conexão
STARTING_UP = "57P03"

# Eventos do console do Windows em que o processo morre sem rodar o atexit:
# Ctrl+Break, fechar a janela, sair da sessão e desligar o computador
CONSOLE_CLOSING_EVENTS = {1, 2, 5, 6}

# Conexões só do próprio computador, sempre com a senha sorteada na primeira abertura
PG_HBA = """\
host    all    all    127.0.0.1/32    scram-sha-256
host    all    all    ::1/128         scram-sha-256
"""


class EmbeddedPostgresError(RuntimeError):
    """O servidor embarcado não pôde ser preparado, subir ou aceitar conexões."""


def dist_dir() -> Path:
    return resource_path("backend/postgres")


def is_available() -> bool:
    """Só o executável do Windows leva o servidor (D4)."""
    dist = dist_dir()
    return (
        sys.platform == "win32"
        and (dist / "postgres.zip").exists()
        and (dist / "cluster.zip").exists()
    )


class EmbeddedPostgres:
    """
    Ciclo de vida do servidor: `start()` devolve a URL do banco e `stop()` o encerra.
    O estado em disco é `<root>/postgres/<versão>` (binários), `<root>/db` (banco),
    `<root>/db.password` e `<root>/postgres.log`.

    O servidor é filho deste processo e o Windows o encerra junto com ele, mesmo numa
    queda. O encerramento limpo roda no fim normal do processo e nos eventos do console
    que o matam sem atexit.
    """

    def __init__(self, dist: Path, root: Path):
        self._dist = dist
        self._root = root
        self._version = (dist / "postgres.version").read_text("utf-8").strip()
        self._bin = root / "postgres" / self._version / "bin"
        self._data = root / "db"
        self._password_file = root / "db.password"
        self._log = root / "postgres.log"
        self._process: subprocess.Popen[bytes] | None = None
        self._lock = threading.Lock()

    def start(self) -> str:
        self._root.mkdir(parents=True, exist_ok=True)
        try:
            self._install_binaries()
            self._install_cluster()
        except (OSError, zipfile.BadZipFile) as error:
            raise EmbeddedPostgresError(
                f"Não foi possível preparar o banco em {self._root}: {error}. "
                "Confira o espaço em disco e se o antivírus não bloqueou a pasta."
            ) from error

        atexit.register(self.stop)
        _stop_on_console_events(self)
        port = self._start_server()
        password = self._secure(port)
        logger.info(
            "PostgreSQL %s embarcado em 127.0.0.1:%s",
            self._version,
            port,
            extra=TERMINAL,
        )
        return f"postgresql+psycopg://{SUPERUSER}:{password}@127.0.0.1:{port}/{DATABASE_NAME}"

    def stop(self) -> None:
        with self._lock:
            process, self._process = self._process, None
        if process is None:
            return
        subprocess.run(
            [
                str(self._bin / "pg_ctl.exe"),
                "-D",
                str(self._data),
                "-m",
                "fast",
                "-w",
                "-t",
                str(SHUTDOWN_TIMEOUT_SECONDS),
                "stop",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
        try:
            process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info("PostgreSQL embarcado encerrado")

    def _install_binaries(self) -> None:
        if (self._bin / "postgres.exe").exists():
            return
        logger.info(
            "Extraindo o PostgreSQL %s (só na primeira abertura)",
            self._version,
            extra=TERMINAL,
        )
        self._extract(self._dist / "postgres.zip", self._bin.parent)

    def _install_cluster(self) -> None:
        if not (self._data / "PG_VERSION").exists():
            logger.info(
                "Criando o banco de dados do jogo (só na primeira abertura)",
                extra=TERMINAL,
            )
            self._extract(self._dist / "cluster.zip", self._data)
        found = (self._data / "PG_VERSION").read_text("utf-8").strip()
        expected = self._version.split(".")[0]
        if found != expected:
            raise EmbeddedPostgresError(
                f"O banco em {self._data} é do PostgreSQL {found} e este executável "
                f"traz o {expected}. Apague a pasta ou use a versão anterior do jogo."
            )

    @staticmethod
    def _extract(archive: Path, destination: Path) -> None:
        # Extrai ao lado e renomeia no fim: uma interrupção não deixa pasta pela metade
        partial = destination.with_name(destination.name + ".partial")
        shutil.rmtree(partial, ignore_errors=True)
        with zipfile.ZipFile(archive) as zipped:
            zipped.extractall(partial)
        shutil.rmtree(destination, ignore_errors=True)
        partial.rename(destination)

    def _start_server(self) -> int:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        with self._log.open("ab") as log:
            self._process = subprocess.Popen(
                [
                    str(self._bin / "postgres.exe"),
                    "-D",
                    str(self._data),
                    "-p",
                    str(port),
                    "-c",
                    "listen_addresses=127.0.0.1",
                ],
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        _end_with_this_process(self._process)
        self._wait_until_ready(port)
        return port

    def _wait_until_ready(self, port: int) -> None:
        assert self._process is not None
        password = (
            self._password_file.read_text("utf-8").strip()
            if self._password_file.exists()
            else None
        )
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if self._process.poll() is not None:
                break
            try:
                self._connect(port, password).close()
            except psycopg.OperationalError as error:
                if error.sqlstate not in (None, STARTING_UP):
                    raise EmbeddedPostgresError(
                        f"O servidor embarcado recusou a conexão: {error}"
                    ) from error
            else:
                return
            time.sleep(0.2)
        exit_code = self._process.poll()
        if exit_code is not None and exit_code & 0xFFFFFFFF == MISSING_DLL_EXIT_CODE:
            raise EmbeddedPostgresError(
                "O Windows não encontrou uma DLL do Visual C++ de que o banco de "
                "dados precisa. Instale o Microsoft Visual C++ Redistributable (x64), "
                f"que também acompanha a release do jogo: {VC_REDIST_URL}\n"
                "Depois abra o jogo de novo."
            )
        raise EmbeddedPostgresError(
            "O servidor PostgreSQL embarcado não subiu. "
            f"Fim do log ({self._log}):\n{self._log_tail()}"
        )

    def _secure(self, port: int) -> str:
        """Garante senha no superusuário e autenticação por senha; devolve a senha."""
        if self._password_file.exists():
            password = self._password_file.read_text("utf-8").strip()
        else:
            # O banco recém-criado aceita conexão local sem senha: é a hora de defini-la
            password = secrets.token_urlsafe(24)
            with self._connect(port, password=None) as connection:
                connection.execute(
                    sql.SQL("ALTER USER {} PASSWORD {}").format(
                        sql.Identifier(SUPERUSER), sql.Literal(password)
                    )
                )
            self._password_file.write_text(password, "utf-8")

        with self._connect(port, password) as connection:
            hba = self._data / "pg_hba.conf"
            if "trust" in hba.read_text("utf-8"):
                hba.write_text(PG_HBA, "utf-8")
                connection.execute("SELECT pg_reload_conf()")
        return password

    def _connect(self, port: int, password: str | None) -> psycopg.Connection[Any]:
        return psycopg.connect(
            host="127.0.0.1",
            port=port,
            user=SUPERUSER,
            password=password,
            dbname="postgres",
            connect_timeout=2,
            autocommit=True,
        )

    def _log_tail(self, lines: int = 15) -> str:
        if not self._log.exists():
            return "(sem log)"
        text = self._log.read_text("utf-8", errors="replace")
        return "\n".join(text.splitlines()[-lines:])


# Fica no módulo enquanto o processo vive: o Windows encerra o grupo quando o
# último identificador do job fecha
_job_handle: Any = None

# Mantém o tratador de eventos do console vivo (o ctypes o libera se perder a referência)
_console_handler: Any = None


def _end_with_this_process(process: subprocess.Popen[bytes]) -> None:
    """Põe o processo num Job Object que o Windows encerra junto com este processo."""
    if sys.platform != "win32":
        return

    class BasicLimits(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimits),
            ("IoInfo", ctypes.c_uint64 * 6),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    global _job_handle
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]

    job_object_extended_limit_information = 9
    kill_on_job_close = 0x2000
    if _job_handle is None:
        _job_handle = kernel32.CreateJobObjectW(None, None)
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = kill_on_job_close
        kernel32.SetInformationJobObject(
            _job_handle,
            job_object_extended_limit_information,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        )
    process_set_quota, process_terminate = 0x0100, 0x0001
    kernel32.OpenProcess.restype = wintypes.HANDLE
    process_handle = kernel32.OpenProcess(
        process_set_quota | process_terminate, False, process.pid
    )
    assigned = process_handle and kernel32.AssignProcessToJobObject(
        _job_handle, process_handle
    )
    if process_handle:
        kernel32.CloseHandle(process_handle)
    if not assigned:
        logger.warning("O servidor embarcado não ficou preso a este processo")


def _stop_on_console_events(server: EmbeddedPostgres) -> None:
    """Encerra o servidor com calma quando o console fecha o processo sem atexit."""
    global _console_handler
    if sys.platform != "win32" or _console_handler is not None:
        return
    handler_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

    def on_event(event: int) -> bool:
        if event in CONSOLE_CLOSING_EVENTS:
            server.stop()
        return False

    _console_handler = handler_type(on_event)
    ctypes.WinDLL("kernel32", use_last_error=True).SetConsoleCtrlHandler(
        _console_handler, True
    )


@cache
def resolve_database_url() -> str:
    """O banco do .env quando configurado; senão, o servidor embarcado."""
    configured = config.env.postgres_url
    if configured:
        return configured
    if not is_available():
        raise EmbeddedPostgresError(
            "POSTGRES_DATABASE_URL não configurada. "
            "Configure a variável de ambiente no arquivo .env"
        )
    return EmbeddedPostgres(dist_dir(), user_data_dir()).start()
