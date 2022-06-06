# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2021-2022 Colin B. Macdonald

"""Tools for upload/downloading rubrics from Plom servers."""

import importlib.resources as resources
import json

# try to avoid importing Pandas unless we use specific functions: Issue #2154
# import pandas

import toml

from plom.create import with_manager_messenger


@with_manager_messenger
def download_rubrics(*, msgr):
    """Download a list of rubrics from a server.

    Keyword Args:
        msgr (plom.Messenger/tuple): either a connected Messenger or a
            tuple appropriate for credientials.

    Returns:
        list: list of dicts, possibly an empty list if server has no rubrics.
    """
    return msgr.MgetRubrics()


@with_manager_messenger
def download_rubrics_to_file(filename, *, msgr, verbose=True):
    """Download the rubrics from a server and save tem to a file.

    Args:
        filename (pathlib.Path): A filename to save to.  The extension is
            used to determine what format, supporting:
            `.json`, `.toml`, and `.csv`.
            If no extension is included, default to `.toml`.

    Keyword Args:
        msgr (plom.Messenger/tuple): either a connected Messenger or a
            tuple appropriate for credientials.

    Returns:
        None: but saves a file as a side effect.
    """
    if filename.suffix.casefold() not in (".json", ".toml", ".csv"):
        filename = filename.with_suffix(filename.suffix + ".toml")
    suffix = filename.suffix

    if verbose:
        print(f'Saving server\'s current rubrics to "{filename}"')
    rubrics = download_rubrics(msgr=msgr)

    with open(filename, "w") as f:
        if suffix == ".json":
            json.dump(rubrics, f, indent="  ")
        elif suffix == ".toml":
            toml.dump({"rubric": rubrics}, f)
        elif suffix == ".csv":
            import pandas

            df = pandas.json_normalize(rubrics)
            df.to_csv(f, index=False, sep=",", encoding="utf-8")
        else:
            raise NotImplementedError(f'Don\'t know how to export to "{filename}"')


def upload_rubrics_from_file(filename, *, msgr, verbose=True):
    """Load rubrics from a file and upload them to a server.

    Args:
        filename (pathlib.Path): A filename to load from.  Types  `.json`,
            `.toml`, and `.csv` are supported.  If no suffix is included
            we'll try to append `.toml`.

    Keyword Args:
        msgr (plom.Messenger/tuple): either a connected Messenger or a
            tuple appropriate for credientials.
    """
    if filename.suffix.casefold() not in (".json", ".toml", ".csv"):
        filename = filename.with_suffix(filename.suffix + ".toml")
    suffix = filename.suffix

    with open(filename, "r") as f:
        if suffix == ".json":
            rubrics = json.load(f)
        elif suffix == ".toml":
            rubrics = toml.load(f)["rubric"]
        elif suffix == ".csv":
            import pandas

            df = pandas.read_csv(f)
            df.fillna("", inplace=True)
            # TODO: flycheck is whining about this to_json
            rubrics = json.loads(df.to_json(orient="records"))
        else:
            raise NotImplementedError(f'Don\'t know how to import from "{filename}"')

    if verbose:
        print(f'Adding {len(rubrics)} rubrics from file "{filename}"')
    upload_rubrics(rubrics, msgr=msgr)


@with_manager_messenger
def upload_rubrics(rubrics, *, msgr):
    """Upload a list of rubrics to a server."""
    for rub in rubrics:
        # Generally we don't want to upload autogenerated rubrics: this HAL
        # test is not quite right as fact some autogenerated deltas and
        # "no marks", "full marks" are made by manager...  Issue #1494.
        if rub.get("username", None) == "HAL":
            continue
        # But we get around the above by uploading only relative and neutral
        # rubrics. No absolute or delta rubrics (as those are currently
        # autogenerated).  The exact logic may need tweaking in the future!
        if rub["kind"] not in ("neutral", "relative"):
            continue
        # TODO: ask @arechnitzer about this question_number discrepancy
        rub["question"] = rub["question_number"]
        msgr.McreateRubric(rub)


@with_manager_messenger
def upload_demo_rubrics(*, msgr, numquestions=3):
    """Load some demo rubrics and upload to server.

    Keyword Args:
        msgr (plom.Messenger/tuple): either a connected Messenger or a
            tuple appropriate for credientials.
        numquestions (int): how many questions should we build for.
            TODO: get number of questions from the server spec if
            omitted.

    The demo data is a bit sparse: we fill in missing pieces and
    multiply over questions.
    """
    rubrics_in = toml.loads(resources.read_text("plom", "demo_rubrics.toml"))
    rubrics_in = rubrics_in["rubric"]
    rubrics = []
    for rub in rubrics_in:
        if not hasattr(rub, "kind"):
            if rub["delta"] == ".":
                rub["kind"] = "neutral"
            elif rub["delta"].startswith("+") or rub["delta"].startswith("-"):
                rub["kind"] = "relative"
            else:
                raise ValueError(f'not sure how to map "kind" for rubric:\n  {rub}')
        # Multiply rubrics w/o question numbers, avoids repetition in demo file
        if not hasattr(rub, "question_number"):
            for q in range(1, numquestions + 1):
                r = rub.copy()
                r["question_number"] = q
                rubrics.append(r)
        else:
            rubrics.append(rub)
    upload_rubrics(rubrics, msgr=msgr)
    return len(rubrics)
