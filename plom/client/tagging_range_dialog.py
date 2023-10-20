# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Colin B. Macdonald

from typing import List, Tuple, Union

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
)


class TaggingAndRangeOptions(QDialog):
    """Just want to store some extra instance variables inside a QMenu.

    This is all a bit "hack" and not in the good sense.
    """

    def __init__(
        self,
        parent,
        prefer_tagged_for_me: bool,
        tag: Union[str, None],
        all_tags: List[str],
        min_paper_num: Union[str, None],
        max_paper_num: Union[str, None],
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Tagging and Range options")

        overall_layout = QVBoxLayout()

        q = QComboBox()
        q.setEditable(True)
        self._prefer_tags_combobox = q
        frame = QFrame()
        vlay = QVBoxLayout(frame)
        vlay.setContentsMargins(0, 0, 0, 0)
        b = QRadioButton("Prefer tasks tagged for me")
        # TODO: would like on-by-default: Issue #2253
        if prefer_tagged_for_me:
            b.setChecked(True)
        self._prefer_tags_radiobuttons = [b]
        vlay.addWidget(b)
        b = QRadioButton("Prefer tasks tagged")
        if not prefer_tagged_for_me and tag:
            b.setChecked(True)
        self._prefer_tags_radiobuttons.append(b)
        lay = QHBoxLayout()
        lay.addWidget(b)
        lay.addWidget(q)
        self._update_tag_menu(all_tags)
        if tag:
            q.setCurrentText(tag)

        vlay.addLayout(lay)
        b = QRadioButton("No preference for tagged papers")
        if not prefer_tagged_for_me and not tag:
            b.setChecked(True)
        self._prefer_tags_radiobuttons.append(b)
        vlay.addWidget(b)

        overall_layout.addWidget(frame)
        overall_layout.addSpacing(8)

        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)
        c = QCheckBox("Require")
        c.setCheckable(True)
        c.setChecked(False)
        lay.addWidget(c)
        t_min = QLineEdit()
        lay.addWidget(t_min, 2)
        _ = QLabel("\N{Less-than Or Equal To} paper number \N{Less-than Or Equal To}")
        lay.addWidget(_)
        # TODO: remove this sometime in 2024!
        c.setToolTip(
            "On legacy servers (commonly used in 2023) this is only"
            " a preference, not a requirement"
        )
        _.setToolTip(c.toolTip())
        t_max = QLineEdit()
        lay.addWidget(t_max, 2)
        # boo, hardcoded sizes in pixels :(
        # t_min.setFixedWidth(70)
        # t_max.setFixedWidth(70)
        if min_paper_num is not None:
            t_min.setText(str(min_paper_num))
        if max_paper_num is not None:
            t_max.setText(str(max_paper_num))
        if min_paper_num is not None or max_paper_num is not None:
            c.setChecked(True)
        self._minmax_action_min_lineedit = t_min
        self._minmax_action_max_lineedit = t_max
        self._minmax_action_checkbox = c
        overall_layout.addWidget(frame)
        overall_layout.addSpacing(8)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        overall_layout.addWidget(buttons)

        self.setLayout(overall_layout)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_papernum_range(self) -> Tuple[Union[None, int], Union[None, int]]:
        """Return a restricted range of paper numbers, either of which can be None.

        None indicates no restricion.
        """
        if not self._minmax_action_checkbox.isChecked():
            return None, None
        try:
            mn = int(self._minmax_action_min_lineedit.text())
        except ValueError:
            mn = None
        try:
            mx = int(self._minmax_action_max_lineedit.text())
        except ValueError:
            mx = None
        return mn, mx

    def _update_tag_menu(self, all_tags: List[str]) -> None:
        # we don't update once dialog open, probably unneeded
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
