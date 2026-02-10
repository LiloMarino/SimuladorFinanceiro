import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    *,
    level: str = "INFO",
    logs_path: str = "logs",
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

    # Arquivo
    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=10_000_000,  # ~10MB por arquivo
        backupCount=5,  # mantém 5 arquivos circulares
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
