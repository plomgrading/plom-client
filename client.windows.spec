# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2022 Andrew Rechnitzer
# Copyright (C) 2020-2024 Colin B. Macdonald
# Copyright (C) 2024 Bryan Tanady

from pathlib import Path
from plom import __version__
import spellchecker

block_cipher = None
dict_path = spellchecker.__path__[0] + '/resources'

a = Analysis(['plom/client/__main__.py'],
             pathex=['./'],
             binaries=[(dict_path, 'spellchecker/resources')],
             datas=[
                 ('plom/client/*.svg', 'plom/client'),
                 ('plom/client/*.png', 'plom/client'),
                 ('plom/client/icons/*.svg', 'plom/client/icons'),
                 ('plom/client/cursors/*.png', 'plom/client/cursors'),
                 ('plom/client/ui_files/*.ui', 'plom/client/ui_files'),
                 ('plom/client/help_img/nav*.png', 'plom/client/help_img'),
                 ('plom/client/help_img/click_drag.gif', 'plom/client/help_img'),
                 ('plom/*keys.toml', 'plom'),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='PlomClient-{}.exe'.format(__version__),
          debug=False,
          strip=False,
          onefile=True,
          upx=True,
          runtime_tmpdir=None,
          console=True )
