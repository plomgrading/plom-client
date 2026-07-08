# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2021-2026 Colin B. Macdonald

import platform

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt6.QtWidgets import QMessageBox
from requests import __version__ as requests_version

from plom.common import __version__ as plom_common_version
from . import __version__
from .translations import translate as _


def show_about_dialog(parent):
    QMessageBox.about(
        parent,
        "Plom Client",
        _("""
            <h2>Plom Client {version}</h2>

            <p>
            <a href="https://plomgrading.org">https://plomgrading.org</a>
            </p>

            <p>Copyright &copy; 2018-2026 Andrew Rechnitzer,
            Colin B. Macdonald, and other contributors.</p>

            <p>Plom is Free Software, available under the GNU Affero
            General Public License version 3, or at your option, any
            later version.</p>

            <h3>Contributors</h3>

            <p>Plom would not have been possible without the help of
            <a href="https://gitlab.com/plom/plom/-/blob/main/CONTRIBUTORS">our
            contributors</a>.</p>

            <h3>System info</h3>
        """).format(version=__version__)
        + f"""
            <p>
            PyQt {PYQT_VERSION_STR} (Qt {QT_VERSION_STR})<br />
            Requests {requests_version}<br />
            Python {platform.python_version()}<br />
            {platform.platform()}<br />
            plom-common package: {plom_common_version}
            </p>
        """,
    )
