# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2021 Andrew Rechnitzer
# Copyright (C) 2019-2024, 2026 Colin B. Macdonald

from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QVBoxLayout,
)


# future translation support
def _(x: str) -> str:
    return x


class AddRemoveTagDialog(QDialog):
    """A dialog for managing the tags of a task.

    Args:
        parent (QWidget): who should parent this modal dialog.
        current_tags (list): the current tags to be laid out for
            deletion.
        tag_choices (list): any explicit choices for new tags, although
            free-form choices can also be made.

    Keyword Args:
        label (str): a short description of what we're tagging, such
            as ``"Paper 7"`` or ``32 questions``.  Used to construct
            dialog titles and prompts.

    Uses the usual `accept()` `reject()` mechanism but on accept you'll need
    to check `.return_values` which is a tuple of `("add", new_tag)` or
    `("remove", tag)`.  In either case the latter is a string.

    Note this dialog does not actually change the tag: the caller needs to
    do that.
    """

    def __init__(self, parent, current_tags, tag_choices, *, label=""):
        super().__init__(parent)

        if label:
            self.from_label = f" from {label}"
        else:
            self.from_label = ""
        self.setWindowTitle(f"Add/remove a tag{self.from_label}")
        self.return_values = None

        flay = QFormLayout()
        # flay = QVBoxLayout

        def remove_func_factory(button, tag):
            def remove_func():
                self.remove_tag(tag)

            return remove_func

        if not current_tags:
            flay.addRow(QLabel("<p><b>No current tags</b></p>"))
        else:
            flay.addRow(QLabel("Current tags:"))
            flay.addItem(
                QSpacerItem(
                    20,
                    4,
                    QSizePolicy.Policy.Minimum,
                    QSizePolicy.Policy.MinimumExpanding,
                )
            )
            for tag in current_tags:
                safe_tag = html.escape(tag)
                row = QHBoxLayout()
                row.addItem(QSpacerItem(48, 1))
                row.addWidget(QLabel(f"<big><em>{safe_tag}</em></big>"))
                b = QToolButton()
                b.setText("\N{ERASE TO THE LEFT}")
                # b.setText("\N{Cross Mark}")
                # b.setText("\N{Multiplication Sign}")
                b.setToolTip(f'Remove tag "{safe_tag}"')
                # important that this callback uses tag not safe_tag:
                b.clicked.connect(remove_func_factory(b, tag))
                row.addWidget(b)
                row.addItem(
                    QSpacerItem(
                        48,
                        1,
                        QSizePolicy.Policy.MinimumExpanding,
                        QSizePolicy.Policy.Minimum,
                    )
                )
                flay.addRow(row)
        flay.addItem(
            QSpacerItem(
                20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding
            )
        )
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        flay.addRow(line)
        flay.addItem(
            QSpacerItem(
                20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding
            )
        )
        q = QComboBox()
        q.setEditable(True)
        q.addItem("")
        normal_tags = [t for t in tag_choices if not t.startswith("@")]
        user_tags = [t for t in tag_choices if t.startswith("@")]
        q.addItems(normal_tags)
        q.insertSeparator(len(normal_tags) + 1)
        q.addItems(user_tags)
        flay.addRow("Add new tag", q)
        self.CBadd = q

        flay.addItem(
            QSpacerItem(
                20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding
            )
        )

        # TODO: cannot tab to OK
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        vlay = QVBoxLayout()
        vlay.addLayout(flay)
        vlay.addWidget(buttons)
        self.setLayout(vlay)

        buttons.accepted.connect(self.add_tag)
        buttons.rejected.connect(self.reject)
        self.CBadd.setFocus()

    def add_tag(self):
        self.return_values = ("add", self.CBadd.currentText())
        self.accept()

    def remove_tag(self, tag):
        safe_tag = html.escape(tag)
        msg = f"<p>Do you want to remove tag &ldquo;{safe_tag}&rdquo;?"
        title = f"Remove tag \u201c{safe_tag}\u201d{self.from_label}?"
        if QMessageBox.question(self, title, msg) != QMessageBox.StandardButton.Yes:
            return
        self.return_values = ("remove", tag)
        self.accept()


class DeferToDialog(QDialog):
    """Dialog to defer a task to other user(s).

    Args:
        parent (QWidget): who should parent this modal dialog.
        task: which task.
        lead_markers: a list of usernames of the lead markers.
        other_markers: a list of the usernames of non-lead markers.

    Keyword Args:
        checked: a list of usernames that should be pre-checked.
    """
    def __init__(
        self,
        parent,
        task: str,
        lead_markers: list[str],
        other_markers: list[str],
        *,
        checked: list[str] = [],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Defer task"))

        dialog_lay = QVBoxLayout()
        dialog_lay.addWidget(
            QLabel(_("<b>Who should mark task {task}?</b>").format(task=task))
        )

        self._checkboxes = []

        if lead_markers:
            w = QGroupBox(_("&Lead markers:"))
            w.setFlat(True)
            w.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            content = QFrame()
            lay = QVBoxLayout(content)
            for username in lead_markers:
                cb = QCheckBox(username)
                if username in checked:
                    cb.setChecked(True)
                lay.addWidget(cb)
                self._checkboxes.append(cb)
            lay = QVBoxLayout()
            if len(lead_markers) <= 8:
                lay.addWidget(content)
            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(content)
                scroll.setFrameShape(QFrame.Shape.NoFrame)
                lay.addWidget(scroll)
            lay.setContentsMargins(0, 0, 0, 0)
            w.setLayout(lay)
            dialog_lay.addWidget(w)

        if other_markers:
            if lead_markers:
                w = QGroupBox(_("Other &markers:"))
            else:
                w = QGroupBox(_("&Markers:"))
            w.setFlat(True)
            w.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            content = QFrame()
            lay = QVBoxLayout(content)
            for username in other_markers:
                cb = QCheckBox(username)
                if username in checked:
                    cb.setChecked(True)
                lay.addWidget(cb)
                self._checkboxes.append(cb)
            lay = QVBoxLayout()
            if len(other_markers) <= 5 or (
                len(other_markers) <= 8 and len(lead_markers) <= 4
            ):
                lay.addWidget(content)
            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(content)
                scroll.setFrameShape(QFrame.Shape.NoFrame)
                lay.addWidget(scroll)
            lay.setContentsMargins(0, 0, 0, 0)
            w.setLayout(lay)
            dialog_lay.addWidget(w)

        label = QLabel(
            _(
                "Task {task} will be dropped from your task list. "
                "Any of the users you tag here may receive the task."
            ).format(task=task)
        )
        label.setWordWrap(True)

        dialog_lay.addWidget(label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        dialog_lay.addWidget(buttons)
        self.setLayout(dialog_lay)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_chosen_users(self) -> list[str]:
        users = []
        for x in self._checkboxes:
            if x.isChecked():
                users.append(x.text().lstrip("@"))
        return users
