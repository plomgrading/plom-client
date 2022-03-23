# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2020 Andrew Rechnitzer
# Copyright (C) 2020 Vala Vakilian
# Copyright (C) 2022 Colin B. Macdonald

"""Read student IDs using Scikit-learn"""

__copyright__ = "Copyright (C) 2020-2022 Andrew Rechnitzer and others"
__credits__ = "The Plom Project Developers"
__license__ = "AGPL-3.0-or-later"

from .model_utils import download_or_train_model
from .predictStudentID import compute_probabilities
from .idReader import lap_solver

__all__ = [
    "download_or_train_model",
    "compute_probabilities",
    "lap_solver",
]
