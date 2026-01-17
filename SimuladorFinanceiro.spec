# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('backend/static', 'backend/static')],
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
        'sqlacodegen',

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
