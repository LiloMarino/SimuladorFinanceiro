"""Abre uma pasta no gerenciador de arquivos do sistema."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def open_in_file_manager(folder: Path) -> bool:
    """
    Abre `folder` no Explorer, no Finder ou no gerenciador do Linux. Devolve `False`
    quando a máquina não tem como abrir (sem `xdg-open`, sem interface gráfica).
    """
    folder.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        else:
            opener = shutil.which("xdg-open")
            if opener is None:
                return False
            subprocess.Popen([opener, str(folder)])
    except OSError:
        return False
    return True
