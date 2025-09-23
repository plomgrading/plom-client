# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 Colin B. Macdonald

from __future__ import annotations

from PyQt6.QtCore import Qt

from .key_wrangler import KeyEditDialog
from .key_help import KeyHelp


def test_KeyEditDialog_open_close_blank(qtbot) -> None:
    d = KeyEditDialog(None, label="my-action")
    qtbot.addWidget(d)
    d.reject()
    d = KeyEditDialog(None, label="my-action")
    qtbot.addWidget(d)
    d.accept()
    new_key = d.get_key()
    assert isinstance(new_key, str)
    assert new_key == ""


def test_KeyEditDialog_idempotent_in_to_out(qtbot) -> None:
    d = KeyEditDialog(None, label="my-action", current_key="a")
    qtbot.addWidget(d)
    d.accept()
    key = d.get_key()
    assert key.casefold() == "a"


def test_KeyEditDialog_change_input(qtbot) -> None:
    d = KeyEditDialog(None, label="my-action", current_key="a")
    qtbot.addWidget(d)
    qtbot.mouseClick(d.keyedit, Qt.MouseButton.LeftButton)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_B)
    d.accept()
    key = d.get_key()
    assert key.casefold() == "b"


def test_KeyEditDialog_no_modifier_keys_for_now(qtbot) -> None:
    """No ctrl-alt-etc for now, but could change in the future!"""
    d = KeyEditDialog(None, label="my-action", current_key="a")
    qtbot.addWidget(d)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_Control)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_Shift)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_B)
    d.accept()
    key = d.get_key()
    assert key.casefold() == "b"


def test_KeyEditDialog_backspace(qtbot) -> None:
    d = KeyEditDialog(None, label="my-action", current_key="a")
    qtbot.addWidget(d)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_Backspace)
    d.accept()
    key = d.get_key()
    assert key.casefold() == ""


def test_KeyEditDialog_restrict_to_list(qtbot) -> None:
    d = KeyEditDialog(None, label="my-action", legal="abc")
    qtbot.addWidget(d)
    qtbot.mouseClick(d.keyedit, Qt.MouseButton.LeftButton)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_D)
    d.accept()
    key = d.get_key()
    assert key.casefold() != "d"


def test_KeyHelp_basics(qtbot) -> None:
    d = KeyHelp(None, "default")
    qtbot.addWidget(d)
    d.accept()
    name = d.get_selected_keybinding_name()
    assert name == "default"
    assert d.get_custom_overlay() == {}


def test_KeyHelp_choose_new(qtbot) -> None:
    d = KeyHelp(None, "default")
    qtbot.addWidget(d)
    qtbot.mouseClick(d._keyLayoutCB, Qt.MouseButton.LeftButton)
    qtbot.keyClick(d._keyLayoutCB, Qt.Key.Key_Down)
    name = d.get_selected_keybinding_name()
    assert name.casefold() != "default"
    # Maintainer: could change if the internal ordering changes; just update test
    assert name.casefold() == "wasd"
    qtbot.keyClick(d._keyLayoutCB, Qt.Key.Key_Down)
    name = d.get_selected_keybinding_name()
    # Maintainer: could change if the internal ordering changes; just update test
    assert name.casefold() == "ijkl"
    d.accept()
