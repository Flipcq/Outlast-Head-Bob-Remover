# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Outlast-HeadBob-Remover.py'],
    pathex=[],
    binaries=[],
    datas=[('Outlast-HeadBob-Remover.ico', '.')],
    hiddenimports=['minilzo'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Outlast-HeadBob-Remover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Outlast-HeadBob-Remover.ico'],
)
