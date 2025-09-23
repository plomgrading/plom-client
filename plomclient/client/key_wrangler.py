# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2021 Andrew Rechnitzer
# Copyright (C) 2021-2025 Colin B. Macdonald

from __future__ import annotations

import logging
import sys
from copy import deepcopy
from typing import Any

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

import plomclient.client

from .useful_classes import WarnMsg

log = logging.getLogger("keybindings")


stringOfLegalKeys = "qwertyuiop[]asdfghjkl;'zxcvbnm,./"

actions_with_changeable_keys = [
    "prev-rubric",
    "next-rubric",
    "prev-tab",
    "next-tab",
    "prev-tool",
    "next-tool",
    "redo",
    "undo",
    "delete",
    "move",
    "zoom",
]


TODO_other_key_layouts = {
    "dvorak": {
        "redo": "Y",
        "undo": "I",
        "nextRubric": "E",
        "previousRubric": ".",
        "nextTab": "U",
        "previousTab": "O",
        "nextTool": "P",
        "previousTool": ",",
        "delete": "'",
        "move": "A",
        "zoom": ";",
    },
}


_keybindings_list: list[dict[str, Any]] = [
    {"name": "default", "file": "default_keys.toml"},
    {"name": "wasd", "file": "wasd_keys.toml"},
    {"name": "ijkl", "file": "ijkl_keys.toml"},
    {"name": "esdf_french", "file": "esdf_french_keys.toml"},
    {
        "name": "custom",
        "long_name": "Custom",
        "file": None,
        "about_html": """
          <p>Changing any key starts a custom overlay.</p>
          <p><b>Warning:</b> this is a beta feature; these customizations
            are <em>not saved</em> when you restart Plom.  Issue #2254.
          </p>
        """,
    },
]


def get_keybindings_list() -> list[dict[str, Any]]:
    it = deepcopy(_keybindings_list)
    for kb in it:
        f = kb["file"]
        if f is None:
            overlay = {}
        else:
            log.info("Loading keybindings from %s", f)
            with open(resources.files(plomclient.client) / f, "rb") as fh:
                overlay = tomllib.load(fh)
        metadata = overlay.pop("__metadata__", {})
        for k, v in metadata.items():
            kb[k] = v
        if kb["name"] != "default":
            kb["overlay"] = overlay
    return it


def get_keybinding_overlay(name: str) -> dict[str, Any]:
    """An overlay is has only the changes compared to the basic shortcut keys."""
    _keybindings_dict = {x["name"]: x for x in _keybindings_list}
    keymap = _keybindings_dict[name]
    f = keymap["file"]
    if name == "default" or f is None:
        overlay = {}
    else:
        log.info("Loading keybindings from %s", f)
        with open(resources.files(plomclient.client) / f, "rb") as fh:
            overlay = tomllib.load(fh)
    # note copy unnecessary as we have fresh copy from file
    overlay.pop("__metadata__", None)
    return overlay


def get_key_bindings(name: str, custom_overlay: dict = {}) -> dict:
    """Generate the keybindings from a name and or a custom overlay.

    Args:
        name: which keybindings to use.

    Keyword Args:.
        custom_overlay: if name is ``"custom"`` then take
            additional shortcut keys from this dict on top of the
            default bindings.  If name isn't ``"custom"`` then
            this input is ignored.

    Returns:
        dict: TODO explain the full keybindings.  The intention is
        not to store this but instead to store only the "overlay"
        and recompute this when needed.

    This function is fairly expensive and loads from disc every time.
    Could be refactored to cache the base data and non-custom overlays,
    if it is too slow.
    """
    f = "default_keys.toml"
    log.info("Loading keybindings from %s", f)
    with (resources.files(plomclient.client) / f).open("rb") as fh:
        default_keydata = tomllib.load(fh)
    default_keydata.pop("__metadata__")

    _keybindings_dict = {x["name"]: x for x in _keybindings_list}
    keymap = _keybindings_dict[name]
    if name == "custom":
        overlay = custom_overlay
    else:
        f = keymap["file"]
        if name == "default" or f is None:
            overlay = {}
        else:
            log.info("Loading keybindings from %s", f)
            with open(resources.files(plomclient.client) / f, "rb") as fh:
                overlay = tomllib.load(fh)
            overlay.pop("__metadata__", None)
        # keymap["overlay"] = overlay
    # note copy unnecessary as we have fresh copy from file
    return compute_keybinding_from_overlay(default_keydata, overlay, copy=False)


def compute_keybinding_from_overlay(base, overlay, *, copy=True):
    # loop over keys in overlay map and push updates into copy of default
    keydata = base
    if copy:
        keydata = deepcopy(keydata)
    for action, dat in overlay.items():
        keydata[action].update(dat)
    return keydata


class KeyEditDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        *,
        label: str,
        current_key: str | None = None,
        legal: str | None = None,
        info: str | None = None,
    ) -> None:
        """Dialog to edit a single key-binding for an action.

        Very simple; no shift-ctrl etc modifier keys.

        TODO: custom line edit eats enter and esc.

        Args:
            parent: widget to parent this dialog.

        Keyword Args:
            label: What action are we changing?
            current_key: the current key as a string to populate the
                dialog.  Can be blank or omitted.
            info: optional extra information to display.
            legal: keys that can entered, or defaults if omitted/empty.

        Returns:
            None
        """
        super().__init__(parent)
        vb = QVBoxLayout()
        vb.addWidget(QLabel(f"Change key for <em>{label}</em>"))
        if not legal:
            legal = stringOfLegalKeys
        _legal = [QKeySequence(c) for c in legal]
        self.keyedit = SingleKeyEdit(self, current_key, _legal)
        vb.addWidget(self.keyedit)
        if info:
            __ = QLabel(info)
            __.setWordWrap(True)
            vb.addWidget(__)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vb.addWidget(buttons)
        self.setLayout(vb)

    def get_key(self) -> str:
        """Get the key that was chosen, e.g., for callers after the dialog is done."""
        return self.keyedit.text()


class SingleKeyEdit(QLineEdit):
    def __init__(
        self, parent: QWidget, currentKey: str | None = None, legal: list = []
    ) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.legal = legal
        self.theKey = ""
        self.theCode = None
        if currentKey:
            self.theKey = currentKey
            self.theCode = QKeySequence(self.theKey)
            self.setText(currentKey)

    def keyPressEvent(self, event) -> None:
        keyCode = event.key()
        # no modifiers please
        if keyCode in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        ):
            return
        if keyCode in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self.backspace()
            self.theCode = None
            self.theKey = ""
            return
        if keyCode not in self.legal:
            return
        self.theCode = keyCode

    def keyReleaseEvent(self, event) -> None:
        # Note: theCode can be None here and we get an empty string
        # TODO: all this feels a bit circular and loopy to me
        self.theKey = QKeySequence(self.theCode).toString()
        self.setText(self.theKey)

    def setText(self, omega: str | None) -> None:
        self.theKey = omega
        if omega and len(omega) > 0:
            self.theCode = QKeySequence(omega)
        else:
            self.theCode = None
        super().setText(omega)


# TODO: no one seems to be using this class.  I dimly remember that it was
# salvaged from some previous code with the idea that it should be used
# one keymaps are saved to config files.
class KeyWrangler:
    def __init__(self):
        super().__init__()
        self.legalKeyCodes = [QKeySequence(c) for c in stringOfLegalKeys]
        self.actions = actions_with_changeable_keys

    def validate(self):
        actToCode = {}
        for act in self.actions:
            actToCode[act] = getattr(self, act + "Key").theCode
            if actToCode[act] is None:
                WarnMsg(self, f"Is invalid - '{act}' is missing a key").exec()
                return False
        # check for duplications
        for n, act in enumerate(self.actions):
            for k in range(0, n):
                if actToCode[act] == actToCode[self.actions[k]]:
                    WarnMsg(
                        self,
                        "Is invalid '{}' and '{}' have same key '{}'".format(
                            act,
                            self.actions[k],
                            QKeySequence(actToCode[act]).toString(),
                        ),
                    ).exec()
                    return False
        return True

    @classmethod
    def overlay_warnings(cls, overlay):
        """No duplicates in the overlay itself, although this allows duplicates in the overall keymap."""
        for k in overlay.keys():
            if k not in actions_with_changeable_keys:
                return f'overlay has invalid action "{k}"'
        # argh, keys like keyboard, not like dict indexing
        # TODO: removed [0] here; once this code is used, better ensure it works!
        all_keys = [v["keys"] for v in overlay.values()]
        if len(set(all_keys)) != len(all_keys):
            return "Two actions have the same key"
        return None
