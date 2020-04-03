# -*- coding: utf-8 -*-

__copyright__ = "Copyright (C) 2020 Andrew Rechnitzer and Colin B. Macdonald"
__credits__ = "The Plom Project Developers"
__license__ = "AGPL-3.0-or-later"
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from plom import SpecVerifier, SpecParser


def checkDirectories():
    if all(
        os.path.isdir(d)
        for d in ["serverConfiguration", "specAndDatabase", "markedQuestions"]
    ):
        return True
    else:
        return False


def checkSpec(spec):
    # This runs after directory check, so we can try to load the local spec file.
    try:
        localSpec = SpecParser().spec
    except:
        print("Problem finding local spec file. Aborting.")
        return False

    # note - small and annoying difference between keys in local spec file and spec grabbed through messenger
    if (
        localSpec["name"] == spec["testName"]
        and localSpec["publicCode"] == spec["publicCode"]
    ):
        return True
    else:
        print(
            "Checking name and public-code in local-spec and sever-spec. They disagree. Aborting."
        )


def locationAndSpecCheck(spec):
    if checkDirectories():
        print("Required directories are present. Continuing")
    else:
        print(
            "Cannot find required directories. Aborting. Are you running this in the server directory?"
        )
        return False
    if checkSpec(spec):
        print("Local specification matches server specification. Continuing.")
    else:
        print(
            "The specification in the local directory does not match that supplied by the server. Aborting. Are you running this in the correct server directory?"
        )
        return False

    return True
