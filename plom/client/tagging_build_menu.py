# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Colin B. Macdonald

from typing import List, Union

from PyQt6.QtWidgets import (
    QPushButton,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QMenu,
    QRadioButton,
    QWidget,
    QWidgetAction,
)


class QMenuNextPrefDialog(QMenu):
    """Just want to store some extra instance variables inside a QMenu.

    This is all a bit "hack" and not in the good sense.
    """

    def __init__(self, parent, get_paper_fcn):
        super().__init__(parent)
        # list new instance vars in one place
        self._prefer_tags_combobox = None
        self._prefer_tags_radiobuttons = None
        self._prefer_above_action = None
        self._prefer_above_action_lineedit = None
        self._prefer_above_action_checkbox = None

        # TODO: rather yuck
        self.addAction("Get paper number...", get_paper_fcn)

        self.addSection("Options")
        q = QComboBox()
        q.setEditable(True)
        self._prefer_tags_combobox = q
        a = QWidgetAction(parent)
        frame = QFrame()
        vlay = QVBoxLayout(frame)
        b = QRadioButton("Prefer tasks tagged for me")
        # TODO: would like on-by-default: Issue #2253
        # b.setChecked(True)
        self._prefer_tags_radiobuttons = [b]
        vlay.addWidget(b)
        b = QRadioButton("Prefer tasks tagged")
        self._prefer_tags_radiobuttons.append(b)
        lay = QHBoxLayout()
        lay.addWidget(b)
        lay.addWidget(q)
        vlay.addLayout(lay)
        b = QRadioButton("No preference for tagged papers")
        b.setChecked(True)
        self._prefer_tags_radiobuttons.append(b)
        vlay.addWidget(b)
        a.setDefaultWidget(frame)
        self.addAction(a)

        a = QWidgetAction(parent)
        frame = QFrame()
        lay = QHBoxLayout(frame)
        c = QCheckBox("Prefer paper number \N{Greater-than Or Equal To}")
        c.setCheckable(True)
        c.setChecked(False)
        lay.addWidget(c)
        t = QLineEdit()
        t.setText("0")
        lay.addWidget(t)
        a.setDefaultWidget(frame)
        self._prefer_above_action = a
        self._prefer_above_action_lineedit = t
        self._prefer_above_action_checkbox = c
        self.addAction(a)

        a = QWidgetAction(parent)
        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.addStretch()
        _ = QPushButton("Ok")
        _.clicked.connect(self.close)
        lay.addWidget(_)
        a.setDefaultWidget(frame)
        self.addAction(a)

    def prefer_above(self) -> Union[None, int]:
        if not self._prefer_above_action_checkbox.isChecked():
            return None
        return int(self._prefer_above_action_lineedit.text())

    def update_tag_menu(self, all_tags: List[str]) -> None:
        q = self._prefer_tags_combobox
        cur = q.currentText()
        q.clear()
        q.addItems(all_tags)
        if cur:
            # TODO: we could restore the previous text only if its still a tag
            # if cur in all_tags:
            q.setCurrentText(cur)

    def get_preferred_tag(self, username: str) -> Union[None, str]:
        if self._prefer_tags_radiobuttons[0].isChecked():
            tag = "@" + username
        elif self._prefer_tags_radiobuttons[1].isChecked():
            tag = self._prefer_tags_combobox.currentText()
        else:
            tag = None
        return tag


def build_tagging_menu(parent: QWidget, get_paper_fcn) -> QMenuNextPrefDialog:
    """Build a pop-up menu/dialog thing for get-next preferences.

    Args:
        parent: the window that will popup this menu.
        get_paper_fcn: a function to call for the get particular
            paper number feature.

    Return:
        A QMenu with some monkey patched hackery: instance variables
        for manipulating the menu.  Probably it should be a subclass.
    """
    return QMenuNextPrefDialog(parent, get_paper_fcn)
