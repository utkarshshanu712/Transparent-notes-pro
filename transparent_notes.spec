# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['transparent_notes.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\sanam\\OneDrive\\Desktop\\tnotes\\Transparent-notes-pro\\notebook.ico', '.')],
    hiddenimports=[],
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
    name='transparent_notes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    uac_admin=True,
    icon=['C:\\Users\\sanam\\OneDrive\\Desktop\\tnotes\\Transparent-notes-pro\\notebook.ico'],
    manifest='uac-manifest.xml',
)
