# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2020 Andrew Rechnitzer
# Copyright (C) 2020 Colin B. Macdonald
# Copyright (C) 2020 Victoria Schuster

from PyQt5.QtCore import QTimer, QPropertyAnimation, pyqtProperty, Qt, QLineF, QPointF
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import (
    QUndoCommand,
    QGraphicsObject,
    QGraphicsLineItem,
    QGraphicsItem,
)

from plom.client.tools import CommandMoveItem


class CommandLine(QUndoCommand):
    def __init__(self, scene, pti, ptf):
        super().__init__()
        self.scene = scene
        self.pti = pti
        self.ptf = ptf
        # A line from pti(nitial) to ptf(inal)
        self.lineItem = LineItemObject(self.pti, self.ptf, scene.style)
        self.setText("Line")

    @classmethod
    def from_pickle(cls, X, *, scene):
        """Reconstruct from a serialized form."""
        assert cls.__name__.endswith(X[0]), 'Type "{}" mismatch: "{}"'.format(X[0], cls)
        X = X[1:]
        if len(X) != 4:
            raise ValueError("wrong length of pickle data")
        return cls(scene, QPointF(X[0], X[1]), QPointF(X[2], X[3]))

    def redo(self):
        """Item knows how to highlight on undo and redo."""
        self.lineItem.flash_redo()
        self.scene.addItem(self.lineItem.li)

    def undo(self):
        """Undo animation takes 0.5s, so trigger removal after 0.5s."""
        self.lineItem.flash_undo()
        QTimer.singleShot(200, lambda: self.scene.removeItem(self.lineItem.li))


class LineItemObject(QGraphicsObject):
    """An object wrapper around LineItem (or subclass) to handle animation."""

    def __init__(self, pti, ptf, style):
        super().__init__()
        self.li = LineItem(pti, ptf, style=style, parent=self)
        self.anim = QPropertyAnimation(self, b"thickness")

    def flash_undo(self):
        """Animate thin -> thick -> none."""
        self.anim.setDuration(200)
        self.anim.setStartValue(2)
        self.anim.setKeyValueAt(0.5, 6)
        self.anim.setEndValue(0)
        self.anim.start()

    def flash_redo(self):
        """Animate thin -> med -> thin."""
        self.anim.setDuration(200)
        self.anim.setStartValue(2)
        self.anim.setKeyValueAt(0.5, 4)
        self.anim.setEndValue(2)
        self.anim.start()

    @pyqtProperty(int)
    def thickness(self):
        return self.li.pen().width()

    @thickness.setter
    def thickness(self, value):
        pen = self.li.pen()
        pen.setWidthF(value)
        self.li.setPen(pen)


class LineItem(QGraphicsLineItem):
    def __init__(self, pti, ptf, style, parent=None):
        super().__init__()
        self.saveable = True
        self.animator = [parent]
        self.animateFlag = False
        self.pti = pti
        self.ptf = ptf
        self.setLine(QLineF(self.pti, self.ptf))
        self.setPen(QPen(style["annot_color"], style["pen_width"]))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # If the position changes then do so with an redo/undo command
            command = CommandMoveItem(self, value)
            self.scene().undoStack.push(command)
        return super().itemChange(change, value)

    def pickle(self):
        return [
            self.__class__.__name__.replace("Item", ""),  # i.e., "Line",
            self.pti.x() + self.x(),
            self.pti.y() + self.y(),
            self.ptf.x() + self.x(),
            self.ptf.y() + self.y(),
        ]

    def paint(self, painter, option, widget):
        if not self.scene().itemWithinBounds(self):
            # paint a bounding rectangle out-of-bounds warning
            painter.setPen(QPen(QColor(255, 165, 0), 8))
            painter.setBrush(QBrush(QColor(255, 165, 0, 128)))
            painter.drawRoundedRect(option.rect, 10, 10)
        super().paint(painter, option, widget)
