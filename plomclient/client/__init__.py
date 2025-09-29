# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020 Andrew Rechnitzer
# Copyright (C) 2020-2025 Colin B. Macdonald

"""Plom client and supporting functions."""

__copyright__ = "Copyright (C) 2018-2025 Andrew Rechnitzer, Colin B. Macdonald, et al"
__credits__ = "The Plom Project Developers"
__license__ = "AGPL-3.0-or-later"


# TODO: this should be a default and the PageScene should have a physical size.
ScenePixelHeight = 2000

# Also hardcoded in AppImageBuilder.yml
__version__ = "0.19.2.dev0"


from .marker import MarkerClient
from .identifier import IDClient
from .chooser import Chooser
from .random_marking_utils import do_rando_marking
from .random_identifying_utils import do_rando_identifying
from .image_view_widget import ImageViewWidget
from .task_table_view import TaskTableView


# what you get from "from plomclient.client import *"
__all__ = ["MarkerClient", "IDClient", "Chooser"]


import sys

if sys.version_info[0] == 2:
    raise RuntimeError("Plom requires Python 3; it will not work with Python 2")
