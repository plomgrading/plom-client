# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2025 Andrew Rechnitzer
# Copyright (C) 2020-2025 Colin B. Macdonald
# Copyright (C) 2020 Victoria Schuster
# Copyright (C) 2022 Joey Shi
# Copyright (C) 2024 Aden Chan
# Copyright (C) 2024 Aidan Murphy
# Copyright (C) 2024-2025 Bryan Tanady
# Copyright (C) 2025 Deep Shah

# a different kind of annotations... this is about code typing
from __future__ import annotations

from copy import deepcopy
from itertools import cycle
import logging
from pathlib import Path
from time import sleep
from typing import Any

import PIL.Image
from PyQt6.QtCore import QEvent, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QFont,
    QGuiApplication,
    QImage,
    QImageReader,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QTransform,
    QUndoStack,
)
from PyQt6.QtWidgets import (
    QGraphicsColorizeEffect,
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsOpacityEffect,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QMenu,
    QMessageBox,
    QToolButton,
)

from plomclient.plom_exceptions import PlomInconsistentRubric
from plomclient.misc_utils import pprint_score
from plomclient.rubric_utils import compute_score

from . import ScenePixelHeight
from .image_view_widget import mousewheel_delta_to_scale

# in some places we make assumptions that our view is this subclass
from .pageview import PageView

from .tools import DefaultPenWidth, AnnFontSizePts
from .tools import (
    CrossItem,
    DeltaItem,
    GhostComment,
    RubricItem,
    TextItem,
    TickItem,
)
from .tools import (
    CommandArrow,
    CommandArrowDouble,
    CommandBox,
    CommandEllipse,
    CommandImage,
    CommandDelete,
    CommandText,
    CommandRubric,
    CommandLine,
    CommandTick,
    CommandQMark,
    CommandCross,
    CommandPen,
    CommandHighlight,
    CommandPenArrow,
    CommandCrop,
    CommandRotatePage,
    CommandShiftPage,
    CommandRemovePage,
    CommandSlantedBox,
)
from .elastics import (
    which_horizontal_step,
    which_sticky_corners,
    which_classic_shortest_corner_side,
    which_centre_to_centre,
)
from .useful_classes import SimpleQuestion

from .draw_operations import (
    LineToolDrawer,
    BoxToolDrawer,
    RubricToolDrawer,
    TickToolDrawer,
    CrossToolDrawer,
    TextToolDrawer,
    DeleteToolDrawer,
    ZoomToolDrawer,
    CropToolDrawer,
    PenToolDrawer,
)


log = logging.getLogger("scene")

COMMAND_MAP = {
    "Arrow": CommandArrow,
    "ArrowDouble": CommandArrowDouble,
    "Box": CommandBox,
    "SlantedBox": CommandSlantedBox,
    "Crop": CommandCrop,
    "Cross": CommandCross,
    "Delete": CommandDelete,
    "Ellipse": CommandEllipse,
    "Highlight": CommandHighlight,
    "Image": CommandImage,
    "Line": CommandLine,
    "Pen": CommandPen,
    "PenArrow": CommandPenArrow,
    "QMark": CommandQMark,
    "Rubric": CommandRubric,
    "Text": CommandText,
    "Tick": CommandTick,
}


class ScoreBox(QGraphicsTextItem):
    """Indicate the current total mark in the top-left.

    Drawn with a rounded-rectangle border.
    """

    def __init__(
        self,
        style: dict[str, Any],
        fontsize,
        maxScore: int,
        score: float | None,
        question_label: str | None = None,
    ) -> None:
        """Initialize a new ScoreBox.

        Args:
            style: a dict of pen width, annotation colour, scale, etc.
            fontsize (int): A non-zero, positive font value.
            maxScore: A non-zero, positive integer maximum score.
            score: A current score for the paper, which can be zero,
                ``None``, or a positive float.
            question_label: how to display the name of this question to
                users, or `None` to display no label at the beginning
                of the score box.
        """
        super().__init__()
        self.score = score
        self.maxScore = maxScore
        self.question_label = question_label
        self.style = style
        self.setDefaultTextColor(self.style["annot_color"])
        font = QFont("Helvetica")
        # Note: PointSizeF seems effected by DPI on Windows (Issue #1071).
        # Strangely, it seems like setPixelSize gives reliable sizes!
        font.setPixelSize(round(1.25 * fontsize))
        self.setFont(font)
        # Not editable.
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setPos(0, 0)
        self._update_text()

    def _update_text(self):
        """Update the displayed text."""
        s = ""
        if self.question_label:
            s += self.question_label + ": "
        if self.score is None:
            s += "Unmarked"
        else:
            s += f"{pprint_score(self.score)} out of {self.maxScore}"
        self.setPlainText(s)

    def get_text(self):
        return self.toPlainText()

    def update_style(self):
        self.style = self.scene().style
        self.setDefaultTextColor(self.style["annot_color"])

    def changeScore(self, x: int | float | None) -> None:
        """Set the score to x.

        Args:
            x: a value or zero for no score yet assigned.

        Returns:
            None
        """
        self.score = x
        self._update_text()

    def changeMax(self, x: int) -> None:
        """Set the max possible mark to x.

        Args:
            x: A non-zero, positive new maximum mark.

        Returns:
            None
        """
        # set the max-mark.
        self.maxScore = x
        self._update_text()

    def paint(self, painter, option, widget):
        """Paint a rounded rectangle border around the scorebox text.

        Args:
            painter (QPainter): Current painter object.
            option (QStyleOptionGraphicsItem): Style options.
            widget (QWidget): Associated widgets.

        Returns:
            None

        Notes:
            Overrides parent method.
        """
        painter.setPen(QPen(self.style["annot_color"], self.style["pen_width"]))
        painter.setBrush(QBrush(QColor(255, 255, 255, 192)))
        painter.drawRoundedRect(option.rect, 10, 10)
        super().paint(painter, option, widget)


class UnderlyingRect(QGraphicsRectItem):
    """A simple white rectangle with dotted border.

    Used to add a nice white margin with dotted border around everything.
    """

    def __init__(self, rect):
        super().__init__()
        self.setPen(QPen(QColor("black"), 4, style=Qt.PenStyle.DotLine))
        self.setBrush(QBrush(QColor(249, 249, 249, 255)))
        self.setRect(rect)
        self.setZValue(-10)


class MaskingOverlay(QGraphicsItemGroup):
    """A transparent rectangular border to place over the images."""

    def __init__(self, outer_rect, inner_rect):
        super().__init__()
        self.outer_rect = outer_rect
        self.inner_rect = inner_rect
        # keep the original inner rectangle for uncropping.
        self.original_inner_rect = inner_rect

        # set rectangles for semi-transparent boundaries - needs some tmp rectangle.
        self.top_bar = QGraphicsRectItem(outer_rect)
        self.bottom_bar = QGraphicsRectItem(outer_rect)
        self.left_bar = QGraphicsRectItem(outer_rect)
        self.right_bar = QGraphicsRectItem(outer_rect)
        self.dotted_boundary = QGraphicsRectItem(inner_rect)
        transparent_paint = QBrush(QColor(249, 249, 249, 220))
        dotted_pen = QPen(QColor(0, 0, 0, 128), 2, style=Qt.PenStyle.DotLine)
        self.top_bar.setBrush(transparent_paint)
        self.bottom_bar.setBrush(transparent_paint)
        self.left_bar.setBrush(transparent_paint)
        self.right_bar.setBrush(transparent_paint)
        self.top_bar.setPen(QPen(Qt.PenStyle.NoPen))
        self.bottom_bar.setPen(QPen(Qt.PenStyle.NoPen))
        self.left_bar.setPen(QPen(Qt.PenStyle.NoPen))
        self.right_bar.setPen(QPen(Qt.PenStyle.NoPen))
        self.dotted_boundary.setPen(dotted_pen)
        # now set the size correctly
        self.set_bars()
        self.addToGroup(self.top_bar)
        self.addToGroup(self.bottom_bar)
        self.addToGroup(self.left_bar)
        self.addToGroup(self.right_bar)
        self.addToGroup(self.dotted_boundary)
        self.setZValue(-1)

    def crop_to_focus(self, crop_rect):
        self.inner_rect = crop_rect
        self.set_bars()
        self.update()

    def get_original_inner_rect(self):
        return self.original_inner_rect

    def set_bars(self):
        # reset the dotted boundary rectangle
        self.dotted_boundary.setRect(self.inner_rect)
        # set rectangles using rectangle defined by top-left and bottom-right points.
        self.top_bar.setRect(
            QRectF(
                self.outer_rect.topLeft(),
                QPointF(
                    self.outer_rect.topRight().x(),
                    self.inner_rect.topRight().y(),
                ),
            )
        )
        self.bottom_bar.setRect(
            QRectF(
                QPointF(
                    self.outer_rect.bottomLeft().x(),
                    self.inner_rect.bottomLeft().y(),
                ),
                self.outer_rect.bottomRight(),
            )
        )
        self.left_bar.setRect(
            QRectF(
                QPointF(
                    self.outer_rect.topLeft().x(),
                    self.inner_rect.topLeft().y(),
                ),
                self.inner_rect.bottomLeft(),
            )
        )
        self.right_bar.setRect(
            QRectF(
                self.inner_rect.topRight(),
                QPointF(
                    self.outer_rect.bottomRight().x(),
                    self.inner_rect.bottomRight().y(),
                ),
            )
        )


class UnderlyingImages(QGraphicsItemGroup):
    """Group for the images of the underlying pages being marked.

    Puts a dotted border around all the images.
    """

    def __init__(self, image_data: list[dict[str, Any]]):
        """Initialize a new series of underlying images.

        Args:
            image_data: each dict has keys 'filename', 'orientation',
                and 'visible' (and possibly others).  Only images with
                'visible' as True will be used.
                The list order determines the order: subject to change!
        """
        super().__init__()
        self.images = {}
        x = 0.0
        n = 0
        for data in image_data:
            if not data["visible"]:
                continue
            qir = QImageReader(str(data["filename"]))
            # deal with jpeg exif rotations
            qir.setAutoTransform(True)
            # In principle scaling in QImageReader or QPixmap can give better
            # zoomed out quality: https://gitlab.com/plom/plom/-/issues/1989
            # qir.setScaledSize(QSize(768, 1000))
            pix = QPixmap(qir.read())
            if pix.isNull():
                raise RuntimeError(f"Could not read an image from {data['filename']}")
            # after metadata rotations, we might have a further DB-level rotation
            rot = QTransform()
            # 90 means CCW, but we have a minus sign b/c of a y-downward coordsys
            rot.rotate(-data["orientation"])
            pix = pix.transformed(rot)
            img = QGraphicsPixmapItem(pix)
            # this gives (only) bilinear interpolation
            img.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            # works but need to adjust the origin of rotation, probably faster
            # img.setTransformOriginPoint(..., ...)
            # img.setRotation(img['orientation'])
            img.setPos(x, 0)
            sf = float(ScenePixelHeight) / float(pix.height())
            img.setScale(sf)
            # TODO: why not?
            # x += img.boundingRect().width()
            # help prevent hairline: subtract one pixel before converting
            x += sf * (pix.width() - 1.0)
            # TODO: don't floor here if units of scene are large!
            x = int(x)
            self.images[n] = img
            self.addToGroup(self.images[n])
            n += 1

        self.setZValue(-1)

    @property
    def min_dimension(self):
        return min(self.boundingRect().height(), self.boundingRect().width())


# things for nice rubric/text drag-box tool
# work out how to draw line from current point
# to nearby point on a given rectangle
# also need a minimum size threshold for that box
# in order to avoid drawing very very small boxes
# by accident when just "clicking"
# see #1435

minimum_box_side_length = 24


class PageScene(QGraphicsScene):
    """An extended QGraphicsScene for interacting with annotations on top of underlying images.

    Extend the graphics scene so that it knows how to translate
    mouse-press/move/release into operations on QGraphicsItems and
    QTextItems.
    """

    def __init__(self, parent, src_img_data, maxMark, question_label):
        """Initialize a new PageScene.

        Args:
            parent (Annotator): the parent of the scene.  Currently
                this *must* be an Annotator, because we call various
                functions from that Annotator.
            src_img_data (list[dict]): metadata for the underlying
                source images.  Each dict has (at least) keys for
               `filename` and `orientation`.
            maxMark(int): maximum possible mark.
            question_label (str/None): how to display this question, for
                example a string like "Q7", or `None` if not relevant.
        """
        super().__init__(parent)
        self.src_img_data = deepcopy(src_img_data)
        for x in self.src_img_data:
            # TODO: revisit moving this "visible" bit outside of PageScene
            # and dedupe the business of pagedata and src_img_data (Issue #3479)
            if "visible" not in x.keys():
                x["visible"] = True
                # log.warn(f'Hacked in an "visible": {x}')
        if not self.src_img_data:
            raise RuntimeError("Cannot start a pagescene with no visible pages")
        self.maxMark = maxMark
        self.score = None
        self._page_action_buttons = []
        # Tool mode - initially set it to "move"
        self.mode = "move"

        self.underImage = None
        self.underRect = None
        self.overMask = None
        self.buildUnderLay()

        self.whichLineToDraw_init()

        # initialise the undo-stack
        self.undoStack = QUndoStack()

        self._scale = 1.0

        self.scoreBox = None
        # Define standard pen, highlight, fill, light-fill
        self.set_annotation_color(QColor("red"))
        self.deleteBrush = QBrush(QColor(255, 0, 0, 16))
        self.zoomBrush = QBrush(QColor(0, 0, 255, 16))

        self.active_drawer = None

        # Add a ghost comment to scene, but make it invisible
        self.ghostItem = GhostComment(
            annot_scale=self._scale,
            display_delta="1",
            txt="blah",
            fontsize=AnnFontSizePts,
        )

        self._hideGhost()
        self.addItem(self.ghostItem)

        # cache some data about the currently selected rubric
        self.current_rubric = None

        # Build a scorebox and set it above all our other graphicsitems
        # so that it cannot be overwritten.
        # set up "k out of n" where k=current score, n = max score.
        self.scoreBox = ScoreBox(
            self.style, AnnFontSizePts, self.maxMark, self.score, question_label
        )
        self.scoreBox.setZValue(10)
        self.addItem(self.scoreBox)

        # make a box around the scorebox where mouse-press-event won't work.
        # make it fairly wide so that items pasted are not obscured when
        # scorebox updated and becomes wider
        self.avoidBox = self.scoreBox.boundingRect().adjusted(-16, -16, 64, 24)
        # holds the path images uploaded from annotator
        self.tempImagePath = None

        # Offset is physical unit which will cause the gap gets bigger when zoomed in.
        self.rubric_cursor_offset = 0

    def textUnderneathPoint(self, pt):
        """Check to see if any text-like object under point."""
        for under in self.items(pt):
            if (
                isinstance(under, DeltaItem)
                or isinstance(under, TextItem)
                or isinstance(under, RubricItem)
            ):
                return True
        return False

    def textUnderneathGhost(self):
        """Check to see if any text-like object under current ghost-text."""
        for under in self.ghostItem.collidingItems():
            if (
                isinstance(under, DeltaItem)
                or isinstance(under, TextItem)
                or isinstance(under, RubricItem)
            ):
                return True
        return False

    def mousePressEvent(self, event):
        if self.active_drawer:
            return self.active_drawer.mouse_press(event)

        if self.avoidBox.contains(event.scenePos()):
            return

        if self.mode == "line":
            self.active_drawer = LineToolDrawer(self, event)
            return
        elif self.mode == "box":
            self.active_drawer = BoxToolDrawer(self, event)
            return
        elif self.mode == "rubric":
            self.active_drawer = RubricToolDrawer(self, event)
            return
        elif self.mode == "tick":
            self.active_drawer = TickToolDrawer(self, event)
            return
        elif self.mode == "cross":
            self.active_drawer = CrossToolDrawer(self, event)
            return
        elif self.mode == "text":
            self.active_drawer = TextToolDrawer(self, event)
            return
        elif self.mode == "delete":
            self.active_drawer = DeleteToolDrawer(self, event)
            return
        elif self.mode == "zoom":
            self.active_drawer = ZoomToolDrawer(self, event)
            return
        elif self.mode == "crop":
            self.active_drawer = CropToolDrawer(self, event)
            return
        elif self.mode == "pen":
            self.active_drawer = PenToolDrawer(self, event)
            return

        elif self.mode == "move":
            self.views()[0].setCursor(Qt.CursorShape.ClosedHandCursor)
            super().mousePressEvent(event)
            return
        elif self.mode == "pan":
            self.views()[0].setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        elif self.mode == "image":
            if self.tempImagePath is not None:
                imageFilePath = self.tempImagePath
                command = CommandImage(self, event.scenePos(), QImage(imageFilePath))
                self.undoStack.push(command)
                self.tempImagePath = None
                _parent = self.parent()
                assert _parent is not None
                _parent.toMoveMode()

                msg = QMessageBox(_parent)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Image Information")
                msg.setText(
                    "You can double-click on an Image to modify its scale and border."
                )
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.active_drawer:
            return self.active_drawer.mouse_move(event)

        if self.mode == "rubric":
            self.ghostItem.setPos(event.scenePos())
            if not self.ghostItem.isVisible():
                self._updateGhost(self.current_rubric)
                self._exposeGhost()
            return
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Delegates mouse release events to an active drawer or simple tool."""
        if self.active_drawer:
            self.active_drawer.mouse_release(event)
            if self.active_drawer.is_finished:
                self.active_drawer = None
            return

        if self.mode == "move":
            self.views()[0].setCursor(Qt.CursorShape.OpenHandCursor)
            super().mouseReleaseEvent(event)
        elif self.mode == "pan":
            self.views()[0].setCursor(Qt.CursorShape.OpenHandCursor)
            page_view = self.views()[0]
            assert isinstance(page_view, PageView)
            page_view.setZoomSelector()
        else:
            super().mouseReleaseEvent(event)

    def buildUnderLay(self):
        if self.underImage:
            log.debug("removing underImage")
            self.removeItem(self.underImage)
        if self.underRect:
            self.removeItem(self.underRect)
            log.debug("removing underRect")
        if self.overMask:
            self.removeItem(self.overMask)
            log.debug("removing overMask")

        # build pixmap and graphicsitemgroup.
        self.underImage = UnderlyingImages(self.src_img_data)
        # a margin that surrounds the scanned images, with size related to the
        # minimum dimensions of the images, but never smaller than 512 pixels
        margin_width = max(512, 0.20 * self.underImage.min_dimension)
        margin_rect = QRectF(self.underImage.boundingRect()).adjusted(
            -margin_width, -margin_width, margin_width, margin_width
        )
        self.underRect = UnderlyingRect(margin_rect)
        # TODO: the overmask has wrong z-value on rebuild (?)
        self.overMask = MaskingOverlay(margin_rect, self.underImage.boundingRect())
        self.addItem(self.underRect)
        self.addItem(self.underImage)
        self.addItem(self.overMask)

        self.build_page_action_buttons()

        # Build scene rectangle to fit the image, and place image into it.
        self.setSceneRect(self.underImage.boundingRect())

    def remove_page_action_buttons(self):
        for h in self._page_action_buttons:
            self.removeItem(h)
            h.deleteLater()
        self._page_action_buttons = []

    def build_page_action_buttons(self):
        def page_delete_func_factory(n):
            def page_delete():
                self.dont_use_page_image(n)

            return page_delete

        def page_shift_func_factory(n, relative):
            def _page_shift():
                self.shift_page_image(n, relative)

            return _page_shift

        def page_rotate_func_factory(n, degrees):
            def _page_rotate():
                self.rotate_page_image(n, degrees)

            return _page_rotate

        self.remove_page_action_buttons()
        for n in range(len(self.underImage.images)):
            img = self.underImage.images[n]
            # b = QToolButton(text=f"Page {n}")
            # b = QToolButton(text="\N{Page}")
            # heaven == hamburger? works for me!
            button = QToolButton(text="\N{TRIGRAM FOR HEAVEN}")
            button.setToolTip(f"Options for page {n + 1}")
            button.setStyleSheet("QToolButton { background-color: #0000ff; }")
            # parenting the menu inside the scene
            m = QMenu(button)
            # TODO: nicer to parent by Annotr but unsupported (?) and unpredictable
            # m = QMenu(self.parent())
            _ = m.addAction("Remove this page", page_delete_func_factory(n))
            if len(self.underImage.images) == 1:
                _.setEnabled(False)
                _.setToolTip("Cannot remove lone page")
            _ = m.addAction("Shift left", page_shift_func_factory(n, -1))
            if n == 0:
                _.setEnabled(False)
            _ = m.addAction("Shift right", page_shift_func_factory(n, 1))
            if n == len(self.underImage.images) - 1:
                _.setEnabled(False)
            m.addAction(
                "\N{ANTICLOCKWISE OPEN CIRCLE ARROW} Rotate CCW",
                page_rotate_func_factory(n, 90),
            )
            m.addAction(
                "\N{CLOCKWISE OPEN CIRCLE ARROW} Rotate CW",
                page_rotate_func_factory(n, -90),
            )
            m.addAction("Flip", page_rotate_func_factory(n, 180))
            m.addSeparator()
            m.addAction("Find other pages...", self.parent().rearrangePages)
            button.setMenu(m)
            button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            proxy_widget = self.addWidget(button)
            proxy_widget.setZValue(20)
            # proxy_widget.setScale(0.9)
            proxy_widget.setOpacity(0.66)
            br = img.mapRectToScene(img.boundingRect())
            # wbr = h.mapRectToScene(h.boundingRect())
            # TODO: positioning via right-edge not correct w/ ItemIgnoresTransformations
            # maybe h.setTransformOriginPoint(...) would help?
            proxy_widget.setPos(
                # br.left() + br.width() - wbr.width(),
                br.left() + 0.86 * br.width(),
                br.top(),
            )
            proxy_widget.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations
            )
            proxy_widget.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren
            )
            self._page_action_buttons.append(proxy_widget)

    def getScore(self):
        return self.score

    def is_neutral_state(self) -> bool:
        """Has the mark has been changed from the unmarked state?

        No annotations is a neutral state.  Annotations that do not change the
        mark leave the scene in a neutral state.   Even neutral rubrics leave
        the scene in the neutral state.  But the use of any mark-changing
        annotation (currently non-neutral rubrics) will change the scene from
        neutral to non-neutral.

        Returns:
            True if the mark has been changed to a concrete value.
        """
        return self.getScore() is None

    def _refreshScore(self):
        # Note that this assumes that the rubrics are consistent as per currentMarkingState
        self.score = compute_score(self.get_rubrics(), self.maxMark)

    def refreshStateAndScore(self):
        """Compute the current score by adding up the rubric items and update state.

        This should be called after any change that might effect the score, but
        normally should shouldn't have to do that manually: for example, adding
        or removing items from the scene triggers this automatically.
        """
        self._refreshScore()
        # after score and state are recomputed, we need to update a few things
        # the scorebox
        if hasattr(self, "scoreBox") and self.scoreBox is not None:
            # if its too early, we may not yet have a scorebox
            self.scoreBox.changeScore(self.score)
        # update the rubric-widget
        self.parent().rubric_widget.updateLegalityOfRubrics()
        # also update the marklabel in the annotator - same text as scorebox
        self.parent().refreshDisplayedMark(self.score)

        # update the ghostcomment if in rubric-mode.
        if self.mode == "rubric":
            self._updateGhost(self.current_rubric)

    def addItem(self, X) -> None:
        # X: QGraphicsItem; but typing it so gives the Liskov error
        super().addItem(X)
        self.refreshStateAndScore()

    def removeItem(self, X) -> None:
        super().removeItem(X)
        self.refreshStateAndScore()

    def get_rubrics(self):
        """A list of the rubrics current used in the scene.

        Returns:
            list: a list of dicts, one for each rubric that is on the page.

        TODO: we will be calling this function quite a lot: maybe its worth
        caching or something.
        """
        rubrics = []
        for X in self.items():
            # check if object has "saveable" attribute and it is set to true.
            if getattr(X, "saveable", False):
                if isinstance(X, RubricItem):
                    rubrics.append(X.as_rubric())
        return rubrics

    def react_to_rubric_list_changes(self, rubric_list: list[dict[str, Any]]) -> None:
        """Someone has possibly changed the rubric list, check if any of our's are out of date.

        Currently, this doesn't actually update them, just flags them
        visually as needing updates.
        """
        if not rubric_list:
            log.info("Pagescene: reacting to rubric change: ignoring empty input")
            return
        log.info("Pagescene: reacting to rubric change...")
        rid_to_rub = {r["rid"]: r for r in rubric_list}
        num_update = 0
        for X in self.items():
            # check if object has "saveable" attribute and it is set to true.
            if getattr(X, "saveable", False):
                if isinstance(X, RubricItem):
                    old_rub = X.as_rubric()
                    rid = old_rub["rid"]
                    old_rev = old_rub.get("revision", None)
                    rub_lookup = rid_to_rub.get(rid, None)
                    if not rub_lookup:
                        log.error(
                            f"cannot find rubric {rid} in input list of"
                            f" length {len(rubric_list)}: maybe a bug?"
                        )
                        continue
                    new_rev = rub_lookup.get("revision", None)
                    if old_rev is None or new_rev is None:
                        log.warn(
                            f"[Is this legacy?] rubric rid={rid}"
                            " w/o 'revision' cannot be checked for updates"
                        )
                        continue
                    if old_rev == new_rev:
                        log.debug(f"   rid {rid} rev {old_rev} already up-to-date")
                        continue
                    s = f"rubric rid {rid} rev {old_rev} needs update to rev {new_rev}"
                    log.info(s)
                    # Change the visual appearance of the RubricItem
                    X.update_attn_state(s)
                    # TODO: future rubric button work might need the scene:
                    # X.update_attn_state(s, _scene=self)
                    num_update += 1
        if num_update:
            # TODO emit signal instead of assuming stuff about the parent
            msg = "Out-of-date rubrics detected: "
            rubrics_have = "rubrics have" if num_update > 1 else "rubric has"
            msg += f"{num_update} {rubrics_have} changed and needs updating."
            _parent = self.parent()
            if _parent:
                # MyPy is rightfully unsure parent is an Annotator:
                # # assert isinstance(_parent, Annotator)
                # but that's likely a circular import, so just add exception:
                _parent.update_attn_bar(msg=msg)  # type: ignore[attr-defined]

    def get_src_img_data(self, *, only_visible: bool = True) -> list[dict[str, Any]]:
        """Get the live source image data for this scene.

        Note you get the actual data, not a copy so careful if you mess with it!
        """
        r = []
        for x in self.src_img_data:
            if x["visible"] or not only_visible:
                r.append(x)
        return r

    def how_many_underlying_images_wide(self) -> int:
        """Count how many images wide the bottom layer is.

        Currently this is just the number of images (because we layout
        in one long row) but future revisions might support alternate
        layouts.
        """
        return len(self.get_src_img_data(only_visible=True))

    def how_many_underlying_images_high(self) -> int:
        """How many images high is the bottom layer.

        Currently this is always 1 because we align the images in a
        single row but future revisions might support alternate layouts.
        """
        return 1

    def reset_scale_factor(self):
        self._scale = 1.0
        self._stuff_to_do_after_setting_scale()

    def get_scale_factor(self):
        return self._scale

    def set_scale_factor(self, scale):
        """The scale factor scales up or down all annotations."""
        self._scale = scale
        self._stuff_to_do_after_setting_scale()

    def increase_scale_factor(self, r: float = 1.1) -> None:
        """Scale up the annotations by 110%.

        Args:
            r: the multiplicative factor, defaults to 1.1.
        """
        self._scale *= r
        self._stuff_to_do_after_setting_scale()

    def decrease_scale_factor(self, r: float = 1.1) -> None:
        """Scale down the annotations by 110%.

        Args:
            r: the scale is multiplied by 1/r.
        """
        self.increase_scale_factor(1.0 / r)

    def _refresh_ink_scaling(self) -> None:
        """Refresh both pen width and ink to reflect global scene's scale."""
        assert isinstance(self.style, dict)
        self.style["pen_width"] = self._scale * DefaultPenWidth
        self.ink: QPen = QPen(self.style["annot_color"], self.style["pen_width"])

    def _stuff_to_do_after_setting_scale(self):
        """Private method for tasks after changing scale.

        TODO: I'd like to move to a model where fontSize is constant
        and all things (line widths, fonts, etc) get multiplied by scale
        """
        # TODO: don't like this 1.25 hardcoded
        font = QFont("Helvetica")
        font.setPixelSize(round(1.25 * self._scale * AnnFontSizePts))
        self.scoreBox.setFont(font)
        assert isinstance(self.style, dict)
        self.style["scale"] = self._scale
        self.style["fontsize"] = self._scale * AnnFontSizePts
        self._refresh_ink_scaling()
        self.ghostItem.change_rubric_size(
            fontsize=int(self._scale * AnnFontSizePts), annot_scale=self._scale
        )

    def set_annotation_color(self, c) -> None:
        """Set the colour of annotations.

        Args:
            c (QColor/tuple): a QColor or an RGB triplet describing
                the new colour.
        """
        try:
            c = QColor(c)
        except TypeError:
            c = QColor.fromRgb(*c)
        style = {
            "annot_color": c,
            "pen_width": self._scale * DefaultPenWidth,
            "scale": self._scale,
            # TODO: 64 hardcoded elsewhere
            "highlight_color": QColor(255, 255, 0, 64),
            "highlight_width": 50,
            # light highlight for backgrounds
            "box_tint": QColor(255, 255, 0, 16),
            "fontsize": self._scale * AnnFontSizePts,
        }
        self.lightBrush = QBrush(style["box_tint"])
        self.highlight = QPen(style["highlight_color"], style["highlight_width"])
        # TODO: Issue 3514: this is an agrecious overwrite of a Qt built-in method
        self.style = style  # type: ignore[method-assign,assignment]
        self._refresh_ink_scaling()
        for X in self.items():
            # check if object has "restyle" function and if so then use it to set the colour
            if getattr(X, "restyle", False):
                # TODO: this loop catches rubric subobjects twice (minor for now)
                X.restyle(self.style)  # type: ignore[attr-defined]
        if self.scoreBox:
            self.scoreBox.update_style()

    def setToolMode(self, mode: str) -> None:
        """Sets the current toolMode.

        Args:
            mode: One of "rubric", "pan", "move" etc..

        Returns:
            None
        """
        # set focus so that shift/control change cursor
        self.views()[0].setFocus(Qt.FocusReason.TabFocusReason)

        self.mode = mode

        # To fix issues with changing mode mid-draw - eg #1540
        # trigger this
        self.stopMidDraw()

        # if current mode is not rubric, make sure the ghostcomment is hidden
        if self.mode != "rubric":
            self._hideGhost()
        else:
            # Careful, don't want it to appear at an old location
            gpt = QCursor.pos()  # global mouse pos
            vpt = self.views()[0].mapFromGlobal(gpt)  # mouse pos in view
            spt = self.views()[0].mapToScene(vpt)  # mouse pos in scene
            self.ghostItem.setPos(spt)
            self._exposeGhost()

        # if mode is "pan", allow the view to drag about, else turn it off
        if self.mode == "pan":
            self.views()[0].setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            # We want "NoDrag" but some reason toggling thru ScrollHandDrag
            # fixes the cursor Issue #3417.  I suspect the real issue is that
            # we are overfiltering mouse events, and not calling the super
            # mouse event handler somewhere (e.g., Issue #834).
            self.views()[0].setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.views()[0].setDragMode(QGraphicsView.DragMode.NoDrag)

    def get_nonrubric_text_from_page(self):
        """Get the current text items and rubrics associated with this paper.

        Returns:
            list: strings from each bit of text.
        """
        texts = []
        for X in self.items():
            if isinstance(X, TextItem):
                # if item is in a rubric then its 'group' will be non-null
                # only keep those with group=None to keep non-rubric text
                if X.group() is None:
                    texts.append(X.toPlainText())
        return texts

    def get_rubric_ids(self):
        """Get the rubric IDs associated with this scene.

        Returns:
            list: of IDs.
        """
        rubrics = []
        for X in self.items():
            if isinstance(X, RubricItem):
                rubrics.append(X.rubricID)
        return rubrics

    def countComments(self) -> int:
        """Counts current text items and comments associated with the paper.

        Returns:
            Total number of comments associated with this paper.
        """
        count = 0
        for X in self.items():
            if type(X) is TextItem:
                count += 1
        return count

    def countRubrics(self) -> int:
        """Counts current rubrics (comments) associated with the paper.

        Returns:
            Total number of rubrics associated with this paper.
        """
        count = 0
        for X in self.items():
            if type(X) is RubricItem:
                count += 1
        return count

    def get_current_rubric_id(self):
        """Last-used or currently held rubric.

        Returns:
            int/str/None: the ID of the last-used or currently held
                rubric.  None probably means we never had one.
        """
        if not self.current_rubric:
            return None
        return self.current_rubric["id"]

    def reset_dirty(self):
        # TODO: what is the difference?
        # self.undoStack.resetClean()
        self.undoStack.setClean()

    def is_dirty(self) -> bool:
        """Has the scene had annotations modified since it was last clean?

        Note that annotations from a older session should not cause this
        to return true.  If you have "saved" annotations you should call
        :meth:`reset_dirty` to ensure this property.
        """
        return not self.undoStack.isClean()

    def hasAnnotations(self) -> bool:
        """Checks for pickleable annotations.

        Returns:
            True if page scene has any pickle-able annotations.
            False otherwise.
        """
        for X in self.items():
            if getattr(X, "saveable", False):
                return True
        # no pickle-able items means no annotations.
        return False

    def getSaveableRectangle(self):
        # the rectangle is set to our current (potentially cropped) inner-rect of the masking
        br = self.overMask.mapRectToScene(self.overMask.inner_rect)
        # for context in cropped case, expand the crop-rect in each direction
        pad = max(128, 0.1 * min(br.height(), br.width()))
        br.adjust(-pad, -pad, pad, pad)
        # and then intersect that with the underlying-image rect
        br = br.intersected(self.underImage.boundingRect())

        # now potentially expand again for any annotations still outside
        for X in self.items():
            if getattr(X, "saveable", False):
                # now check it is inside the UnderlyingRect
                if X.collidesWithItem(
                    self.underRect, mode=Qt.ItemSelectionMode.ContainsItemShape
                ):
                    # add a little padding around things.
                    br = br.united(
                        X.mapRectToScene(X.boundingRect()).adjusted(-16, -16, 16, 16)
                    )
        return br

    def updateSceneRectangle(self):
        self.setSceneRect(self.getSaveableRectangle())
        self.update()

    def squelch_animations(self):
        """Wait for transient animations or perhaps hurry them along."""
        while True:
            have_anim = False
            for x in self.items():
                if getattr(x, "is_transcient_animation", False):
                    have_anim = True
                    # force an early removal of the animation
                    self.removeItem(x)
            if not have_anim:
                break
            # wait a little bit, processing events
            page_view = self.views()[0]
            assert isinstance(page_view, PageView)
            # yuck, what a parenting nightmare
            page_view._annotr.pause_to_process_events()
            log.warn("sleeping 50 ms waiting for animations to finish")
            sleep(0.05)

    def save(self, basename):
        """Save the annotated group-image.

        Args:
            basename (str/pathlib.Path): where to save, we will add a png
                or jpg extension to it.  If the file already exists, it
                will be overwritten.

        Returns:
            pathlib.Path: the file we just saved to, including jpg or png.
        """
        self.squelch_animations()

        # don't want to render these, but should we restore them after?
        # TODO: or setVisible(False) instead of remove?
        self.remove_page_action_buttons()

        self._hideGhost()

        # Get the width and height of the image
        br = self.getSaveableRectangle()
        self.setSceneRect(br)
        w = br.width()
        h = br.height()
        MINWIDTH = 1024  # subject to maxheight
        MAXWIDTH = 15999  # 16383 but for older imagemagick
        MAXHEIGHT = 8191
        MAX_PER_PAGE_WIDTH = 2000
        msg = []
        num_pages = self.how_many_underlying_images_wide()
        if w < MINWIDTH:
            r = (1.0 * w) / (1.0 * h)
            w = MINWIDTH
            h = w / r
            msg.append("Increasing bitmap width because of minimum width constraint")
            if h > MAXHEIGHT:
                h = MAXHEIGHT
                w = h * r
                msg.append("Constraining bitmap height by min width constraint")
        if w > num_pages * MAX_PER_PAGE_WIDTH:
            r = (1.0 * w) / (1.0 * h)
            w = num_pages * MAX_PER_PAGE_WIDTH
            h = w / r
            msg.append("Constraining bitmap width by maximum per page width")
        if w > MAXWIDTH:
            r = (1.0 * w) / (1.0 * h)
            w = MAXWIDTH
            h = w / r
            msg.append("Constraining bitmap width by overall maximum width")
        w = round(w)
        h = round(h)
        if msg:
            log.warning("{}: {}x{}".format(". ".join(msg), w, h))

        # Create an output pixmap and painter (to export it)
        oimg = QPixmap(w, h)
        exporter = QPainter(oimg)
        # Render the scene via the painter
        self.render(exporter)
        exporter.end()

        basename = Path(basename)
        pngname = basename.with_suffix(".png")
        jpgname = basename.with_suffix(".jpg")
        oimg.save(str(pngname))
        # Sadly no control over chroma subsampling which mucks up thin red lines
        # oimg.save(str(jpgname), quality=90)

        # im = PIL.Image.fromqpixmap(oimg)
        im = PIL.Image.open(pngname)
        im.convert("RGB").save(jpgname, quality=90, optimize=True, subsampling=0)

        jpgsize = jpgname.stat().st_size
        pngsize = pngname.stat().st_size
        log.debug("scene rendered: jpg/png sizes (%s, %s) bytes", jpgsize, pngsize)
        # For testing
        # if random.uniform(0, 1) < 0.5:
        if jpgsize < 0.9 * pngsize:
            pngname.unlink()
            return jpgname
        else:
            jpgname.unlink()
            return pngname

    def keyPressEvent(self, event):
        """Changes the focus or cursor based on key presses.

        Notes:
            Overrides parent method.
            Escape key removes focus from the scene.
            Changes the cursor in accordance with each tool's mousePress
            documentation.

        Args:
            event (QKeyEvent): The Key press event.

        Returns:
            None
        """
        # TODO: all this should somehow be an "alternative action" of the tool
        cursor = self.parent().cursor
        variableCursors = {
            "cross": (cursor["tick"], cursor["QMark"]),
            "line": (cursor["arrow"], cursor["DoubleArrow"]),
            "tick": (cursor["cross"], cursor["QMark"]),
            "box": (cursor["ellipse"], cursor["box"]),
            "pen": (cursor["Highlight"], cursor["DoubleArrow"]),
        }

        if self.mode in variableCursors:
            if event.key() == Qt.Key.Key_Shift:
                self.views()[0].setCursor(variableCursors.get(self.mode)[0])
            elif event.key() == Qt.Key.Key_Control:
                self.views()[0].setCursor(variableCursors.get(self.mode)[1])
            else:
                pass

        if event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            # also if in box,line,pen,rubric,text - stop mid-draw
            if self.mode in ["box", "line", "pen", "rubric", "text", "cross", "tick"]:
                self.stopMidDraw()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Changes cursors back to their standard cursor when keys are released.

        Args:
            event (QKeyEvent): the key release.

        Returns:
            None
        """
        variableCursorRelease = {
            "cross": self.parent().cursor["cross"],
            "line": self.parent().cursor["line"],
            "tick": self.parent().cursor["tick"],
            "box": self.parent().cursor["box"],
            "pen": self.parent().cursor["pen"],
        }
        if self.mode in variableCursorRelease:
            if self.views()[0].cursor() == variableCursorRelease.get(self.mode):
                pass
            else:
                self.views()[0].setCursor(variableCursorRelease.get(self.mode))
        else:
            pass

    def wheelEvent(self, event) -> None:
        if (
            QGuiApplication.queryKeyboardModifiers()
            == Qt.KeyboardModifier.ControlModifier
        ):
            s = mousewheel_delta_to_scale(event.delta())
            self.views()[0].scale(s, s)
            # sets the view rectangle and updates zoom-dropdown.
            # convince MyPy we have a PageView, not just any QGraphicsView
            page_view = self.views()[0]
            assert isinstance(page_view, PageView)
            page_view.setZoomSelector(True)
            self.zoomFlag = 0
            event.accept()

    def whichLineToDraw_init(self):
        witches = [
            which_horizontal_step,
            which_sticky_corners,
            which_classic_shortest_corner_side,
            which_centre_to_centre,
        ]
        self._witches = cycle(witches)
        self._whichLineToDraw = next(self._witches)

    def whichLineToDraw_next(self):
        self._whichLineToDraw = next(self._witches)
        print(f"Changing rubric-line to: {self._whichLineToDraw}")
        # TODO: can we generate a fake mouseMove event to force redraw?

    def whichLineToDraw(self, A, B):
        if A.intersects(B):
            # if boxes intersect then return a trivial path
            path = QPainterPath(A.topRight())
            path.lineTo(A.topRight())
            return path
        else:
            return self._whichLineToDraw(A, B)

    def mousePressImage(self, event) -> None:
        """Adds the selected image at the location the mouse is pressed and shows a message box with instructions.

        Args:
            event (QMouseEvent): given mouse click.

        Returns:
            None
        """
        if self.tempImagePath is not None:
            imageFilePath = self.tempImagePath
            command = CommandImage(self, event.scenePos(), QImage(imageFilePath))
            self.undoStack.push(command)
            self.tempImagePath = None
            _parent = self.parent()
            assert _parent is not None
            # set the mode back to move
            # MyPy is rightfully unsure parent is an Annotator:
            # # assert isinstance(_parent, Annotator)
            # but that's likely a circular import, so just add exception:
            _parent.toMoveMode()  # type: ignore[attr-defined]
            msg = QMessageBox(_parent)  # type: ignore[call-overload]
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Image Information")
            msg.setText(
                "You can double-click on an Image to modify its scale and border."
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    def dragEnterEvent(self, e):
        """Handles drag/drop events."""
        if e.mimeData().hasFormat("text/plain"):
            # User has dragged in plain text from somewhere
            e.acceptProposedAction()
        elif e.mimeData().hasFormat(
            "application/x-qabstractitemmodeldatalist"
        ) or e.mimeData().hasFormat("application/x-qstandarditemmodeldatalist"):
            # User has dragged in a rubric from the rubric-list.
            e.setDropAction(Qt.DropAction.CopyAction)
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        """Handles drag and move events."""
        e.acceptProposedAction()

    def dropEvent(self, e):
        """Handles drop events."""
        # all drop events should copy
        # - even if user is trying to remove rubric from rubric-list make sure is copy-action.
        e.setDropAction(Qt.DropAction.CopyAction)

        if e.mimeData().hasFormat("text/plain"):
            # Simulate a rubric click.
            # TODO: cannot simulate a rubric, we have no ID: Issue #2417
            txt = e.mimeData().text()
            # self.rubricText = txt
            # self.rubricDelta = "0"
            # self.rubricKind = "neutral"
            # self.mousePressRubric(e)
            log.error(
                f"Issue #2417: Drag-drop gave plain text but no way to add: {txt}"
            )
        elif e.mimeData().hasFormat(
            "application/x-qabstractitemmodeldatalist"
        ) or e.mimeData().hasFormat("application/x-qstandarditemmodeldatalist"):
            # Simulate a rubric click.
            self.mousePressRubric(e)
            # User has dragged in a rubric from the rubric-list.
            pass
        else:
            pass
        # After the drop event make sure pageview has the focus.
        self.views()[0].setFocus(Qt.FocusReason.TabFocusReason)

    def latexAFragment(self, *args, **kwargs):
        """Latex a fragment of text."""
        return self.parent().latexAFragment(*args, **kwargs)

    def event(self, event):
        """A fix for misread touchpad events on macOS.

        Args:
            event (QEvent): A mouse event.

        Returns:
            (bool) True if the event is accepted, False otherwise.
        """
        if event.type() in [
            QEvent.Type.TouchBegin,
            QEvent.Type.TouchEnd,
            QEvent.Type.TouchUpdate,
            QEvent.Type.TouchCancel,
        ]:
            # ignore the event
            event.accept()
            return True
        else:
            return super().event(event)

    def _debug_printUndoStack(self):
        """A helper method for debugging the undoStack."""
        c = self.undoStack.count()
        for k in range(c):
            print(k, self.undoStack.text(k))

    def is_user_placed(self, item) -> bool:
        """Tell me if the user placed it or if its some autogen junk.

        Let's try to isolate this unpleasantness in one place.

        Returns:
            True if this is a user-generated object, False if not.
        """
        from .tools import (
            ImageItem,
            EllipseItem,
            HighlightItem,
            LineItem,
            ArrowItem,
            ArrowDoubleItem,
            PenItem,
            PenArrowItem,
            QMarkItem,
        )

        if getattr(item, "saveable", None):
            return True
        if item in (
            CrossItem,
            DeltaItem,
            ImageItem,
            TextItem,
            TickItem,
            EllipseItem,
            HighlightItem,
            LineItem,
            ArrowItem,
            ArrowDoubleItem,
            PenItem,
            PenArrowItem,
            QMarkItem,
        ):
            return True
        # TODO more special cases?  I notice a naked QGraphicsLineItem used in elastic box...
        return False

    def find_items_right_of(self, x):
        keep = []
        log.debug(f"Searching for user-placed objects to the right of x={x}")
        for item in self.items():
            if not self.is_user_placed(item):
                log.debug(f"  nonuser: {item}")
                continue
            br = item.mapRectToScene(item.boundingRect())
            myx = br.left()
            if myx > x:
                log.debug(f"  found:   {item}: has x={myx} > {x}")
                keep.append(item)
            else:
                log.debug(f"  discard: {item}: has x={myx} <= {x}")
        return keep

    def move_some_items(self, L: list[QGraphicsItem], dx: float, dy: float) -> None:
        """Translate some of the objects in the scene.

        Args:
            L: list of objects to move.  TODO: not quite sure yet
                what is admissible here but we will try to filter out
                non-user-created stuff.
                TODO: typed as ``QGraphicsItem`` but maybe Groups too?
            dx: translation delta in the horizontal direction.
            dy: translation delta in the vertical direction.

        Wraps the movement of all objects in a compound undo item.  If
        you want this functionality without the macro (b/c you're doing
        your own, see the low-level :py:method:`_move_some_items`.
        """
        self.undoStack.beginMacro("Move several items at once")
        self._move_some_items(L, dx, dy)
        self.undoStack.endMacro()

    def _move_some_items(self, L: list, dx: float, dy: float) -> None:
        from .tools import CommandMoveItem

        log.debug(f"Shifting {len(L)} objects by ({dx}, {dy})")
        for item in L:
            if not self.is_user_placed(item):
                continue
            log.debug(f"got user-placed item {item}, shifting by ({dx}, {dy})")
            command = CommandMoveItem(item, QPointF(dx, dy))
            self.undoStack.push(command)

    def pickleSceneItems(self):
        """Pickles the saveable annotation items in the scene.

        Returns:
            (list[str]): a list containing all pickled elements.
        """
        lst = []
        for X in self.items():
            # check if object has "saveable" attribute and it is set to true.
            if getattr(X, "saveable", False):
                lst.append(X.pickle())
        return lst

    def unpickleSceneItems(self, lst):
        """Unpickles all items from the scene.

        Args:
            lst (list[list[str]]): a list containing lists of scene items'
                pickled information.

        Notes:
            Each pickled item type in lst is in a different format. Look in
            tools for more information.

        Returns:
            None, adds pickled items to the scene.

        Raises:
            ValueError: invalid pickle data.
        """
        # do this as a single undo macro.
        self.undoStack.beginMacro("Unpickling scene items")

        # clear all items from scene.
        for X in self.items():
            # X is a saveable object then it is user-created.
            # Hence it can be deleted, otherwise leave it.
            if getattr(X, "saveable", False):
                command = CommandDelete(self, X)
                self.undoStack.push(command)
        # now load up the new items
        for X in lst:
            # Special hack for legacy server data:
            if X[0] == "GroupDeltaText":
                assert len(X) == 10
                r = {
                    "rid": int(X[3]),
                    "kind": X[4],
                    "value": X[5],
                    "out_of": X[6],
                    "display_delta": X[7],
                    "text": X[8],
                    "tags": X[9],
                }
                log.info("Rewrote legacy GroupDeltaText %d as a Rubric", r["rid"])
                X = ["Rubric", X[1], X[2], r]
            CmdCls = COMMAND_MAP.get(X[0])
            if CmdCls and getattr(CmdCls, "from_pickle", None):
                # TODO: use try-except here?
                self.undoStack.push(CmdCls.from_pickle(X, scene=self))
                continue
            log.error("Could not unpickle whatever this is:\n  {}".format(X))
            raise ValueError("Could not unpickle whatever this is:\n  {}".format(X))
        # now make sure focus is cleared from every item
        for X in self.items():
            X.clearFocus()
        # finish the macro
        self.undoStack.endMacro()

    def shift_page_image(self, n: int, relative: int) -> None:
        """Shift a page left or right on the undostack.

        Currently does not attempt to adjust the positions of annotation items.

        Args:
            n: which page, indexed from 0.
            relative: +1 or -1, but no error checking is done and its
                not defined what happens for other values.

        Returns:
            None
        """
        if relative > 0:
            # not obvious we need a macro, but maybe later we move annotations with it
            macroname = f"Page {n} shift right {relative}"
        else:
            macroname = f"Page {n} shift left {abs(relative)}"
        self.undoStack.beginMacro(macroname)

        # like calling _shift_page_image_only but covered in undo sauce
        cmd = CommandShiftPage(self, n, n + relative)
        self.undoStack.push(cmd)

        # TODO: adjust annotations, then end the macro
        self.undoStack.endMacro()

    def _idx_from_visible_idx(self, n: int) -> int:
        """Find the index in the src_img_data for the nth visible image.

        We often want to operate on the src_img_data, for a given visible image.
        This helper routine helps us find the right index.

        Args:
            n: the nth visible image, indexed from 0.

        Returns:
            The corresponding 0-based index into the src_img_data.

        Raises:
            KeyError: cannot find such.
        """
        m = -1
        for idx, x in enumerate(self.src_img_data):
            if x["visible"]:
                m += 1
            if m == n:
                return idx
        raise KeyError(f"no row in src_img_data visible at n={n}")

    def _id_from_visible_idx(self, n: int) -> int:
        """Find the id from the src_img_data for the nth visible image.

        We often want to operate on the src_img_data, for a given visible image.
        This helper routine helps us find the right index.

        Args:
            n: the nth visible image, indexed from 0.

        Returns:
            The corresponding `id` which is one of the keys of the
            rows in the src_img_data.

        Raises:
            KeyError: cannot find such.
        """
        n_idx = self._idx_from_visible_idx(n)
        return self.src_img_data[n_idx]["id"]

    def _shift_page_image_only(self, n: int, m: int) -> None:
        n_idx = self._idx_from_visible_idx(n)
        m_idx = self._idx_from_visible_idx(m)
        d = self.src_img_data.pop(n_idx)
        self.src_img_data.insert(m_idx, d)
        # self.parent().report_new_or_permuted_image_data(self.src_img_data)
        self.buildUnderLay()

    def rotate_page_image(self, n: int, degrees: int) -> None:
        """Rotate a page on the undostack, shifting objects on other pages appropriately.

        The rotations happen within a single undoable "macro".

        Args:
            n: which page, indexed from 0.
            degrees: rotation angle, positive means CCW.

        Returns:
            None.
        """
        self.undoStack.beginMacro(f"Page {n} rotation {degrees} and item move")

        # get old page width and location, select rightward objects to shift
        img = self.underImage.images[n]
        br = img.mapRectToScene(img.boundingRect())
        loc = br.right()
        w = br.width()
        log.debug(f"About to rotate img {n} by {degrees}: right pt {loc} w={w}")
        stuff = self.find_items_right_of(loc)

        # like calling _rotate_page_image_only but covered in undo sauce
        cmd = CommandRotatePage(self, n, degrees)
        self.undoStack.push(cmd)

        # shift previously-selected rightward annotations by diff in widths
        img = self.underImage.images[n]
        br = img.mapRectToScene(img.boundingRect())
        log.debug(f"After rotation: old width {w} now {br.width()}")
        # enqueues appropriate CommmandMoves
        self._move_some_items(stuff, br.width() - w, 0)

        self.undoStack.endMacro()

    def _rotate_page_image_only(self, n: int, degrees: int) -> None:
        """Low-level rotate page support: only rotate page, no shifts."""
        # do the rotation in metadata and rebuild
        n_idx = self._idx_from_visible_idx(n)
        self.src_img_data[n_idx]["orientation"] += degrees
        # self.parent().report_new_or_permuted_image_data(self.src_img_data)
        self.buildUnderLay()

    def dont_use_page_image(self, n: int) -> None:
        imgid = self._id_from_visible_idx(n)
        img = self.underImage.images[n]
        # the try behaves like "with highlighted_pages([n]):"
        self.highlight_pages([n], "darkred")
        try:
            d = SimpleQuestion(
                self.parent(),  # self.addWidget(d) instead?
                """Remove this page? <ul>\n
                  <li>You can undo or find the page again using
                  <em>Rearrange Pages</em>.</li>\n
                <li>Existing annotations will shift left or right.</li>\n
                </ul>""",
                "Are you sure you want to remove this page?",
            )
            # h = self.addWidget(d)
            # Not sure opening a dialog from the scene is wise
            if d.exec() == QMessageBox.StandardButton.No:
                return
        finally:
            self.highlight_pages_reset()

        self.undoStack.beginMacro(f"Page {n} remove and item move")

        br = img.mapRectToScene(img.boundingRect())
        log.debug(f"About to delete img {n}: left={br.left()} w={br.width()}")

        if n == len(self.underImage.images) - 1:
            # special case when deleting right-most image
            loc = br.left()
            go_left = False
        else:
            # shift existing annotations leftward
            loc = br.right()
            go_left = True
        stuff = self.find_items_right_of(loc)

        # like calling _set_visible_page_image but covered in undo sauce
        cmd = CommandRemovePage(self, imgid, n, go_left=go_left)
        self.undoStack.push(cmd)

        # enqueues appropriate CommmandMoves
        self._move_some_items(stuff, -br.width(), 0)

        self.undoStack.endMacro()

    def _set_visible_page_image(self, imgid: int, show: bool = True) -> None:
        for row in self.src_img_data:
            if row["id"] == imgid:
                row["visible"] = show
        # TODO: replace with emit signal (if needed)
        # self.parent().report_new_or_permuted_image_data(self.src_img_data)
        self.buildUnderLay()

    def deleteIfLegal(self, item, *, dryrun: bool = False) -> bool:
        """Deletes the annotation item if that is a legal action.

        Notes:
            Can't delete the pageimage, scorebox, delete-box, ghostitem and
            its constituents, probably other things too.  You can delete
            annotations: those all have a "saveable" attribute.
            You also cannot delete objects that are part of a group: you need
            to the parent.

        Args:
            item (QGraphicsItem): the item to possibly be deleted.

        Keyword Args:
            dryrun: just check if we could delete but don't actually
                do it.

        Returns:
            True if the object was deleted, else False.
        """
        if item.group() is not None:
            return False
        if not getattr(item, "saveable", False):
            # we can only delete "saveable" items
            return False
        # we're ready to delete, unless this is a dryrun
        if dryrun:
            return True
        command = CommandDelete(self, item)
        self.undoStack.push(command)
        return True

    def hasAnyCrosses(self) -> bool:
        """Returns True if scene has any crosses, False otherwise."""
        for X in self.items():
            if isinstance(X, CrossItem):
                return True
        return False

    def hasOnlyCrosses(self) -> bool:
        """Returns True if scene has only crosses, False otherwise."""
        for X in self.items():
            if getattr(X, "saveable", None):
                if not isinstance(X, CrossItem):
                    return False
        return True

    def hasAnyComments(self) -> bool:
        """Returns True if scene has any rubrics or text items, False otherwise."""
        for X in self.items():
            if isinstance(X, (TextItem, RubricItem)):
                return True
        return False

    def hasAnyTicks(self) -> bool:
        """Returns True if scene has any ticks. False otherwise."""
        for X in self.items():
            if isinstance(X, TickItem):
                return True
        return False

    def hasOnlyTicks(self) -> bool:
        """Returns True if scene has only ticks, False otherwise."""
        for X in self.items():
            if getattr(X, "saveable", None):
                if not isinstance(X, TickItem):
                    return False
        return True

    def hasOnlyTicksCrossesDeltas(self) -> bool:
        """Checks if the image only has crosses, ticks or deltas.

        Returns:
            True if scene only has ticks/crosses/deltas, False otherwise.
        """
        for x in self.items():
            if getattr(x, "saveable", None):
                if isinstance(x, (TickItem, CrossItem)):
                    continue
                if isinstance(x, RubricItem):
                    # check if this is a delta-rubric
                    # TODO: see rubrics_list.py: rubric_is_naked_delta
                    if x.kind == "relative" and x.blurb.toPlainText() == ".":
                        continue
                return False  # otherwise
        return True  # only tick,cross or delta-rubrics

    def highlight_pages(
        self, indices: list[int], colour: str = "blue", *, fade_others: bool = True
    ) -> None:
        """Highlight some of the underlying images that we are annotating."""
        for i in range(len(self.underImage.images)):
            img = self.underImage.images[i]
            if i in indices:
                colour_effect = QGraphicsColorizeEffect()
                colour_effect.setColor(QColor(colour))
                img.setGraphicsEffect(colour_effect)
            elif fade_others:
                fade_effect = QGraphicsOpacityEffect()
                fade_effect.setOpacity(0.25)
                img.setGraphicsEffect(fade_effect)
            else:
                pass

    def highlight_pages_reset(self) -> None:
        """Remove any graphical effects from the underlying images that we are annotating."""
        for i in range(len(self.underImage.images)):
            img = self.underImage.images[i]
            img.setGraphicsEffect(None)

    def get_list_of_non_annotated_underimages(self) -> list[int]:
        """Which images in the scene are not yet annotated.

        Note these are indexed from zero.  Thinking of them as pages is
        potentially misleading: we are annotating a scene made of a list
        of images: which of those images are not yet annotated?
        """
        # TODO: Issue #3367: do nicer code without explicit N^2
        lst = []
        for n in range(len(self.underImage.images)):
            img = self.underImage.images[n]
            page_annotated = False
            for x in self.items():
                if self.is_user_placed(x) and x.collidesWithItem(img):
                    page_annotated = True
                    # no need to further check this img
                    break
            if not page_annotated:
                lst.append(n)
        return lst

    def itemWithinBounds(self, item) -> bool:
        """Check if given item is within the margins or not."""
        return item.collidesWithItem(
            self.underRect, mode=Qt.ItemSelectionMode.ContainsItemShape
        )

    def check_all_saveable_objects_inside(self) -> list:
        """Checks that all objects are within the boundary of the page.

        Returns:
            All annotation (saveable) objects that are outside
            of the boundaries of the margin box (annotable area).
            The list will be empty in the good case of no objects being
            outside.
        """
        out_objs = []
        for X in self.items():
            if getattr(X, "saveable", False):
                if not self.itemWithinBounds(X):
                    out_objs.append(X)
        return out_objs

    def check_all_saveable_objects_are_happy(self) -> list:
        """Checks that all objects are "happy" and not in some error state.

        TODO: a future refactor might subsume the function
        :method:`check_all_saveable_objects_inside`.

        Returns:
            All annotation (saveable) objects that are unhappy.
        """
        unhappy_objs = []
        for X in self.items():
            if getattr(X, "saveable", False):
                # TODO: a future implementation should call X.is_happy()
                # but for now we just hardcode some stuff
                if isinstance(X, RubricItem):
                    if getattr(X, "_attn_msg", ""):
                        unhappy_objs.append(X)
        return unhappy_objs

    def _updateGhost(self, rubric: dict[str, Any]) -> None:
        """Updates the ghost object based on the delta and text.

        Args:
            rubric: we need its delta, its text and whether its legal.

        Returns:
            None
        """
        self.ghostItem.changeComment(
            rubric["display_delta"], rubric["text"], self.isLegalRubric(rubric)
        )

    def _exposeGhost(self) -> None:
        """Exposes the ghost object."""
        self.ghostItem.setVisible(True)

    def _hideGhost(self) -> None:
        """Hides the ghost object."""
        self.ghostItem.setVisible(False)

    def setTheMark(self, newMark: int | float) -> None:
        """Sets the new mark/score for the paper.

        Args:
            newMark: the new mark/score for the paper.

        Returns:
            None
        """
        self.score = newMark
        self.scoreBox.changeScore(self.score)

    def undo(self):
        """Undoes a given action."""
        self.undoStack.undo()

    def redo(self):
        """Redoes a given action."""
        self.undoStack.redo()

    def isLegalRubric(self, rubric: dict[str, Any]) -> bool:
        """Is this rubric-type legal for the current scene, and does it move score below 0 or above maxMark?

        Args:
            rubric (dict): must have at least the keys "kind", "value",
                "display_delta", and "out_of".

        Returns:
            True if the delta is legal, False otherwise.
        """
        rubrics = self.get_rubrics()
        rubrics.append(rubric)

        try:
            compute_score(rubrics, self.maxMark)
        except ValueError:
            return False
        except PlomInconsistentRubric:
            return False
        return True

    def setCurrentRubric(self, rubric: dict[str, Any]) -> None:
        """Changes the new rubric for the paper based on the delta and text.

        This doesn't effect what is shown in the scene: its just a setter.
        To force an update, see ``setToolMode``, which you likely want to call
        after this method.

        Args:
            rubric (dict): must have at least the keys and values::
                - value (int):
                - out_of (int):
                - display_delta (str): a string displaying the value of the rubric.
                - text (str): the text in the rubric.
                - id (int): the id of the rubric.
                - kind (str): ``"absolute"``, ``"neutral"``, etc.

        Returns:
            None
        """
        self.current_rubric = rubric
        self._updateGhost(rubric)

    def stopMidDraw(self):

        if self.active_drawer:
            self.active_drawer.cancel()
            self.active_drawer = None
            return

        # log.debug("Flags = {}".format(self.__getFlags()))

    def isDrawing(self):
        # return any(flag > 0 for flag in self.__getFlags())
        return self.active_drawer is not None

    # PAGE SCENE CROPPING STUFF
    def _crop_to_focus(self, crop_rect):
        # this is called by the actual command-redo.
        self.overMask.crop_to_focus(crop_rect)
        self.scoreBox.setPos(crop_rect.topLeft())
        self.avoidBox = self.scoreBox.boundingRect().adjusted(-16, -16, 64, 24)
        # set zoom to "fit-page"
        self.views()[0].zoomFitPage(update=True)

    def current_crop_rectangle_as_proportions(
        self,
    ) -> tuple[float, float, float, float]:
        """Return the crop rectangle as proportions of original image."""
        full_height = self.underImage.boundingRect().height()
        full_width = self.underImage.boundingRect().width()
        rect_in_pix = self.overMask.inner_rect

        rect_as_proportions = (
            rect_in_pix.x() / full_width,
            rect_in_pix.y() / full_height,
            rect_in_pix.width() / full_width,
            rect_in_pix.height() / full_height,
        )
        return rect_as_proportions

    def crop_from_plomfile(self, crop_dat):
        # crop dat = (x,y,w,h) as proportions of full image, so scale by underlying image width/height
        full_height = self.underImage.boundingRect().height()
        full_width = self.underImage.boundingRect().width()
        crop_rect = QRectF(
            crop_dat[0] * full_width,
            crop_dat[1] * full_height,
            crop_dat[2] * full_width,
            crop_dat[3] * full_height,
        )
        self.trigger_crop(crop_rect)

    def uncrop_underlying_images(self):
        self.trigger_crop(self.overMask.get_original_inner_rect())

    def trigger_crop(self, crop_rect):
        # make sure that the underlying crop-rectangle is normalised
        # also make sure that it is not larger than the original image - so use their intersection
        actual_crop = crop_rect.intersected(self.underImage.boundingRect()).normalized()
        # pass new crop rect, as well as current one (for undo)
        command = CommandCrop(self, actual_crop, self.overMask.inner_rect)
        self.undoStack.push(command)
        # now set mode to move.
        self.parent().toMoveMode()
