# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2020 Andrew Rechnitzer
# Copyright (C) 2020-2021 Colin B. Macdonald
# Copyright (C) 2020 Victoria Schuster
# Copyright (C) 2020 Vala Vakilian

import logging
from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QBrush, QIcon, QPixmap, QTransform
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QGridLayout,
    QListView,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QToolButton,
)

from .examviewwindow import ImageViewWidget
from .useful_classes import ErrorMessage, SimpleMessage


log = logging.getLogger("viewerdialog")


class SourceList(QListWidget):
    """An immutable ordered list of possible pages from the server.

    Some of them may be hidden at any time (e.g., when they are in
    the other Sink List), but they cannot currently be removed or
    added too.  In particular, no changes in the Adjust Pages dialog
    directly make it back to the server.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.setViewMode(QListWidget.IconMode)
        self.setAcceptDrops(False)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setFlow(QListView.LeftToRight)
        self.setIconSize(QSize(320, 320))
        self.setSpacing(8)
        self.setWrapping(False)
        self.itemDoubleClicked.connect(self.viewImage)
        self.item_positions = {}
        self.item_files = {}
        self.item_orientation = {}
        # self.setSelectionMode(QListView.SingleSelection)

    def resizeEvent(self, whatev):
        A = self.size()
        x = min(A.width(), A.height())
        # TODO: must be a way to not hardcode 50 here
        # TODO: also compensate for scrollbars or not
        B = QSize(x - 50, x - 50)
        self.setIconSize(B)

    def addImageItem(self, p, pfile, belongs):
        current_row = self.count()
        name = str(p)
        it = QListWidgetItem(QIcon(pfile), name)
        if belongs:
            it.setBackground(QBrush(Qt.darkGreen))
        self.addItem(it)  # item is added at current_row
        self.item_positions[name] = current_row
        self.item_files[name] = pfile
        self.item_orientation[name] = 0

    def hideItemByName(self, name=None):
        """Removes (hides) a single named item from source-list.

        Returns:
            str: The name of the item we just hid.  If the item was
                already hidden, we still return name here.
        """
        if name is None:
            raise ValueError("You must provide the 'name' argument")

        ci = self.item(self.item_positions[name])

        if ci is None:
            return None
        ci.setHidden(True)
        self.setCurrentItem(None)
        assert ci.text() == name, "Something has gone very wrong: expect match"
        return ci.text()

    def hideSelectedItems(self):
        """Hides the selected items and passes back name list."""
        name_list = []
        for ci in self.selectedItems():
            ci.setHidden(True)
            name_list.append(ci.text())
        self.setCurrentItem(None)
        return name_list

    def unhideNamedItems(self, name_list):
        """Unhide the name list of items."""
        for name in name_list:
            ci = self.item(self.item_positions[name])
            if ci:
                ci.setHidden(False)

    def viewImage(self, qi):
        self._parent.viewImage(self.item_files[qi.text()])


class SinkList(QListWidget):
    """An ordered list of pages for this task.

    This holds the current view of pages we're considering for this
    task.  They can be reordered, removed (and visually put back in
    the SourceList), rotated, etc.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.setViewMode(QListWidget.IconMode)
        self.setFlow(QListView.LeftToRight)
        self.setAcceptDrops(False)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setFlow(QListView.LeftToRight)
        # self.setResizeMode(QListView.Adjust)
        self.setIconSize(QSize(320, 320))
        self.setSpacing(8)
        self.setWrapping(False)
        self.item_belongs = (
            {}
        )  # whether or not the item 'officially' belongs to the question
        self.item_files = {}
        self.item_orientation = {}
        self.item_id = {}
        self.itemDoubleClicked.connect(self.viewImage)
        # self.setSelectionMode(QListView.SingleSelection)

    def resizeEvent(self, whatev):
        A = self.size()
        x = min(A.width(), A.height())
        # TODO: must be a way to not hardcode 50 here
        B = QSize(x - 50, x - 50)
        self.setIconSize(B)

    def addPotentialItem(self, p, pfile, belongs, db_id=None):
        name = str(p)
        self.item_files[name] = pfile
        self.item_orientation[name] = 0  # TODO
        self.item_id[name] = db_id
        self.item_belongs[name] = belongs

    def removeSelectedItems(self):
        """Remove the selected items and pass back a name list"""
        name_list = []
        # be careful removing things as list indices update as you delete.
        sel_rows = [x.row() for x in self.selectedIndexes()]
        for cr in reversed(sorted(sel_rows)):
            ci = self.takeItem(cr)
            name_list.append(ci.text())

        self.setCurrentItem(None)
        return name_list

    def appendItem(self, name):
        if name is None:
            return
        ci = QListWidgetItem(QIcon(self.item_files[name]), name)
        if self.item_belongs[name]:
            ci.setBackground(QBrush(Qt.darkGreen))
        self.addItem(ci)
        # TODO: workaround to force re-orientation on entry to Sink list
        self.rotateForceRefresh(name)
        self.setCurrentItem(ci)

    def appendItems(self, name_list):
        for name in name_list:
            self.appendItem(name)

    def shuffleLeft(self):
        cr = self.currentRow()
        if cr in [-1, 0]:
            return
        ci = self.takeItem(cr)
        self.insertItem(cr - 1, ci)
        self.setCurrentRow(cr - 1)

    def shuffleRight(self):
        cr = self.currentRow()
        if cr in [-1, self.count() - 1]:
            return
        ci = self.takeItem(cr)
        self.insertItem(cr + 1, ci)
        self.setCurrentRow(cr + 1)

    def reverseOrder(self):
        rc = self.count()
        for n in range(rc // 2):
            # swap item[n] with item [rc-n-1]
            ri = self.takeItem(rc - n - 1)
            li = self.takeItem(n)
            self.insertItem(n, ri)
            self.insertItem(rc - n - 1, li)

    def rotateSelectedImages(self, angle=90):
        """Iterate over selection, rotating each image"""
        for i in self.selectedIndexes():
            ci = self.item(i.row())
            name = ci.text()
            self.rotateItemBy(name, angle)
        self._parent.update()
        # Issue #1164 workaround: https://www.qtcentre.org/threads/25867-Problem-with-QListWidget-Updating
        self.setFlow(QListView.LeftToRight)

    def rotateForceRefresh(self, name):
        """Force an item to visually update its rotate.

        TODO: make this unnecessary and remove it!  Icons should know
        how to display themselves properly.
        """
        angle = self.item_orientation[name]
        if angle == 0:
            return
        log.info("Forcing orientation to %s", format(angle))
        self.rotateItemTo(name, angle)

    def rotateItemBy(self, name, delta_angle):
        """Rotate image by an angle relative to its current state.

        args:
            name (str)
            delta_angle (int)
        """
        angle = self.item_orientation[name]
        angle = (angle + delta_angle) % 360
        self.rotateItemTo(name, angle)

    def rotateItemTo(self, name, angle):
        """Rotate image to a particular orientation.

        args:
            name (str)
            angle (int)
        """
        self.item_orientation[name] = angle
        rot = QTransform()
        rot.rotate(angle)
        # TODO: instead of loading pixmap again, can we transform the QIcon?
        # Also, docs warned QPixmap.transformed() is slow
        rfile = self.item_files[name]
        cpix = QPixmap(rfile)
        npix = cpix.transformed(rot)
        # ci = self.item(self.item_positions[name])
        # TODO: instead we get `ci` with a dumb loop
        for i in range(self.count()):
            ci = self.item(i)
            if ci.text() == name:
                break
        ci.setIcon(QIcon(npix))
        # rotpixmap = ci.getIcon().pixmap().transformed(rot)
        # ci.setIcon(QIcon(rotpixmap))

    def viewImage(self, qi):
        self._parent.viewImage(self.item_files[qi.text()])

    def getNameList(self):
        nList = []
        for r in range(self.count()):
            nList.append(self.item(r).text())
        return nList


class RearrangementViewer(QDialog):
    def __init__(
        self, parent, testNumber, current_pages, page_data, need_to_confirm=False
    ):
        super().__init__(parent)
        self.testNumber = testNumber
        self.need_to_confirm = need_to_confirm
        self._setupUI()
        page_data = self.dedupe_by_md5sum(page_data)
        self.pageData = page_data
        self.nameToIrefNFile = {}
        if current_pages:
            self.populateListWithCurrent(current_pages)
        else:
            self.populateListOriginal()

    def _setupUI(self):
        """
        Sets up thee UI for the rearrangement Viewer.

        Notes:
             helper method for __init__

        Returns:
            None
        """
        self.scrollA = QScrollArea()
        self.listA = SourceList(self)
        self.listA.itemSelectionChanged.connect(self.show_relevant_tools)
        self.scrollA.setWidget(self.listA)
        self.scrollA.setWidgetResizable(True)
        self.scrollB = QScrollArea()
        self.listB = SinkList(self)
        self.listB.itemSelectionChanged.connect(self.show_relevant_tools)
        self.scrollB.setWidget(self.listB)
        self.scrollB.setWidgetResizable(True)

        self.appendB = QToolButton()
        # TODO: move &A here and use alt-Enter to Accept dialog?
        self.appendB.setText("Add &Page(s)")
        self.appendB.setArrowType(Qt.DownArrow)
        self.appendB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.removeB = QToolButton()
        self.removeB.setArrowType(Qt.UpArrow)
        self.removeB.setText("&Remove Page(s)")
        self.removeB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.sLeftB = QToolButton()
        self.sLeftB.setArrowType(Qt.LeftArrow)
        self.sLeftB.setText("Shift Left")
        self.sLeftB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.sRightB = QToolButton()
        self.sRightB.setArrowType(Qt.RightArrow)
        self.sRightB.setText("Shift Right")
        self.sRightB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.reverseB = QPushButton("Reverse Order")
        self.revertB = QPushButton("Revert to original state")
        self.revertB.clicked.connect(self.populateListOriginal)

        self.rotateB_cw = QPushButton("\N{Clockwise Open Circle Arrow} Rotate CW")
        self.rotateB_ccw = QPushButton("\N{Anticlockwise Open Circle Arrow} Rotate CCW")

        self.closeB = QPushButton("&Cancel")
        self.acceptB = QPushButton("&Accept")

        self.permute = [False]

        def GrippyMcGrab():
            """Grippy bars to spice-up QSplitterHandles."""
            width = 64
            pad = 20
            hb = QHBoxLayout()
            hb.addItem(
                QSpacerItem(pad, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
            )
            vb = QVBoxLayout()
            hb.addLayout(vb)
            hb.addItem(
                QSpacerItem(pad, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
            )

            vb.setContentsMargins(0, 1, 0, 1)
            vb.setSpacing(2)
            vb.addItem(
                QSpacerItem(
                    width, 3, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
                )
            )
            for i in range(3):
                f = QFrame()
                f.setFrameShape(QFrame.HLine)
                f.setFrameShadow(QFrame.Sunken)
                vb.addWidget(f)
            vb.addItem(
                QSpacerItem(
                    width, 3, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
                )
            )
            return hb

        hb3 = QHBoxLayout()
        self.tools = QFrame()
        hb = QHBoxLayout()
        self.tools.setLayout(hb)
        hb.setContentsMargins(0, 0, 0, 0)
        hb.addWidget(self.rotateB_ccw)
        hb.addWidget(self.rotateB_cw)
        hb.addItem(QSpacerItem(16, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        hb.addWidget(self.sLeftB)
        hb.addWidget(self.sRightB)
        hb.addItem(QSpacerItem(16, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        hb3.addWidget(self.tools)
        hb3.addWidget(self.reverseB)
        hb3.addItem(
            QSpacerItem(16, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        )
        hb3.addWidget(self.acceptB)
        hb3.addWidget(self.closeB)

        allPages = QLabel("Other Pages in Exam")
        thisQuestion = QLabel("Pages for this Question")

        # center add/remove buttons on label row
        hb1 = QHBoxLayout()
        hb1.addWidget(thisQuestion)
        hb1.addLayout(GrippyMcGrab())
        hb = QHBoxLayout()
        hb.addWidget(self.appendB)
        hb.addItem(QSpacerItem(64, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        hb.addWidget(self.removeB)
        hb1.addLayout(hb)
        hb1.addLayout(GrippyMcGrab())
        hb1.addWidget(self.revertB)

        vb0 = QVBoxLayout()
        s = QSplitter()
        s.setOrientation(Qt.Vertical)
        # s.setOpaqueResize(False)
        s.setChildrenCollapsible(False)
        # TODO: better not to hardcode, take from children?
        s.setHandleWidth(50)
        vb0.addWidget(s)
        f = QFrame()
        s.addWidget(f)
        vb = QVBoxLayout()
        vb.setContentsMargins(0, 0, 0, 0)
        f.setLayout(vb)
        vb.addWidget(allPages)
        vb.addWidget(self.scrollA)
        f = QFrame()
        s.addWidget(f)
        vb = QVBoxLayout()
        vb.setContentsMargins(0, 0, 0, 0)
        f.setLayout(vb)
        vb.addWidget(self.scrollB)
        vb.addLayout(hb3)

        handle = s.handle(1)
        vb = QVBoxLayout()
        vb.setContentsMargins(0, 0, 0, 0)
        vb.setSpacing(0)
        handle.setLayout(hb1)
        hb1.setContentsMargins(0, 0, 0, 0)
        # TODO: Buttons inside the splitter bar, disable drag and custom cursor
        for b in (self.removeB, self.appendB, self.revertB):
            b.mouseMoveEvent = lambda *args: None
            b.setCursor(Qt.ArrowCursor)

        self.setLayout(vb0)
        self.resize(
            QSize(
                int(self.parent().width() * 7 / 8),
                int(self.parent().height() * 11 / 12),
            )
        )

        self.closeB.clicked.connect(self.close)
        self.sLeftB.clicked.connect(self.shuffleLeft)
        self.sRightB.clicked.connect(self.shuffleRight)
        self.reverseB.clicked.connect(self.reverseOrder)
        self.rotateB_cw.clicked.connect(lambda: self.rotateImages(90))
        self.rotateB_ccw.clicked.connect(lambda: self.rotateImages(-90))
        self.appendB.clicked.connect(self.sourceToSink)
        self.removeB.clicked.connect(self.sinkToSource)
        self.acceptB.clicked.connect(self.doShuffle)

        allPageWidgets = [self.listA, self.listB]

        self.listA.selectionModel().selectionChanged.connect(
            lambda sel, unsel: self.singleSelect(self.listA, allPageWidgets)
        )
        self.listB.selectionModel().selectionChanged.connect(
            lambda sel, unsel: self.singleSelect(self.listB, allPageWidgets)
        )

    def dedupe_by_md5sum(self, pageData):
        """Collapse entries in the pagedata with duplicated md5sums.

        In the future [1], pages will be shared between questions but we
        only want to show one copy of each such duplicated page in the
        "Adjust pages" dialog.

        [1] https://gitlab.com/plom/plom/-/merge_requests/698

        The data looks like the following.  We want to compress rows that
        have duplicated md5sums:
        ```
        ['h1.1', 'e224c22eda93456143fbac94beb0ffbd', True, 1, 40, '/tmp/plom_zq/tmpnqq.image]
        ['h1.2', '97521f4122df24ca012a12930391195a', True, 2, 41, '/tmp/plom_zq/tmp_om.image]
        ['h2.1', 'e224c22eda93456143fbac94beb0ffbd', False, 1, 40, '/tmp/plom_zq/tmpx0s.image]
        ['h2.2', '97521f4122df24ca012a12930391195a', False, 2, 41, '/tmp/plom_zq/tmpd5g.image]
        ['h2.3', 'abcd1234abcd12314717621412412444', False, 3, 42, '/tmp/plom_zq/tmp012.image]
        ['h3.1', 'abcd1234abcd12314717621412412444', False, 1, 42, '/tmp/plom_zq/tmp012.image]
        ```
        (Possibly filenames are repeated for repeat md5: not required by this code.)

        From this we want something like:
        ```
        ['h1.1 (& h2.1)', 'e224c22eda93456143fbac94beb0ffbd', True, 1, 40, '/tmp/plom_zq/tmpnqq.image]
        ['h1.2 (& h2.2)', '97521f4122df24ca012a12930391195a', True, 2, 41, '/tmp/plom_zq/tmp_om.image]
        ['h2.3 (& h3.1)', 'abcd1234abcd12314717621412412444', False, 3, 42, '/tmp/plom_zq/tmp012.image]
        ```
        where the names of duplicates are shown in parentheses.

        It seems we need to keep the order as much as possible in this file, which complicates this.
        May not be completely well-posed.  Probably better to refactor before this.  E.g., factor out
        a dict of md5sum to filenames before we get here.

        "Included" (column 3): include these in the question or maybe server
        originally had these in the question (TODO: maybe not, True/False
        generated on API call).

        TODO: if order does not have `h1,1` first, should we move it first?
              that is, before the parenthetical?  Probably by re-ordering
              the list.
        """
        # List of lists, preserving original order within each list
        tmp_data = []
        for x in pageData:
            md5 = x[1]
            md5s_so_far = [y[0][1] for y in tmp_data]
            if md5 in md5s_so_far:
                i = md5s_so_far.index(md5)
                tmp_data[i].append(x.copy())
            else:
                tmp_data.append([x.copy()])

        # Compress each list down to a single item, packing the names
        new_pageData = []
        # warn/log if True not in first?
        for y in tmp_data:
            z = y[0].copy()
            other_names = [_[0] for _ in y[1:]]
            if other_names:
                z[0] = z[0] + " (& {})".format(", ".join(other_names))
            # If any entry had True for "included", include this row
            # TODO: or should we reorder the list, moving True to front?
            # TODO: depends what is done with the other data
            z[2] = any([_[2] for _ in y])
            new_pageData.append(z)

        return new_pageData

    def show_relevant_tools(self):
        """Hide/show tools based on current selections."""
        if self.listB.selectionModel().hasSelection():
            self.removeB.setEnabled(True)
            self.tools.setEnabled(True)
        else:
            self.removeB.setEnabled(False)
            self.tools.setEnabled(False)
        if self.listA.selectionModel().hasSelection():
            self.appendB.setEnabled(True)
        else:
            self.appendB.setEnabled(False)

    def populateListOriginal(self):
        """
        Populates the QListWidgets with exam pages, using original server view.

        Returns:
            None: but changes the state of self.
        """
        self.nameToIrefNFile = {}
        self.listA.clear()
        self.listB.clear()
        move_order = {}
        for row in self.pageData:
            self.nameToIrefNFile[row[0]] = [row[1], row[5]]
            # add every page image to list A
            self.listA.addImageItem(row[0], row[5], row[2])
            # add the potential for every page to listB
            self.listB.addPotentialItem(row[0], row[5], row[2], db_id=row[4])
            # if position in current annot is non-null then add to list of pages to move between lists.
            if row[2] and row[3]:
                move_order[row[3]] = row[0]
        for k in sorted(move_order.keys()):
            self.listB.appendItem(self.listA.hideItemByName(name=move_order[k]))

    def populateListWithCurrent(self, current):
        """
        Populates the QListWidgets with pages, with current state highlighted.

        Args:
            current (list): dicts with 'md5' and 'orientation' keys.

        Returns:
            None: but changes the state of self.
        """
        self.nameToIrefNFile = {}
        self.listA.clear()
        self.listB.clear()
        for row in self.pageData:
            self.nameToIrefNFile[row[0]] = [row[1], row[5]]
            # add every page image to list A
            self.listA.addImageItem(row[0], row[5], row[2])
            # add the potential for every page to listB
            self.listB.addPotentialItem(row[0], row[5], row[2], db_id=row[4])
        for kv in current:
            match = [row[0] for row in self.pageData if row[1] == kv["md5"]]
            assert len(match) == 1, "Oops, expected unique md5s in filtered pagedata"
            (match,) = match
            self.listB.appendItem(self.listA.hideItemByName(match))
            if kv["orientation"] != 0:
                log.info("Applying orientation of %s", kv["orientation"])
                # always display unrotated in source ListA
                # TODO: should reflect server static info (currently always orientation = 0 but...)
                self.listB.rotateItemTo(match, kv["orientation"])

    def sourceToSink(self):
        """
        Adds the currently selected page to the list for the current question.

        Notes:
            If currently selected page is in current question, does nothing.

        Returns:
            None

        """
        if self.listA.selectionModel().hasSelection():
            self.listB.appendItems(self.listA.hideSelectedItems())
        else:
            pass

    def sinkToSource(self):
        """
        Removes the currently selected page from the list for the current
        question.

        Notes:
            If currently selected page isn't in current question,
            does nothing.

        Returns:
            None
        """
        if self.listB.selectionModel().hasSelection():
            self.listA.unhideNamedItems(self.listB.removeSelectedItems())
        else:
            pass

    def shuffleLeft(self):
        """
        Shuffles currently selected page to the left one position.

        Notes:
            If currently selected page isn't in current question,
            does nothing.

        Returns:
            None
        """
        if self.listB.selectionModel().hasSelection():
            self.listB.shuffleLeft()
        else:
            pass

    def shuffleRight(self):
        """
        Shuffles currently selected page to the left one position.

        Notes:
            If currently selected page isn't in current question,
            does nothing.

        Returns:
            None
        """
        if self.listB.selectionModel().hasSelection():
            self.listB.shuffleRight()
        else:
            pass

    def reverseOrder(self):
        """
        reverses the order of the pages in current question.
        """
        self.listB.reverseOrder()

    def rotateImages(self, angle=90):
        """Rotates the currently selected page by 90 degrees."""
        self.listB.rotateSelectedImages(angle)

    def viewImage(self, fname):
        """Shows a larger view of the currently selected page."""
        GroupView(self, [fname], bigger=True).exec_()

    def doShuffle(self):
        """
        Reorders and saves pages according to user's selections.

        Returns:
            Doesn't return anything directly but sets `permute` instance
            variable which contains a list of tuples:
                `(iref, filename, angle, database_id)`
            (where `iref` seems to be md5sum?  TODO).
        """
        if self.listB.count() == 0:
            msg = ErrorMessage("You must have at least one page in the bottom list.")
            msg.exec()
            return
        if self.need_to_confirm:
            msg = SimpleMessage(
                "Are you sure you want to save this page order? This will erase "
                "all your annotations."
            )
            if msg.exec() == QMessageBox.No:
                return

        self.permute = []
        for n in self.listB.getNameList():
            tmp = self.nameToIrefNFile[n]
            self.permute.append(
                (*tmp, self.listB.item_orientation[n], self.listB.item_id[n])
            )
        self.accept()

    def singleSelect(self, currentList, allPages):
        """
        If item selected by user isn't in currentList, deselects currentList.

        Args:
            currentList (QListWidget): the list being checked.
            allPages (List[QListWidget]): all lists in selection

        Notes:
            from https://stackoverflow.com/questions/45509496/qt-multiple-qlistwidgets-and-only-a-single-entry-selected

        Returns:
            None

        """
        for lstViewI in allPages:
            if lstViewI == currentList:
                continue
            # the check is necessary to prevent recursions...
            if lstViewI.selectionModel().hasSelection():
                # ...as this causes emission of selectionChanged() signal as well:
                lstViewI.selectionModel().clearSelection()


class GroupView(QDialog):
    def __init__(self, parent, fnames, bigger=False):
        super().__init__(parent)
        grid = QGridLayout()
        self.testImg = ImageViewWidget(self, fnames, has_reset_button=False)
        closeButton = QPushButton("&Close")
        resetB = QPushButton("&reset view")
        grid.addWidget(self.testImg, 1, 1, 1, 8)
        grid.addWidget(closeButton, 2, 8)
        grid.addWidget(resetB, 2, 1)
        self.setLayout(grid)
        if bigger:
            self.resize(
                QSize(
                    int(self.parent().width() * 2 / 3),
                    int(self.parent().height() * 11 / 12),
                )
            )
        resetB.clicked.connect(self.testImg.resetView)
        closeButton.clicked.connect(self.close)
        if bigger:
            # TODO: seems needed for Ctrl-R double-click popup
            self.testImg.resetView()
            self.testImg.forceRedrawOrSomeBullshit()

    def closeEvent(self, event):
        self.closeWindow()

    def closeWindow(self):
        self.close()


class QuestionViewDialog(GroupView):
    """View the raw scans from a particular question, optionally with tagging.

    Args:
        parent: the parent of this dialog
        fnames (list): the files to use for viewing, `str` or `pathlib.Path`.
            We don't claim the files: caller should manage them and delete
            when done.
        testnum (int): which test/paper number is this
        questnum (int): which question number.  TODO: probably should
            support question label.
        ver (int/None): if we know the version, we can display it.
        marker (None/plom.client.Marker): used to talk to the server for
            tagging.
    """

    def __init__(self, parent, fnames, testnum, questnum, ver=None, marker=None):
        super().__init__(parent, fnames)
        s = f"Original ungraded images for test {testnum:04} question {questnum}"
        if ver:
            s += f" (ver {ver})"
        self.setWindowTitle(s)
        self.tgv = (testnum, questnum, ver)
        grid = self.layout()
        if marker:
            self.marker = marker
            tagButton = QPushButton("&Tags")
            tagButton.clicked.connect(self.tags)
            # add new button to bottom right
            grid.addWidget(tagButton, grid.rowCount() - 1, grid.columnCount() - 2)

    def tags(self):
        """If we have a marker parent then use it to manage tags"""
        if self.marker:
            task = f"q{self.tgv[0]:04}g{self.tgv[1]}"
            self.marker.manage_task_tags(task, parent=self)


class WholeTestView(QDialog):
    def __init__(self, testnum, filenames, labels=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Original scans of test {testnum}")
        self.pageTabs = QTabWidget()
        closeButton = QPushButton("&Close")
        prevButton = QPushButton("&Previous")
        nextButton = QPushButton("&Next")
        grid = QGridLayout()
        grid.addWidget(self.pageTabs, 1, 1, 6, 6)
        grid.addWidget(prevButton, 7, 1)
        grid.addWidget(nextButton, 7, 2)
        grid.addWidget(closeButton, 7, 6)
        self.setLayout(grid)
        prevButton.clicked.connect(self.previousTab)
        nextButton.clicked.connect(self.nextTab)
        closeButton.clicked.connect(self.closeWindow)
        self.pageTabs.currentChanged.connect(self.tabSelected)
        self.setMinimumSize(500, 500)
        if not labels:
            labels = [f"{k + 1}" for k in range(len(filenames))]
        for f, label in zip(filenames, labels):
            # Tab doesn't seem to have padding so compact=False
            tab = ImageViewWidget(self, [f], compact=False)
            self.pageTabs.addTab(tab, label)

    def closeEvent(self, event):
        self.closeWindow()

    def closeWindow(self):
        self.close()

    def tabSelected(self, index):
        """Resize on change tab."""
        if index >= 0:
            self.pageTabs.currentWidget().resetView()

    def nextTab(self):
        t = self.pageTabs.currentIndex() + 1
        if t >= self.pageTabs.count():
            t = 0
        self.pageTabs.setCurrentIndex(t)

    def previousTab(self):
        t = self.pageTabs.currentIndex() - 1
        if t < 0:
            t = self.pageTabs.count() - 1
        self.pageTabs.setCurrentIndex(t)


class SelectTestQuestion(QDialog):
    def __init__(self, info, gn=None):
        super().__init__()
        self.setModal(True)
        self.setWindowTitle("View another test")
        self.iL = QLabel("From which test do you wish to view the current question?")
        self.ab = QPushButton("&Accept")
        self.ab.clicked.connect(self.accept)
        self.cb = QPushButton("&Cancel")
        self.cb.clicked.connect(self.reject)

        fg = QFormLayout()
        self.tsb = QSpinBox()
        self.tsb.setRange(1, info["numberToProduce"])
        self.tsb.setValue(1)
        fg.addRow("Select test:", self.tsb)
        if gn is not None:
            self.gsb = QSpinBox()
            self.gsb.setRange(1, info["numberOfQuestions"])
            self.gsb.setValue(gn)
            fg.addRow("Select question:", self.gsb)
            self.iL.setText("Which test/group do you wish to view?")
        grid = QGridLayout()
        grid.addWidget(self.iL, 0, 1, 1, 3)
        grid.addLayout(fg, 1, 1, 3, 3)
        grid.addWidget(self.ab, 4, 1)
        grid.addWidget(self.cb, 4, 3)
        self.setLayout(grid)


class SolutionViewer(QWidget):
    def __init__(self, parent, fname):
        super().__init__()
        self._annotr = parent
        grid = QGridLayout()
        self.sv = ImageViewWidget(self, fname)
        self.refreshButton = QPushButton("&Refresh")
        self.closeButton = QPushButton("&Close")
        self.maxNormButton = QPushButton("&Max/Norm")
        grid.addWidget(self.sv, 1, 1, 6, 6)
        grid.addWidget(self.refreshButton, 7, 1)
        grid.addWidget(self.closeButton, 7, 7)
        grid.addWidget(self.maxNormButton, 1, 7)
        self.setLayout(grid)
        self.closeButton.clicked.connect(self.closeWindow)
        self.maxNormButton.clicked.connect(self.swapMaxNorm)
        self.refreshButton.clicked.connect(self.refresh)

        self.setWindowTitle(f"Solutions - {Path(fname).stem}")

        self.setMinimumSize(500, 500)

        self.show()

    def swapMaxNorm(self):
        """Toggles the window size between max and normal"""
        if self.windowState() != Qt.WindowMaximized:
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.setWindowState(Qt.WindowNoState)

    def closeEvent(self, event):
        self.closeWindow()

    def closeWindow(self):
        self.close()

    def refresh(self):
        solnfile = self._annotr.refreshSolutionImage()
        self.sv.updateImage(solnfile)
        if solnfile is None:
            ErrorMessage("Server no longer has a solution.  Try again later?").exec_()


class CatViewer(QDialog):
    def __init__(self, parent, dogAttempt=False):
        import tempfile
        import urllib.request

        self.msgs = [
            "PLOM",
            "I%20can%20haz%20more%20markingz",
            "Insert%20meme%20here",
            "Hello%20Omer",
            "More%20patz%20pleeze",
        ]

        super().__init__(parent)
        grid = QGridLayout()
        self.count = 0
        self.catz = tempfile.NamedTemporaryFile(delete=False)

        try:
            logging.debug("Trying to refresh cat image")
            if dogAttempt:
                urllib.request.urlretrieve(
                    "https://cataas.com/cat/says/No%20dogz.%20Only%20Catz%20and%20markingz",
                    self.catz.name,
                )
            else:
                urllib.request.urlretrieve("https://cataas.com/cat", self.catz.name)
            self.sv = ImageViewWidget(self, self.catz.name)
            logging.debug("Cat image refreshed")
        except Exception:
            ErrorMessage("Cannot get cat picture.  Try again later?").exec_()
            self.sv = ImageViewWidget(self, None)

        self.refreshButton = QPushButton("&Refresh")
        self.closeButton = QPushButton("&Close")
        grid.addWidget(self.sv, 1, 1, 6, 7)
        grid.addWidget(self.refreshButton, 7, 1)
        grid.addWidget(self.closeButton, 7, 7)
        self.setLayout(grid)
        self.closeButton.clicked.connect(self.closeWindow)
        self.refreshButton.clicked.connect(self.refresh)

        self.setWindowTitle("Catz")

        self.setMinimumSize(500, 500)

    def closeEvent(self, event):
        from os import unlink

        try:
            unlink(self.catz.name)
        except OSError:
            pass
        self.closeWindow()

    def closeWindow(self):
        self.close()

    def refresh(self):
        import urllib.request
        import random

        self.count += 1
        if self.count > 5:
            urllib.request.urlretrieve(
                "https://cataas.com/cat/says/{Back%20to%20work}", self.catz.name
            )
            self.sv.updateImage(self.catz.name)
            ErrorMessage("Enough break time").exec_()
            self.close()

        else:
            try:
                logging.debug("Trying to refresh cat image")
                if random.choice([0, 1]) == 0:
                    urllib.request.urlretrieve("https://cataas.com/cat", self.catz.name)
                else:
                    msg = random.choice(self.msgs)
                    urllib.request.urlretrieve(
                        f"https://cataas.com/cat/says/{msg}", self.catz.name
                    )

                self.sv.updateImage(self.catz.name)
                logging.debug("Cat image refreshed")
            except Exception:
                ErrorMessage("Cannot get cat picture.  Try again later?").exec_()


###
