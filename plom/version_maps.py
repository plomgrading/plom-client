# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2019-2024 Andrew Rechnitzer
# Copyright (C) 2021-2025 Colin B. Macdonald

"""Tools for manipulating version maps."""

from __future__ import annotations


def undo_json_packing_of_version_map(
    vermap_in: dict[str, dict[str, int]],
) -> dict[int, dict[int, int]]:
    """JSON must have string keys; undo such to int keys for version map.

    Both the test number and the question number have likely been
    converted to strings by an evil JSON: we build a new dict-of-dicts
    with both converted explicitly to integers.

    Note: sometimes the dict-of-dicts is key'd by page number instead
    of question number.  This same function can be used in that case.
    """
    vmap = {}
    for t, question_vers in vermap_in.items():
        vmap[int(t)] = {int(q): v for q, v in question_vers.items()}
    return vmap
