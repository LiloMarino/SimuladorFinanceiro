# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for Simulador Financeiro.
Gera um executável que contém o backend e o frontend compilado.
"""

import sys
from pathlib import Path

block_cipher = None

# Diretório base do projeto
project_root = Path.cwd()

# Dados adicionais (frontend compilado)
datas = []

# Adiciona o frontend compilado se existir
static_dir = project_root / "backend" / "static"

if static_dir.exists():
    datas.append((str(static_dir), "backend/static"))

# Coleta todos os módulos do backend
hiddenimports = [
    "backend",
    "backend.config",
    "backend.core",
    "backend.core.database",
    "backend.core.logger",
    "backend.core.models",
    "backend.core.runtime",
    "backend.features",
    "backend.routes",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "socketio",
    "engineio",
    "fastapi",
    "starlette",
    "pydantic",
    "sqlalchemy",
    "peewee",
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="SimuladorFinanceiro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True para ver logs no console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
