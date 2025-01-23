# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2022 Andrew Rechnitzer
# Copyright (C) 2020-2025 Colin B. Macdonald
# Copyright (C) 2024 Bryan Tanady

from pathlib import Path
from plom import __version__
import spellchecker

block_cipher = None
dict_path = spellchecker.__path__[0] + '/resources'

# Notes: https://github.com/Ousret/charset_normalizer/issues/253
a = Analysis(['plomclient/client/__main__.py'],
             pathex=['./'],
             binaries=[(dict_path, 'spellchecker/resources')],
             datas=[
                 ('plomclient/client/icons/*.svg', 'plomclient/client/icons'),
                 ('plomclient/client/icons/*.png', 'plomclient/client/icons'),
                 ('plomclient/client/cursors/*.png', 'plomclient/client/cursors'),
                 ('plomclient/client/ui_files/*.ui', 'plomclient/client/ui_files'),
                 ('plomclient/client/help_img/nav*.png', 'plomclient/client/help_img'),
                 ('plomclient/client/help_img/click_drag.gif', 'plomclient/client/help_img'),
                 ('plomclient/*keys.toml', 'plom'),
             ],
             hiddenimports=["charset_normalizer.md__mypyc"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# See https://gitlab.com/plom/plom/-/issues/1655
# target_arch='universal2',
# and then remove _arm64
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=f'PlomClient-{__version__}-macOS-arm64.bin',
          debug=False,
          strip=False,
          onefile=True,
          upx=True,
          runtime_tmpdir=None,
          console=False )

app = BUNDLE(exe,
             name=f'PlomClient-{__version__}-arm64.app',
             icon=None,
             bundle_identifier='org.plomgrading.PlomClient',
             version=__version__)
