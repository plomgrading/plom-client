# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2021 Andrew Rechnitzer
# Copyright (C) 2019-2025 Colin B. Macdonald
# Copyright (C) 2024 Aden Chan

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor, QMouseEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QMenu,
    QTableView,
)


class TaskTableView(QTableView):
    """A table-view widget for local storage/presentation of tasks.

    It emits various signals including `annotateSignal` when the user
    hits enter or return.
    """

    # Note: marker.ui knows about this via a "plom/client/task_table_view.h" header

    # Marker will need to connect to these
    annotateSignal = pyqtSignal()
    tagSignal = pyqtSignal(str)
    claimSignal = pyqtSignal(str)
    deferSignal = pyqtSignal()
    reassignSignal = pyqtSignal(str)
    reassignToMeSignal = pyqtSignal(str)
    resetSignal = pyqtSignal(str)
    want_to_change_task = pyqtSignal(str)
    refresh_task_list = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        # User can sort, cannot edit, selects by rows.
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Resize to fit the contents
        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)

    def keyPressEvent(self, event):
        """Emit the annotateSignal on Return/Enter key, else pass the event onwards."""
        key = event.key()
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.annotateSignal.emit()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent | None) -> None:  # or bool?
        """Custom mouse event handler.

        By default, the selection of a row happens *before* we get an event.
        This makes it hard to undo the selection change, if the user rejects
        the change (due to unsaved work for example).

        So instead we have our own `want_to_change_task` signal that emit
        from here.  Note that we then *do not* move the selection.
        The application will have to call us back, if they would like to
        change tasks.

        TODO: up and down keys also move the selection, needs hacks there too.
        """
        if not event:
            return
        print(event)
        clicked_idx = self.indexAt(event.pos())
        print(clicked_idx)
        print(clicked_idx.isValid())
        if clicked_idx.isValid():
            r = clicked_idx.row()
            print(f"DEBUG: we have a click on a value index, row {r}")
            # TODO: here we muck around in the model, which we're probably not supposed to
            task = self.model().getPrefix(r)  # type: ignore[union-attr]
            print(f"DEBUG: this is task {task}")
            if event.button() == Qt.MouseButton.LeftButton:
                print(f"DEBUG: leftclick so emitting `want_to_change_task({task})`")
                self.want_to_change_task.emit(task)
                # print("delaying 1 seconds")
                # for __ in range(10):
                #     import time

                #     time.sleep(0.1)
                #     print("  wait")

                # return without passing the event onwards (which might
                # change the selection in an undesirable way)
                return
            else:
                # Ignore events from all other buttons (?)
                # TODO: strangely the right-click nonetheless opens
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:  # or bool?
        # TODO: we need to filter out drag events too: many clicks are actually short drags
        print("Debug: we have a mouseMoveEvent on task_table, discarding")
        return

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:  # or bool?
        # TODO: we need to filter out drag events too: many clicks are actually short drags
        print("Debug: we have a mouseReleaseEvent on task_table, discarding")
        return

    def contextMenuEvent(self, event: QContextMenuEvent | None) -> None:
        """Open a context menu with options for the currently highlighted task."""
        if not event:
            return

        menu = QMenu(self)

        clicked_idx = self.indexAt(event.pos())
        if clicked_idx.isValid():
            # TODO: what to do if invalid?  early return?
            r = clicked_idx.row()
            print(f"DEBUG: contextmenu: we have a click on a value index, row {r}")
            # TODO: here we muck around in the model, which we're probably not supposed to
            task = self.model().getPrefix(r)  # type: ignore[union-attr]
            print(f"DEBUG: this is task {task}")

            a = QAction("Annotate\tEnter", self)
            a.triggered.connect(self.annotateSignal.emit)
            menu.addAction(a)
            a = QAction(f"Tag task {task}", self)
            a.triggered.connect(lambda: self.tagSignal.emit(task))
            menu.addAction(a)
            a = QAction(f"Reset task {task}", self)
            a.triggered.connect(lambda: self.resetSignal.emit(task))
            menu.addAction(a)
            # TODO: this menu could be "context aware", not showing
            # claim if we already own it or defer if we don't
            a = QAction(f"Claim task {task}", self)
            a.triggered.connect(lambda: self.claimSignal.emit(task))
            menu.addAction(a)
            a = QAction(f"Reassign task {task}...", self)
            a.triggered.connect(lambda: self.reassignSignal.emit(task))
            menu.addAction(a)
            a = QAction(f"Reassign task {task} to me", self)
            a.triggered.connect(lambda: self.reassignToMeSignal.emit(task))
            menu.addAction(a)
            menu.addSeparator()

        a = QAction("Defer current task", self)
        a.triggered.connect(self.deferSignal.emit)
        menu.addAction(a)
        menu.addSeparator()
        a = QAction("Refresh task list", self)
        a.triggered.connect(self.refresh_task_list.emit)
        menu.addAction(a)
        menu.popup(QCursor.pos())
        event.accept()
