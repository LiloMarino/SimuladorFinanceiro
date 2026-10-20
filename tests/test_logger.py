from __future__ import annotations

import io
import logging
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from backend.core.logger import LIBRARY_LEVELS, TERMINAL, setup_logging

Setup = Callable[..., Path]  # setup(debug=False, sql=False)

# Loggers cujo nível o `setup_logging` mexe; voltam ao que eram depois do teste
_TOUCHED_LOGGERS = ("backend", "uvicorn.access", "sqlalchemy.engine", *LIBRARY_LEVELS)


@pytest.fixture
def setup(tmp_path: Path) -> Iterator[Setup]:
    """`setup_logging` no raiz limpo, gravando em `tmp_path`; o raiz volta ao que era."""
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    saved_factory = logging.getLogRecordFactory()
    saved_levels = {name: logging.getLogger(name).level for name in _TOUCHED_LOGGERS}
    root.handlers = []

    def run(*, debug: bool = False, sql: bool = False) -> Path:
        # O pytest põe handlers de captura no raiz ao iniciar o teste
        root.handlers = []
        setup_logging(logs_path=str(tmp_path), debug=debug, sql=sql)
        return tmp_path

    yield run

    for handler in root.handlers:
        handler.close()
    root.handlers = saved_handlers
    root.setLevel(saved_level)
    logging.setLogRecordFactory(saved_factory)
    for name, level in saved_levels.items():
        logging.getLogger(name).setLevel(level)


@pytest.fixture
def logs(setup: Setup) -> Path:
    return setup()


@pytest.fixture
def console(logs: Path) -> io.StringIO:
    """O que o terminal recebeu: o stream do handler de console vira um buffer."""
    stream = io.StringIO()
    handler = next(
        h for h in logging.getLogger().handlers if type(h) is logging.StreamHandler
    )
    handler.setStream(stream)
    return stream


def read(logs: Path, name: str) -> str:
    path = logs / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def test_exception_leaves_traceback_in_error_log(logs: Path) -> None:
    try:
        int("falha provocada")
    except ValueError:
        logging.getLogger("backend.routes.simulation").exception("ValueError")

    for name in ("error.log", "app.log"):
        content = read(logs, name)
        assert "Traceback" in content
        assert "falha provocada" in content


def test_error_log_stays_empty_without_failures(logs: Path) -> None:
    logging.getLogger("backend.features.simulation.simulation").info("tick")
    logging.getLogger("backend.routes").warning("aviso")

    assert read(logs, "error.log") == ""
    assert "tick" in read(logs, "app.log")


def test_expected_library_failure_stays_out_of_error_log(logs: Path) -> None:
    logging.getLogger("yfinance").error("possibly delisted")

    assert "possibly delisted" in read(logs, "app.log")
    assert "possibly delisted" in read(logs, "import.log")
    assert read(logs, "error.log") == ""


@pytest.mark.parametrize(
    ("logger_name", "file_name"),
    [
        ("backend.features.simulation.simulation_loop", "simulation.log"),
        ("backend.features.variable_income.broker", "simulation.log"),
        ("backend.features.realtime.ws_broker", "realtime.log"),
        ("socketio.server", "realtime.log"),
        ("backend.features.import_data.importer_service", "import.log"),
        ("backend.core.migration", "database.log"),
        ("sqlalchemy.engine", "database.log"),
        ("backend.metrics", "slow.log"),
    ],
)
def test_line_goes_to_area_file_and_app_log(
    logs: Path, logger_name: str, file_name: str
) -> None:
    logging.getLogger(logger_name).warning("linha da área")

    assert "linha da área" in read(logs, file_name)
    assert "linha da área" in read(logs, "app.log")
    other_areas = {
        "simulation.log",
        "realtime.log",
        "import.log",
        "database.log",
        "slow.log",
    }
    for other in other_areas - {file_name}:
        assert read(logs, other) == ""


def test_logger_outside_the_table_stays_in_app_log(logs: Path) -> None:
    logging.getLogger("backend.routes.auth").info("login")
    logging.getLogger("sqlalchemyfoo").info("prefixo parecido")

    assert "login" in read(logs, "app.log")
    assert "prefixo parecido" in read(logs, "app.log")
    assert read(logs, "database.log") == ""


def test_debug_mode_keeps_access_lines_out_of_the_console(setup: Setup) -> None:
    logs = setup(debug=True)
    stream = io.StringIO()
    next(
        h for h in logging.getLogger().handlers if type(h) is logging.StreamHandler
    ).setStream(stream)
    logging.getLogger("uvicorn.access").info("GET /api/x 200")

    assert "GET /api/x" in read(logs, "app.log")
    assert stream.getvalue() == ""


def test_uvicorn_reaches_app_log_without_access_lines(logs: Path) -> None:
    logging.getLogger("uvicorn.error").info("erro de protocolo do WebSocket")
    logging.getLogger("uvicorn.access").info("GET /api/x 200")

    content = read(logs, "app.log")
    assert "erro de protocolo do WebSocket" in content
    assert "GET /api/x" not in content


def test_normal_mode_drops_app_debug(logs: Path) -> None:
    logging.getLogger("backend.features.simulation.simulation").debug("detalhe do tick")

    assert "detalhe do tick" not in read(logs, "app.log")


def test_debug_mode_writes_app_debug_to_app_and_area_logs(setup: Setup) -> None:
    logs = setup(debug=True)
    logging.getLogger("backend.features.simulation.simulation").debug("detalhe do tick")

    assert "detalhe do tick" in read(logs, "app.log")
    assert "detalhe do tick" in read(logs, "simulation.log")


def test_debug_mode_keeps_error_log_to_errors_only(setup: Setup) -> None:
    logs = setup(debug=True)
    logging.getLogger("backend.routes").debug("só debug")
    logging.getLogger("backend.routes").error("falhou")

    content = read(logs, "error.log")
    assert "falhou" in content
    assert "só debug" not in content


def test_debug_mode_keeps_libraries_at_warning(setup: Setup) -> None:
    logs = setup(debug=True)
    logging.getLogger("engineio.server").info("pacote 42")
    logging.getLogger("engineio.server").warning("cliente caiu")

    content = read(logs, "realtime.log")
    assert "pacote 42" not in content
    assert "cliente caiu" in content


def test_sql_is_off_without_the_sql_option(setup: Setup) -> None:
    logs = setup(debug=True)
    logging.getLogger("sqlalchemy.engine.Engine").info("SELECT 1")

    for name in ("app.log", "database.log"):
        assert "SELECT 1" not in read(logs, name)


def test_sql_needs_debug_mode(setup: Setup) -> None:
    logs = setup(sql=True)
    logging.getLogger("sqlalchemy.engine.Engine").info("SELECT 1")

    assert "SELECT 1" not in read(logs, "database.log")


def test_sql_goes_only_to_database_log(setup: Setup) -> None:
    logs = setup(debug=True, sql=True)
    logging.getLogger("sqlalchemy.engine.Engine").info("SELECT 1")

    assert "SELECT 1" in read(logs, "database.log")
    assert "SELECT 1" not in read(logs, "app.log")


def test_library_warning_still_reaches_app_log(logs: Path) -> None:
    logging.getLogger("sqlalchemy.pool").warning("conexão perdida")

    assert "conexão perdida" in read(logs, "app.log")
    assert "conexão perdida" in read(logs, "database.log")


def test_console_ignores_plain_info(logs: Path, console: io.StringIO) -> None:
    logging.getLogger("backend.features.simulation.simulation").info("partida iniciada")

    assert console.getvalue() == ""
    assert "partida iniciada" in read(logs, "app.log")


def test_console_shows_terminal_messages_plain(
    logs: Path, console: io.StringIO
) -> None:
    logging.getLogger("backend.main").info("Acesse: %s", "http://x", extra=TERMINAL)

    assert console.getvalue() == "Acesse: http://x\n"
    assert "Acesse: http://x" in read(logs, "app.log")


def test_console_shows_warning_as_one_short_line(
    logs: Path, console: io.StringIO
) -> None:
    logging.getLogger("backend.routes").warning("aviso")

    line = console.getvalue()
    assert "WARNING ROUTES: aviso" in line
    assert "[" not in line


def test_console_exception_has_no_traceback(logs: Path, console: io.StringIO) -> None:
    try:
        int("falha provocada")
    except ValueError:
        logging.getLogger("backend.routes").exception("ValueError")

    assert "Traceback" not in console.getvalue()
    assert "detalhes em" in console.getvalue()
    assert "Traceback" in read(logs, "error.log")


def test_console_never_shows_debug(setup: Setup) -> None:
    logs = setup(debug=True)
    stream = io.StringIO()
    next(
        h for h in logging.getLogger().handlers if type(h) is logging.StreamHandler
    ).setStream(stream)
    logging.getLogger("backend.features.simulation.simulation").debug(
        "detalhe", extra=TERMINAL
    )
    logging.getLogger("backend.features.simulation.simulation").debug("outro")

    assert "outro" not in stream.getvalue()
    assert "detalhe" in read(logs, "app.log")
