# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 Colin B. Macdonald

from __future__ import annotations

from PyQt6.QtCore import Qt

from .key_wrangler import KeyEditDialog


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


def test_KeyEditDialog_restrict_to_list(qtbot) -> None:
    d = KeyEditDialog(None, label="my-action", legal="abc")
    qtbot.addWidget(d)
    qtbot.mouseClick(d.keyedit, Qt.MouseButton.LeftButton)
    qtbot.keyClick(d.keyedit, Qt.Key.Key_D)
    d.accept()
    key = d.get_key()
    assert key.casefold() != "d"
