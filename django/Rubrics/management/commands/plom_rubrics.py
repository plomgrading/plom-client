# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Colin B. Macdonald

import sys

if sys.version_info >= (3, 9):
    import importlib.resources as resources
else:
    import importlib_resources as resources

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib
# import tomlkit

# from tabulate import tabulate
from django.core.management.base import BaseCommand, CommandError

from Rubrics.services import RubricService


class Command(BaseCommand):
    """Commands for rubrics manipulation."""

    help = "Manipulate rubrics"

    def upload_demo_rubrics(self, *, numquestions=3):
        """Load some demo rubrics and upload to server.

        Keyword Args:
            numquestions (int): how many questions should we build for.
                TODO: get number of questions from the server spec if
                omitted.

        The demo data is a bit sparse: we fill in missing pieces and
        multiply over questions.
        """
        with open(resources.files("plom") / "demo_rubrics.toml", "rb") as f:
            rubrics_in = tomllib.load(f)
        rubrics_in = rubrics_in["rubric"]
        rubrics = []
        for rub in rubrics_in:
            if not rub.get("kind"):
                if rub["delta"] == ".":
                    rub["kind"] = "neutral"
                    rub["value"] = 0
                    rub["out_of"] = 0
                elif rub["delta"].startswith("+") or rub["delta"].startswith("-"):
                    rub["kind"] = "relative"
                    rub["value"] = int(rub["delta"])
                    rub["out_of"] = 0  # unused for relative
                else:
                    raise ValueError(f'not sure how to map "kind" for rubric:\n  {rub}')
            rub["display_delta"] = rub["delta"]
            rub.pop("delta")

            # TODO: didn't need to do this on legacy
            rub["username"] = "manager"
            rub["tags"] = ""

            # Multiply rubrics w/o question numbers, avoids repetition in demo file
            if rub.get("question") is None:
                for q in range(1, numquestions + 1):
                    r = rub.copy()
                    r["question"] = q
                    rubrics.append(r)
            else:
                rubrics.append(rub)
        service = RubricService()

        for rubric in rubrics:
            service.create_rubric(rubric)
        return len(rubrics)

    def add_arguments(self, parser):
        sub = parser.add_subparsers(
            dest="command",
            description="Various tasks about rubrics.",
        )

        sub.add_parser(
            "init",
            help="Initialize the rubric system with system rubrics",
            description="Initialize the rubric system with system rubrics.",
        )

        sp_wipe = sub.add_parser(
            "wipe",
            help="Erase all rubrics, including system rubrics (CAREFUL)",
            description="""
                Erase all rubrics, including system rubrics.
                BE CAREFUL: this will remove any rubrics that markers have added.
            """,
        )
        sp_wipe.add_argument(
            "--yes", action="store_true", help="Don't ask for confirmation."
        )

        sp_push = sub.add_parser(
            "push",
            help="Add pre-build rubrics",
            description="""
                Add pre-made rubrics to the server.  Your graders will be able to
                build their own rubrics but if you have premade rubrics you can
                add them here.
            """,
        )
        group = sp_push.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "file",
            nargs="?",
            help="""
                Upload a pre-build list of rubrics from this file.
                This can be a .json, .toml or .csv file.
            """,
        )
        group.add_argument(
            "--demo",
            action="store_true",
            help="Upload an auto-generated rubric list for demos.",
        )
        sp_pull = sub.add_parser(
            "pull",
            help="Get the current rubrics from the server.",
            description="Get the current rubrics from a running server.",
        )
        sp_pull.add_argument(
            "file",
            nargs="?",
            help="""
                Dump the current rubrics into a file,
                which can be a .toml, .json, or .csv.
                Defaults to .toml if no extension specified.
                TODO: or default to the screen if no file provided?
            """,
        )

    def handle(self, *args, **opt):
        if opt["command"] == "init":
            print("TODO: init")
        elif opt["command"] == "wipe":
            print("CAUTION: this will erase ALL rubrics on the server!")
            if not opt["yes"]:
                if input('  Are you sure? "y" to continue ') != "y":
                    return
            print("TODO: wipe")
        elif opt["command"] == "push":
            if opt["demo"]:
                print("uploading demo rubrics")
                N = self.upload_demo_rubrics(numquestions=3)
                print(f"added {N} rubrics")
                return
            print("TODO: push")
            print(opt["file"])
        elif opt["command"] == "pull":
            print("TODO: pull")
            print(opt["file"])
        else:
            self.print_help("manage.py", "plom_rubrics")
