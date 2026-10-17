"""Onde moram os arquivos do app: config.toml, .env, logs e os dados do banco embarcado."""

import os
import sys
from pathlib import Path

APP_DIR_NAME = "SimuladorFinanceiro"


def user_data_dir() -> Path:
    """Pasta do app na área do usuário, no padrão de cada sistema."""
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or home / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
    return base / APP_DIR_NAME


def app_files_dir() -> Path:
    """
    Pasta do config.toml, do .env e dos logs. No executável é a pasta do usuário, para
    que abrir o programa de qualquer lugar não deixe arquivos ao lado dele; rodando do
    código-fonte é a pasta de onde o comando roda.
    """
    if getattr(sys, "frozen", False):
        directory = user_data_dir()
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return Path()
