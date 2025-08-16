# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 Deep Shah
# Copyright (C) 2025 Colin B. Macdonald

from typing import Any

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem

from . import CommandTool, UndoStackMoveMixin


class CommandSlantedBox(CommandTool):
    def __init__(self, scene, path) -> None:
        super().__init__(scene)
        self.obj = SlantedBoxItem(path, scene.style)
        self.setText("SlantedBox")

    @classmethod
    def from_pickle(cls, X, *, scene):
        assert cls.__name__.endswith(X[0]), f'Type "{X[0]}" mismatch: "{cls}"'
        X = X[1:]

        if len(X) != 1:
            raise ValueError("Wrong number of arguments for SlantedBox from_pickle")

        points_list = X[0]

        if len(points_list) < 4:
            raise ValueError("Not enough points to define a SlantedBox")

        p1 = QPointF(points_list[0]["x"], points_list[0]["y"])
        p2 = QPointF(points_list[1]["x"], points_list[1]["y"])
        p3 = QPointF(points_list[2]["x"], points_list[2]["y"])
        p4 = QPointF(points_list[3]["x"], points_list[3]["y"])

        path = QPainterPath(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p4)
        path.closeSubpath()

        return cls(scene, path)


class SlantedBoxItem(UndoStackMoveMixin, QGraphicsPathItem):
    def __init__(self, path, style) -> None:
        super().__init__()
        self.saveable = True
        self._path = path
        self.setPath(path)
        self.restyle(style)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def restyle(self, style):
        self.setPen(QPen(style["annot_color"], style["pen_width"]))
        self.setBrush(QBrush(style["box_tint"]))

    def pickle(self) -> list[Any]:
        elements = []
        for i in range(self._path.elementCount()):
            element = self._path.elementAt(i)
            if element.isMoveTo() or element.isLineTo():
                elements.append({"x": element.x + self.x(), "y": element.y + self.y()})

        return ["SlantedBox", elements]
