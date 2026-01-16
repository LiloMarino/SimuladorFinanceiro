import sys
from pathlib import Path


def format_percent(rate: float) -> str:
    return f"{rate * 100:.2f}%"


def resource_path(relative: str) -> Path:
    """Resolve caminho de recurso em dev e no executável PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative  # type: ignore
    return Path(relative).resolve()
