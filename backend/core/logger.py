import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Arquivo da área → prefixos de logger que escrevem nele. Área nova é uma linha.
# Cada linha vai ao app.log e, se a área tiver arquivo, também a ele.
AREA_LOGGERS: dict[str, tuple[str, ...]] = {
    "simulation.log": (
        "backend.features.simulation",
        "backend.features.variable_income",
        "backend.features.fixed_income",
    ),
    "realtime.log": (
        "backend.features.realtime",
        "backend.routes.realtime",
        "socketio",
        "engineio",
    ),
    "import.log": ("backend.features.import_data", "yfinance"),
    "database.log": (
        "backend.core.database",
        "backend.core.migration",
        "alembic",
        "sqlalchemy",
    ),
}

# Bibliotecas que tratam falha esperada como ERROR (ticker inexistente no yfinance):
# a linha fica no app.log e a mensagem de erro é a do código que chamou a biblioteca.
EXPECTED_FAILURE_LOGGERS = ("yfinance",)


class _PrefixFilter(logging.Filter):
    """Aceita o logger de nome igual ao prefixo ou descendente dele (`a.b` e `a.b.c`)."""

    def __init__(self, prefixes: tuple[str, ...], *, exclude: bool = False) -> None:
        super().__init__()
        self._prefixes = prefixes
        self._exclude = exclude

    def filter(self, record: logging.LogRecord) -> bool:
        matches = any(
            record.name == prefix or record.name.startswith(f"{prefix}.")
            for prefix in self._prefixes
        )
        return matches != self._exclude


def _file_handler(path: Path, formatter: logging.Formatter) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=10_000_000,  # ~10MB por arquivo
        backupCount=5,  # mantém 5 arquivos circulares
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    return handler


def setup_logging(
    *,
    level: str = "INFO",
    logs_path: str | Path = "logs",
    log_file: str = "app.log",
) -> None:
    """
    Configura logging global da aplicação.
    Deve ser chamado UMA vez no boot.
    """
    log_dir = Path(logs_path)
    log_dir.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.display_name = record.name.split(".")[-1].upper().replace("_", " ")
        return record

    logging.setLogRecordFactory(record_factory)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(display_name)s] [%(levelname)s] %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Evita handlers duplicados
    if root_logger.handlers:
        return

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Registro completo e cronológico
    root_logger.addHandler(_file_handler(log_dir / log_file, formatter))

    # Só os erros, com o traceback que `logger.exception` gera
    error_handler = _file_handler(log_dir / "error.log", formatter)
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(_PrefixFilter(EXPECTED_FAILURE_LOGGERS, exclude=True))
    root_logger.addHandler(error_handler)

    # Um arquivo por área
    for file_name, prefixes in AREA_LOGGERS.items():
        area_handler = _file_handler(log_dir / file_name, formatter)
        area_handler.addFilter(_PrefixFilter(prefixes))
        root_logger.addHandler(area_handler)

    # O uvicorn.access registra uma linha por requisição
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
