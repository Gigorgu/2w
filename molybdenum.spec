# molybdenum.spec

# Импорт нужных функций
a = Analysis(
    ['molybdenum.py'],
    pathex=['.'],  
    binaries=[],
    datas=[('molybdenum/molybdenum.ico', 'molybdenum'),  
           ('molybdenum/molybdenum.png', 'molybdenum')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,  # Убираем шифрование
    noarchive=False,
)

# Создание исполняемого файла
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='molybdenum',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  
    icon='molybdenum/molybdenum.ico',  
)
