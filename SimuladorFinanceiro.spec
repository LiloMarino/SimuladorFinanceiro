# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Simulador Financeiro

Este arquivo configura o PyInstaller para criar um executável standalone
que inclui o backend Flask e o frontend React compilado.
"""

import sys
from pathlib import Path

# Diretórios do projeto
project_root = Path('.').resolve()
backend_dir = project_root / 'backend'
frontend_static = backend_dir / 'static'
frontend_templates = backend_dir / 'templates'

# Coleta dados (arquivos não-Python que precisam ser incluídos)
datas = []

# Adiciona arquivos estáticos do frontend
if frontend_static.exists():
    datas.append((str(frontend_static), 'backend/static'))
    
# Adiciona templates do frontend
if frontend_templates.exists():
    datas.append((str(frontend_templates), 'backend/templates'))

# Adiciona outros arquivos de configuração que possam existir
config_files = [
    'example.env',
]

for config_file in config_files:
    config_path = project_root / config_file
    if config_path.exists():
        datas.append((str(config_path), '.'))

# Pacotes hidden (que o PyInstaller pode não detectar automaticamente)
hiddenimports = [
    'engineio.async_drivers.threading',
    'socketio',
    'flask_socketio',
    'dns',
    'dns.resolver',
    'peewee',
    'psycopg',
    'psycopg_binary',
    'sqlalchemy',
    'sqlalchemy.orm',
    'sqlalchemy.ext.declarative',
    'pandas',
    'numpy',
]

# Análise do script principal
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Remove duplicatas
pyz = PYZ(a.pure)

# Executável
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SimuladorFinanceiro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Mostra console para ver logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione o caminho para um .ico se tiver um ícone
)

# Coleta todos os arquivos em uma pasta
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SimuladorFinanceiro',
)
