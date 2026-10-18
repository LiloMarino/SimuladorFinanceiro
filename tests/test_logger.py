from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from backend.core.logger import NOISY_LOGGERS, setup_logging


@pytest.fixture
def logs(tmp_path: Path) -> Iterator[Path]:
    """`setup_logging` rodando no raiz limpo, gravando em `tmp_path`; o raiz volta ao que era."""
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    saved_factory = logging.getLogRecordFactory()
    saved_access_level = logging.getLogger("uvicorn.access").level
    root.handlers = []

    setup_logging(logs_path=str(tmp_path))
    yield tmp_path

    for handler in root.handlers:
        handler.close()
    root.handlers = saved_handlers
    root.setLevel(saved_level)
    logging.setLogRecordFactory(saved_factory)
    logging.getLogger("uvicorn.access").setLevel(saved_access_level)


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


def test_uvicorn_reaches_app_log_without_access_lines(logs: Path) -> None:
    logging.getLogger("uvicorn.error").info("erro de protocolo do WebSocket")
    logging.getLogger("uvicorn.access").info("GET /api/x 200")

    content = read(logs, "app.log")
    assert "erro de protocolo do WebSocket" in content
    assert "GET /api/x" not in content


@pytest.fixture
def debug_logs(tmp_path: Path) -> Iterator[Path]:
    """Como `logs`, mas com o modo debug ligado (nível DEBUG)."""
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    saved_factory = logging.getLogRecordFactory()
    saved_access_level = logging.getLogger("uvicorn.access").level
    saved_noisy = {name: logging.getLogger(name).level for name in NOISY_LOGGERS}
    root.handlers = []

    setup_logging(level="DEBUG", logs_path=str(tmp_path))
    yield tmp_path

    for handler in root.handlers:
        handler.close()
    root.handlers = saved_handlers
    root.setLevel(saved_level)
    logging.setLogRecordFactory(saved_factory)
    logging.getLogger("uvicorn.access").setLevel(saved_access_level)
    for name, level in saved_noisy.items():
        logging.getLogger(name).setLevel(level)


def test_info_level_drops_debug_lines(logs: Path) -> None:
    logging.getLogger("backend.features.simulation.simulation").debug("detalhe do tick")

    assert "detalhe do tick" not in read(logs, "app.log")


def test_debug_level_writes_debug_to_app_and_area_logs(debug_logs: Path) -> None:
    logging.getLogger("backend.features.simulation.simulation").debug("detalhe do tick")

    assert "detalhe do tick" in read(debug_logs, "app.log")
    assert "detalhe do tick" in read(debug_logs, "simulation.log")


def test_debug_level_keeps_error_log_to_errors_only(debug_logs: Path) -> None:
    logging.getLogger("backend.routes").debug("só debug")
    logging.getLogger("backend.routes").error("falhou")

    content = read(debug_logs, "error.log")
    assert "falhou" in content
    assert "só debug" not in content


def test_debug_level_keeps_chatty_libraries_at_info(debug_logs: Path) -> None:
    logging.getLogger("engineio.server").debug("pacote 42")
    logging.getLogger("engineio.server").info("cliente conectou")

    content = read(debug_logs, "realtime.log")
    assert "pacote 42" not in content
    assert "cliente conectou" in content
