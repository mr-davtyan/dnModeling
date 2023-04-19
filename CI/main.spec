# -*- mode: python ; coding: utf-8 -*-

root_path = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))

block_cipher = None

a = Analysis([os.path.join(root_path, 'main.py')],
             pathex=[root_path],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
a.datas += [('resources/icon.ico', os.path.join(root_path, 'resources', 'icon.ico'),'DATA')]
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='dnModeling',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False ,
		  version=os.path.join(root_path, 'CI/version'),
		  icon=os.path.join(root_path, 'resources/icon.ico'),
		  )