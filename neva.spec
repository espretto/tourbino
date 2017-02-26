# -*- mode: python -*-

import sys

# taken from the pyinstaller wiki
def Datafiles(*filenames, **kw):
    import os

    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)

        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
      datafile(filename, strip_path=strip_path)
      for filename in filenames
      if os.path.isfile(filename)
      )

block_cipher = None

a = Analysis(
  ['neva.py'],
  pathex=['C:\\Users\\test\\Desktop\\neva'],
  binaries=[],
  datas=[],
  hiddenimports=[],
  hookspath=[],
  runtime_hooks=[],
  excludes=[],
  win_no_prefer_redirects=False,
  win_private_assemblies=False,
  cipher=block_cipher
  )

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# workaround for windows
if sys.platform == 'win32':
    a.binaries += [
      ('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
      ('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')
    ]

exe = EXE(
  pyz,
  a.scripts,
  a.binaries,
  a.zipfiles,
  a.datas,
  Datafiles('client/index.html', strip_path=False),
  name='neva',
  debug=False,
  strip=False,
  upx=True,
  console=True
  )
