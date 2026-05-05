# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025-2026 Colin B. Macdonald
# Copyright (C) 2025 Ambre G.

"""Utilities for localization.

## Notes on how to updates:

# keeping things up-to-date after changing python code:
cd plomclient/client
pybabel extract chooser.py marker.py annotator.py about_dialog.py -o messages.pot
pybabel update -i messages.pot -d locales/
pybabel compile -d locales/


# new language
pybabel init -i messages.pot -d locales/ -l zh
"""

import gettext
import locale

# Issue #5130: uncomment this
# Hat-tip to https://github.com/slgobinath/SafeEyes/pull/706/files
# _translations = gettext.NullTranslations()


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
        "messages",
        localedir,
        fallback=True,  # fallback to original text if no translation found
        languages=[usr_locale[0]],
    )

    return _translations


# Issue #5130: uncomment this
# def translate(msg: str) -> str:
#     """Translate a string using the current translator."""
#     return _translations.gettext(msg)


# Issue #5130: ... and remove this placeholder
def translate(msg: str) -> str:
    return msg
