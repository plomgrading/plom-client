# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2021 Andrew Rechnitzer
# Copyright (C) 2021, 2023-2024, 2026 Colin B. Macdonald

from PyQt6.QtGui import QPainterPath, QUndoCommand

from .animations import AnimatingTempItemMixin, AnimatingTempPathItem


class CommandTool(QUndoCommand):
    """Handles the do/undo of edits to the PageScene.

    Subclasses will implement the ``obj`` which is the actual object to be
    drawn.  Commands are free to subclass ``QUndoCommand`` themselves
    rather than subclassing this ``CommandTool``.

    The :py:method:`redo` method handles both the initial drawing and any
    subsequent draw operations to due to undo/redo cycles.

    Thus far, the ``redo`` method should not create subcommand objects:
    in my experience, hard to debug and segfault behaviour comes from
    trying.  Instead, macros are instead created in PageScene.  This
    could be revisited in the future.

    Note both ``redo` and ``undo`` are overloaded from QUndoCommand and
    are part of the QUndoStack interface.
    """

    def __init__(self, scene) -> None:
        super().__init__()
        self.scene = scene
        # obj needs to be done by each tool
        # self.obj = QGraphicsItem()

        # a hack used to skip the next "redo" animation: typically so that an object
        # does not animate when the task is revisited.
        self._redo_skip_ani = False

    # pylint seems unhappy with the recursive of these constructors
    @classmethod
    def _from_pickle(cls, *args, **kwargs):  # -> CommandTool:
        """Low-level interface to restore an object a command from saved data.

        Subclasses should not re-implement this but they must
        implement `method:`from_pickle`.
        """
        instance = cls.from_pickle(*args, **kwargs)
        # To reproduce crash #5110, change to False and switch rapidly & repeatedly b/w papers
        instance._redo_skip_ani = True
        return instance

    @classmethod
    def from_pickle(cls, *args, **kwargs):  # -> CommandTool:
        """Abstract: subclasses must override this to restore themselves from a data."""
        raise NotImplementedError("subclasses must define this abstract method")

    def get_undo_redo_animation_shape(self) -> QPainterPath:
        """Return a shape appropriate for animating the undo/redo of an object.

        Returns:
            A QPainterPath used to draw the undo and redo temporary animations.
            Subclasses are free to return a different, perhaps simpler
            QPainterPath.  For example, :py:class:`CommandHighlight` returns
            its ``obj._original_path`` instead.  Another example would be a subclass
            that does not use the ``.obj`` instantance variable.
        """
        return self.obj.shape()

    def get_undo_redo_animation(
        self, *, backward: bool = False
    ) -> AnimatingTempItemMixin:
        """Return an object suitable for animating the undo/redo action.

        Returns:
            A QGraphicsItem, that also has the AnimatingTempItemMixin.
            This is a special object that will animate and then remove
            itself from the scene.
        """
        return AnimatingTempPathItem(
            self.get_undo_redo_animation_shape(), backward=backward
        )

    def redo_animation(self) -> None:
        """An animation of redoing something."""
        self.scene.addItem(self.get_undo_redo_animation())

    def redo(self) -> None:
        """Redo a command, putting it back in the scene with an animation.

        This is an overloaded method of QUndoCommand.
        """
        self.scene.addItem(self.obj)
        if not self._redo_skip_ani:
            self.redo_animation()
        self._redo_skip_ani = False

    def undo_animation(self) -> None:
        """An animation of undoing something."""
        self.scene.addItem(self.get_undo_redo_animation(backward=True))

    def undo(self) -> None:
        """Undo a command, removing from the scene with an animation.

        This is an overloaded method of QUndoCommand.
        """
        self.scene.removeItem(self.obj)
        self.undo_animation()
