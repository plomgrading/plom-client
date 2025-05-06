# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2020 Andrew Rechnitzer
# Copyright (C) 2020-2023 Colin B. Macdonald
# Copyright (C) 2020 Victoria Schuster
# Copyright (C) 2025 Bryan Tanady

from PyQt6.QtGui import QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem


class CommandMoveItem(QUndoCommand):
    # Moves the graphicsitem. we give it an ID so it can be merged with other
    # commandmoves on the undo-stack.
    # Don't use this for moving text - that gets its own command.
    # Graphicsitems are separate from graphicsTEXTitems
    def __init__(self, xitem, delta):
        super().__init__()
        # The item to move
        self.xitem = xitem
        # The delta-position of that item.
        self.delta = delta
        self.setText("Move")

    def id(self) -> int:
        """An integer unique to the command class, used as prerequisite of commands merging"""
        return 101

    def redo(self):
        # Temporarily disable the item emitting "I've changed" signals
        self.xitem.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, False
        )
        # Move the object
        self.xitem.setPos(self.xitem.pos() + self.delta)
        # Re-enable the item emitting "I've changed" signals
        self.xitem.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True
        )

    def undo(self):
        # Temporarily disable the item emitting "I've changed" signals
        self.xitem.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, False
        )
        # Move the object back
        self.xitem.setPos(self.xitem.pos() - self.delta)
        # Re-enable the item emitting "I've changed" signals
        self.xitem.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True
        )

    def mergeWith(self, other) -> bool:
        """
        Overrides commands merging, base implementation: https://doc.qt.io/qt-6/qundocommand.html#mergeWith.

        Note: QUndoStack::push(cmd) first checks whether cmd has the same id with the command
        at the top of the stack. If they share same ids, qt will try to merge them by calling
        mergeWith. Ref: https://doc.qt.io/qt-6/qundostack.html#push

        Args:
            other: the other command to be merged.

        Returns:
            True if "self" and "other" commands are mergable, otherwise False.
        """
        # Most commands cannot be merged - make sure the moved items are the
        # same - if so then merge things.
        if self.xitem != other.xitem:
            return False

        # since we are merging commands, we need the cumulative effect so we don't
        # lose the effect of any command being merged.
        self.delta += other.delta
        return True


class UndoStackMoveMixin:
    """A mixin class to avoid copy-pasting this method over many *Item classes.
    Overrides the itemChange method.
    """

    def itemChange(self, change, value):
        """A callback function handling a change in QGraphicsItem's state.

        Args:
            change: type of state change.
            value: the value representing the change of state.
        """
        if (
            change == QGraphicsItem.GraphicsItemChange.ItemPositionChange
            and self.scene()
        ):
            # value represents last position (QPointF) after object is moved.
            delta = value - self.pos()
            command = CommandMoveItem(self, delta)
            self.scene().undoStack.push(command)
        return super().itemChange(change, value)
