import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(
    name: str = "APP", log_file: str = "app.log", level=logging.INFO
) -> logging.Logger:
    logger = logging.getLogger(name.split(".")[-1].upper().replace("_", " "))
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    )

    # Evita adicionar múltiplos handlers ao reiniciar
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = RotatingFileHandler(
            LOG_DIR / log_file,
            maxBytes=1_000_000,  # ~1MB por arquivo
            backupCount=5,  # mantém 5 arquivos circulares
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
