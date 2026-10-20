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
        "backend.routes.operation",
    ),
    "realtime.log": (
        "backend.features.realtime",
        "backend.routes.realtime",
        "socketio",
        "engineio",
    ),
    "import.log": ("backend.features.import_data", "yfinance"),
    "slow.log": ("backend.metrics",),
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

# Mensagem que também vai ao terminal: `logger.info("...", extra=TERMINAL)`. Sem isso, só
# WARNING ou acima aparece lá; o resto fica nos arquivos.
TERMINAL = {"terminal": True}

# Bibliotecas ficam em WARNING: o que elas dizem em INFO e DEBUG (consulta, pacote,
# requisição) não é do app. Quem quiser ver uma delas sobe o nível aqui.
LIBRARY_LEVELS = {
    "sqlalchemy": logging.WARNING,
    "engineio": logging.WARNING,
    "socketio": logging.WARNING,
    "urllib3": logging.WARNING,
    "asyncio": logging.WARNING,
}


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


class _SqlFilter(logging.Filter):
    """Descarta o SQL (`sqlalchemy.*` abaixo de WARNING): ele só vai ao `database.log`."""

    def filter(self, record: logging.LogRecord) -> bool:
        is_sql = record.name == "sqlalchemy" or record.name.startswith("sqlalchemy.")
        return not is_sql or record.levelno >= logging.WARNING


class _ConsoleFilter(logging.Filter):
    """O terminal recebe o que leva `TERMINAL` e tudo de WARNING para cima."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.WARNING or bool(
            getattr(record, "terminal", False)
        )


class _ConsoleFormatter(logging.Formatter):
    """Linha curta, sem traceback: o traceback completo fica no `error.log`."""

    def __init__(self, error_log: Path) -> None:
        super().__init__()
        self._error_log = error_log

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        if getattr(record, "terminal", False):
            return message

        line = (
            f"{self.formatTime(record, '%H:%M:%S')} {record.levelname} "
            f"{getattr(record, 'display_name', record.name)}: {message}"
        )
        if record.exc_info:
            line += f" (detalhes em {self._error_log})"
        return line


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
    debug: bool = False,
    sql: bool = False,
    logs_path: str | Path = "logs",
    log_file: str = "app.log",
) -> None:
    """
    Configura logging global da aplicação.
    Deve ser chamado UMA vez no boot.

    O raiz fica em INFO. No modo debug só o código do app (`backend.*`) sobe para DEBUG,
    e apenas os arquivos o recebem: o terminal nunca mostra DEBUG. `sql` (válido só com
    o debug ligado) liga a consulta do SQLAlchemy, que vai só ao `database.log`.
    """
    log_dir = Path(logs_path)
    log_dir.mkdir(parents=True, exist_ok=True)

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
    root_logger.setLevel(logging.INFO)
    logging.getLogger("backend").setLevel(logging.DEBUG if debug else logging.INFO)

    for name, library_level in LIBRARY_LEVELS.items():
        logging.getLogger(name).setLevel(library_level)
    if debug and sql:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    # O uvicorn.access registra uma linha por requisição: só o modo debug a guarda,
    # e só nos arquivos
    logging.getLogger("uvicorn.access").setLevel(
        logging.INFO if debug else logging.WARNING
    )

    # Evita handlers duplicados
    if root_logger.handlers:
        return

    # Terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(_ConsoleFormatter(log_dir / "error.log"))
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(_ConsoleFilter())
    root_logger.addHandler(console_handler)

    # Registro completo e cronológico
    app_handler = _file_handler(log_dir / log_file, formatter)
    app_handler.addFilter(_SqlFilter())
    root_logger.addHandler(app_handler)

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
