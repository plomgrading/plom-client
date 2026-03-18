# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Colin B. Macdonald

from PyQt6.QtCore import Qt
from pytest import raises

from .tagging import DeferToDialog
from .useful_classes import InfoMsg


def test_defer(qtbot) -> None:
    d = DeferToDialog(None, "0123g4", ["user1"], ["user2", "user3"])
    d.show()
    qtbot.addWidget(d)
    # TODO: why doesn't this click work?
    # qtbot.mouseClick(d._checkboxes[0], Qt.MouseButton.LeftButton)
    # TODO: instead we use the spacebar
    qtbot.keyClick(d._checkboxes[0], Qt.Key.Key_Space)
    qtbot.keyClick(d._checkboxes[2], Qt.Key.Key_Space)
    d.accept()
    assert d.get_chosen_users() == ["user1", "user3"]


def test_defer_cancel(qtbot) -> None:
    d = DeferToDialog(None, "0123g4", ["user1"], ["user2", "user3"])
    d.show()
    qtbot.addWidget(d)
    d.reject()


def test_defer_cannot_defer_to_noone(qtbot, monkeypatch) -> None:
    def _raise(*args, **kwargs):
        raise RuntimeError()

    monkeypatch.setattr(InfoMsg, "exec", _raise)
    d = DeferToDialog(None, "0123g4", ["user1"], ["user2", "user3"])
    d.show()
    qtbot.addWidget(d)
    with raises(RuntimeError):
        d.accept()


def test_defer_prechecked_accept_ok(qtbot) -> None:
    d = DeferToDialog(None, "0123g4", ["user1"], ["user2", "user3"], checked="user2")
    d.show()
    qtbot.addWidget(d)
    d.accept()
    assert d.get_chosen_users() == ["user2"]


def test_defer_prechecked_and_toggle_some(qtbot) -> None:
    d = DeferToDialog(None, "0123g4", ["user1"], ["user2", "user3"], checked="user2")
    d.show()
    qtbot.addWidget(d)
    qtbot.keyClick(d._checkboxes[0], Qt.Key.Key_Space)
    qtbot.keyClick(d._checkboxes[1], Qt.Key.Key_Space)
    qtbot.keyClick(d._checkboxes[2], Qt.Key.Key_Space)
    d.accept()
    assert d.get_chosen_users() == ["user1", "user3"]
