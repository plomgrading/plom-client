# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2024 Andrew Rechnitzer
# Copyright (C) 2020-2025 Colin B. Macdonald
# Copyright (C) 2023 Edith Coates
# Copyright (C) 2024 Aden Chan

"""Plom is Paperless Open Marking.

Plom creates multi-versioned tests, scans them, coordinates online
marking/grading, and returns them online.
"""

__copyright__ = "Copyright (C) 2018-2025 Andrew Rechnitzer, Colin B. Macdonald, et al"
__credits__ = "The Plom Project Developers"
__license__ = "AGPL-3.0-or-later"

# Also hardcoded in AppImageBuilder.yml
__version__ = "0.18.2.dev0"

Plom_API_Version = "114"
Plom_Legacy_Server_API_Version = "60"

from .tagging import (
    is_valid_tag_text,
    plom_valid_tag_text_pattern,
    plom_valid_tag_text_description,
)

# TODO: what you get from "from plomclient import *"
# __all__ = ["client"]
