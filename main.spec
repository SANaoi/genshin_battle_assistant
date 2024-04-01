# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
a = Analysis(
    ['main.py'],
    pathex=['E:\\Anaconda\\envs\\wyswd\\Lib\\site-packages\\paddleocr', 'E:\\Anaconda\\envs\\wyswd\\Lib\\site-packages\\paddle\\libs'],
    binaries=[('E:\\Anaconda\\envs\\wyswd\\Lib\\site-packages\\paddle\\libs', '.')],
    datas=[("config","config"),("fonts","fonts"),("modules","modules")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
