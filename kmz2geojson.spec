# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for KMZ to GeoJSON GUI application."""

block_cipher = None

a = Analysis(
    ['src/kmz2geojson/gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'lxml._elementpath',
        'lxml.etree',
        'bs4',
        'bs4.builder',
        'bs4.builder._lxml',
        'geojson',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'click',
        'pytest',
        'black',
        'flake8',
        'mypy',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'scipy',
    ],
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
    name='kmz2geojson',
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
    icon=None,
)
