# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py','image_operations.py','index.py'],
    pathex=[],
    binaries=[],
    datas=[('res/github.png','res'),('res/Q.png','res'),('res/保存.png','res'),('res/反色.png','res'),('res/放大.png','res'),('res/灰度-灰.png','res'),('res/机器视觉.png','res'),('res/目录.png','res'),('res/清理.png','res'),('res/缩小.png','res'),('res/图片.png','res'),('res/退出.png','res'),('res/文件夹.png','res'),('res/显示器.png','res'),('res/向右旋转.png','res'),('res/旋转.png','res'),],
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
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
