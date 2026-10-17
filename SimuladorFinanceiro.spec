# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# O servidor Postgres embarcado só existe no executável do Windows (`pnpm build:postgres`)
postgres_dist = Path('postgres_dist')
if sys.platform == 'win32' and os.environ.get('CI') and not postgres_dist.exists():
    raise SystemExit('Rode `pnpm build:postgres` antes de empacotar no Windows.')
postgres_datas = [(str(postgres_dist), 'backend/postgres')] if postgres_dist.exists() else []


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/static', 'backend/static'),
        ('backend/migrations', 'backend/migrations'),
    ] + postgres_datas,
    hiddenimports=[
        'psycopg_binary',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes = [
        # Dev / tooling
        'pyright',
        'ruff',
        'line_profiler',
        'radon',
        'snakeviz',

        # GUI
        'tcl',
        'tk',
        'tkinter',

        # Unused heavy libs (se não usadas)
        'beautifulsoup4',
        'matplotlib',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SimuladorFinanceiro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
