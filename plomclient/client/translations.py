# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 Colin B. Macdonald
# Copyright (C) 2025 Ambre G.

"""Utilities for localization."""

import gettext
import locale

# from pathlib import Path


# without translation _() is a no-op
# code below will (hopefully?) overwrite this
# but without this prototype, the `mypy` linter is unhappy.
# def _(x: str) -> str:
#     return x


# Hat-tip to https://github.com/slgobinath/SafeEyes/pull/706/files
_translations = gettext.NullTranslations()


def setup():
    global _translations

    # localization parameters
    # filename_stem = Path(__file__).stem
    localedir = "./plomclient/client/locales"
    usr_locale = locale.getlocale()  # pair (lang, encoding)

    print(usr_locale)
    # TODO: what if is?  mypy was concerned, hence the assert
    assert usr_locale[0] is not None

    _translations = gettext.translation(
        # TODO: how to support all our files?
        "chooser",
        localedir,
        fallback=True,  # fallback to original text if no translation found
        languages=[usr_locale[0]],
    )

    return _translations


def translate(msg: str) -> str:
    """Translate a string using the current translator."""
    return _translations.gettext(msg)
