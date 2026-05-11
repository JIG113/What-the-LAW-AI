# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

project_root = Path(SPECPATH).resolve().parent
entrypoint = str(project_root / 'run_server.py')

a = Analysis(
    [entrypoint],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.protocols', 'uvicorn.lifespan', 'fastapi', 'sqlmodel', 'app.main'],
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
    name='what_the_law_backend',
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
