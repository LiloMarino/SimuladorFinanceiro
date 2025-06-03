import logging
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(
    name: str = "APP", log_file: str = "app.log", level=logging.INFO
) -> logging.Logger:
    logger = logging.getLogger(name.upper())
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
        file_handler = logging.FileHandler(
            os.path.join(LOG_DIR, log_file), encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
