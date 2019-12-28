__author__ = "Andrew Rechnitzer"
__copyright__ = "Copyright (C) 2018-2019 Andrew Rechnitzer"
__credits__ = ["Andrew Rechnitzer", "Colin Macdonald", "Elvis Cai", "Matt Coles"]
__license__ = "AGPLv3"
import os
import toml
import re
import time

from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QDropEvent, QIcon, QPixmap, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QLabel,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QItemDelegate,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableView,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class ErrorMessage(QMessageBox):
    """A simple error message pop-up"""

    def __init__(self, txt):
        super(ErrorMessage, self).__init__()
        fnt = self.font()
        fnt.setPointSize((fnt.pointSize() * 3) // 2)
        self.setFont(fnt)
        self.setText(txt)
        self.setStandardButtons(QMessageBox.Ok)


class SimpleMessage(QMessageBox):
    """A simple message pop-up with yes/no buttons and
    large font.
    """

    def __init__(self, txt):
        super(SimpleMessage, self).__init__()
        self.setText(txt)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.Yes)
        fnt = self.font()
        fnt.setPointSize((fnt.pointSize() * 3) // 2)
        self.setFont(fnt)


class SimpleMessageCheckBox(QMessageBox):
    """A simple message pop-up with yes/no buttons, a checkbox and
    large font.
    """

    def __init__(self, txt):
        super(SimpleMessageCheckBox, self).__init__()
        self.cb = QCheckBox("Don't show this message again")
        self.setText(txt)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.Yes)
        self.setCheckBox(self.cb)

        fnt = self.font()
        fnt.setPointSize((fnt.pointSize() * 3) // 2)
        self.setFont(fnt)


class SimpleTableView(QTableView):
    """A table-view widget that emits annotateSignal when
    the user hits enter or return.
    """

    # This is picked up by the marker, lets it know to annotate
    annotateSignal = pyqtSignal()

    def __init__(self, parent=None):
        super(SimpleTableView, self).__init__()
        # User can sort, cannot edit, selects by rows.
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Resize to fit the contents
        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)

    def keyPressEvent(self, event):
        # If user hits enter or return, then fire off
        # the annotateSignal, else pass the event on.
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self.annotateSignal.emit()
        else:
            super(SimpleTableView, self).keyPressEvent(event)


class SimpleToolButton(QToolButton):
    """Specialise the tool button to be an icon above text."""

    def __init__(self, txt, icon):
        super(SimpleToolButton, self).__init__()
        self.setText(txt)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIcon(QIcon(QPixmap(icon)))
        self.setIconSize(QSize(24, 24))
        self.setMinimumWidth(100)


# Comment helper functions: TODO may split out to new .py file
def commentLoadAll():
    """Grab comments from the toml file or return defaults."""

    clist_defaults = """
[[comment]]
delta = -1
text = "algebra"

[[comment]]
delta = -1
text = "arithmetic"

[[comment]]
delta = "."
text = "meh"

[[comment]]
delta = 0
text = 'tex: you can write latex $e^{i\pi}+1=0$'

[[comment]]
delta = 0
text = "be careful"

[[comment]]
delta = 1
text = "good"

[[comment]]
delta = 1
text = "Quest. 1 specific comment"
tags = "Q1"

[[comment]]
delta = -1
text = "Quest. 2 specific comment"
tags = "Q2 foo bar"
"""
    comment_defaults = {
        "tags": "",
        "created": time.gmtime(0),
        "modified": time.gmtime(0),
    }
    if os.path.exists("plomComments.toml"):
        cdict = toml.load("plomComments.toml")
    else:
        cdict = toml.loads(clist_defaults)
    # should be a dict = {"comment": [list of stuff]}
    assert "comment" in cdict
    clist = cdict["comment"]
    for d in clist:
        for k, v in comment_defaults.items():
            d.setdefault(k, comment_defaults[k])
    return clist


def commentSaveList(clist):
    """Export comment list to toml file."""
    # toml wants a dictionary
    with open("plomComments.toml", "w") as fname:
        toml.dump({"comment": clist}, fname)


def commentVisibleInQuestion(com, n):
    """Return True if comment would be visible in Question n.

    Either there are no Q# tags or there is a Qn tag.

    TODO: eventually should have a comment class: `com.isVisibileInQ(n)`
    """
    Qn = "Q{}".format(n)
    tags = com["tags"].split()
    return any([t == Qn for t in tags]) or not any(
        [re.match("^Q\d+$", t) for t in tags]
    )


def commentTaggedQn(com, n):
    """Return True if comment tagged for Question n.

    There is a Qn tag.
    """
    Qn = "Q{}".format(n)
    tags = com["tags"].split()
    return any([t == Qn for t in tags])


def commentHasMultipleQTags(com):
    tags = com["tags"].split()
    x = [1 if re.match("^Q\d+$", t) else 0 for t in tags]
    return sum(x) >= 2


class CommentWidget(QWidget):
    """A widget wrapper around the marked-comment table."""

    def __init__(self, parent, maxMark):
        # layout the widget - a table and add/delete buttons.
        super(CommentWidget, self).__init__()
        self.parent = parent
        self.maxMark = maxMark
        grid = QGridLayout()
        # the table has 2 cols, delta&comment.
        self.CL = SimpleCommentTable(self)
        grid.addWidget(self.CL, 1, 1, 2, 3)
        self.addB = QPushButton("Add")
        self.delB = QPushButton("Delete")
        grid.addWidget(self.addB, 3, 1)
        grid.addWidget(self.delB, 3, 3)
        self.setLayout(grid)
        # connect the buttons to functions.
        self.addB.clicked.connect(self.addFromTextList)
        self.delB.clicked.connect(self.deleteItem)

    def setStyle(self, markStyle):
        # The list needs a style-delegate because the display
        # of the delta-mark will change depending on
        # the current total mark and whether mark
        # total or up or down. Delta-marks that cannot
        # be assigned will be shaded out to indicate that
        # they will not be pasted into the window.
        self.CL.delegate.style = markStyle

    def changeMark(self, currentMark):
        # Update the current and max mark for the lists's
        # delegate so that it knows how to display the comments
        # and deltas when the mark changes.
        self.CL.delegate.maxMark = self.maxMark
        self.CL.delegate.currentMark = currentMark
        self.CL.viewport().update()

    def saveComments(self):
        self.CL.saveCommentList()

    def addItem(self):
        self.CL.addItem()

    def deleteItem(self):
        self.CL.deleteItem()

    def currentItem(self):
        # grab focus and trigger a "row selected" signal
        # in the comment list
        self.CL.currentItem()
        self.setFocus()

    def nextItem(self):
        # grab focus and trigger a "row selected" signal
        # in the comment list
        self.CL.nextItem()
        self.setFocus()

    def previousItem(self):
        # grab focus and trigger a "row selected" signal
        # in the comment list
        self.CL.previousItem()
        self.setFocus()

    def getCurrentItemRow(self):
        return self.CL.getCurrentItemRow()

    def setCurrentItemRow(self, r):
        self.CL.selectRow(r)

    def addFromTextList(self):
        # text items in scene.
        lst = self.parent.getComments()
        # text items already in comment list
        clist = []
        for r in range(self.CL.cmodel.rowCount()):
            clist.append(self.CL.cmodel.index(r, 1).data())
        # text items in scene not in comment list
        alist = [X for X in lst if X not in clist]

        questnum = int(self.parent.parent.pageGroup)  # YUCK!
        acb = AddCommentBox(self, self.maxMark, alist, questnum)
        if acb.exec_() == QDialog.Accepted:
            if acb.DE.checkState() == Qt.Checked:
                dlt = acb.SB.value()
            else:
                dlt = "."
            txt = acb.TE.toPlainText().strip()
            tag = acb.TEtag.toPlainText().strip()
            # check if txt has any content
            if len(txt) > 0:
                com = {
                    "delta": dlt,
                    "text": txt,
                    "tags": tag,
                    "created": time.gmtime(),
                    "modified": time.gmtime(),
                }
                self.CL.insertItem(com)
                self.currentItem()
                # send a click to the comment button to force updates
                self.parent.ui.commentButton.animateClick()

    def editCurrent(self, com):
        # text items in scene.
        lst = self.parent.getComments()
        # text items already in comment list
        clist = []
        for r in range(self.CL.cmodel.rowCount()):
            clist.append(self.CL.cmodel.index(r, 1).data())
        # text items in scene not in comment list
        alist = [X for X in lst if X not in clist]
        questnum = int(self.parent.parent.pageGroup)  # YUCK!
        acb = AddCommentBox(self, self.maxMark, alist, questnum, com)
        if acb.exec_() == QDialog.Accepted:
            if acb.DE.checkState() == Qt.Checked:
                dlt = str(acb.SB.value())
            else:
                dlt = "."
            txt = acb.TE.toPlainText().strip()
            tag = acb.TEtag.toPlainText().strip()
            # update the comment with new values
            com["delta"] = dlt
            com["text"] = txt
            com["tags"] = tag
            com["modified"] = time.gmtime()
            return com
        else:
            return None


class commentDelegate(QItemDelegate):
    """A style delegate that changes how rows of the
    comment list are displayed. In particular, the
    delta will be shaded out if it cannot be applied
    given the current mark and the max mark.
    Eg - if marking down then all positive delta are shaded
    if marking up then all negative delta are shaded
    if mark = 7/10 then any delta >= 4 is shaded.
    """

    def __init__(self):
        super(commentDelegate, self).__init__()
        self.currentMark = 0
        self.maxMark = 0
        self.style = 0

    def paint(self, painter, option, index):
        # Only run the standard delegate if flag is true.
        # else don't paint anything.
        flag = True
        # Only shade the deltas which are in col 0.
        if index.column() == 0:
            # Grab the delta value.
            delta = index.model().data(index, Qt.EditRole)
            if delta == ".":
                flag = True
            elif self.style == 2:
                # mark up - shade negative, or if goes past max mark
                if int(delta) < 0 or int(delta) + self.currentMark > self.maxMark:
                    flag = False
            elif self.style == 3:
                # mark down - shade positive, or if goes below 0
                if int(delta) > 0 or int(delta) + self.currentMark < 0:
                    flag = False
            elif self.style == 1:
                # mark-total - do not show deltas.
                flag = False
        if flag:
            QItemDelegate.paint(self, painter, option, index)


class commentRowModel(QStandardItemModel):
    """Need to alter the standrd item model so that when we
    drag/drop to rearrange things, the whole row is moved,
    not just the item. Solution found at (and then tweaked)
    https://stackoverflow.com/questions/26227885/drag-and-drop-rows-within-qtablewidget/43789304#43789304
    """

    def setData(self, index, value, role=Qt.EditRole):
        """Simple validation of data in the row. Also convert
        an escaped '\n' into an actual newline for multiline
        comments.
        """
        # check that data in column zero is numeric
        if index.column() == 0:  # try to convert value to integer
            try:
                v = int(value)  # success! is number
                if v > 0:  # if it is positive, then make sure string is "+v"
                    value = "+{}".format(v)
                # otherwise the current value is "0" or "-n".
            except ValueError:
                value = "."  # failed, so set to "."
        # If its column 1 then convert '\n' into actual newline in the string
        elif index.column() == 1:
            value = value.replace(
                "\\n ", "\n"
            )  # so we can latex commands that start with \n
        return super().setData(index, value, role)


class SimpleCommentTable(QTableView):
    """The comment table needs to signal the annotator to tell
    it what the current comment and delta are.
    Also needs to know the current/max mark and marking style
    in order to change the shading of the delta that goes with
    each comment.

    Dragdrop rows solution found at (and tweaked)
    https://stackoverflow.com/questions/26227885/drag-and-drop-rows-within-qtablewidget/43789304#43789304
    """

    # This is picked up by the annotator and tells is what is
    # the current comment and delta
    commentSignal = pyqtSignal(list)

    def __init__(self, parent):
        super(SimpleCommentTable, self).__init__()
        self.parent = parent
        # No numbers down the left-side
        self.verticalHeader().hide()
        # The comment column should be as wide as possible
        self.horizontalHeader().setStretchLastSection(True)
        # Only select one row at a time.
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Drag and drop rows to reorder and also paste into pageview
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        # When clicked, the selection changes, so must emit signal
        # to the annotator.
        self.pressed.connect(self.handleClick)

        # Use the row model defined above, to allow newlines inside comments
        self.cmodel = commentRowModel()
        # self.cmodel = QStandardItemModel()
        self.cmodel.setHorizontalHeaderLabels(["delta", "comment", "idx"])
        self.setModel(self.cmodel)
        # When editor finishes make sure current row re-selected.
        self.cmodel.itemChanged.connect(self.handleClick)
        # Use the delegate defined above to shade deltas when needed
        self.delegate = commentDelegate()
        self.setItemDelegate(self.delegate)
        # A list of comments
        self.clist = commentLoadAll()
        self.populateTable()
        # put these in a timer(0) so they exec when other stuff done
        QTimer.singleShot(0, self.resizeRowsToContents)
        QTimer.singleShot(0, self.resizeColumnsToContents)
        # If an item is changed resize things appropriately.
        self.cmodel.itemChanged.connect(self.resizeRowsToContents)

        # set this so no (native) edit. Instead we'll hijack double-click
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.doubleClicked.connect(self.editRow)
        self.hideColumn(2)

    def dropEvent(self, event: QDropEvent):
        # If drag and drop from self to self.
        if not event.isAccepted() and event.source() == self:
            # grab the row number of dragged row and its data
            row = self.selectedIndexes()[0].row()
            idx = self.cmodel.index(row, 2).data()
            # Get the row on which to drop
            dropRow = self.drop_on(event)
            dropIdx = self.cmodel.index(dropRow, 2).data()
            # If we drag from earlier row, handle index after deletion
            if row < dropRow:
                dropRow -= 1
            com = self.clist.pop(row)
            self.clist.insert(dropRow, com)
            self.populateTable()

            # Reselect the dropped row (TODO: does this work?)
            self.selectRow(dropRow)

            # Resize the rows - they were expanding after drags for some reason
            # TODO: remove?
            self.resizeRowsToContents()
        else:
            super().dropEvent(event)

    def drop_on(self, event):
        # Where is the drop event - which row
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.cmodel.rowCount()
        if self.isBelow(event.pos(), index):
            return index.row() + 1
        else:
            return index.row()

    def isBelow(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() < rect.top() + margin:
            return False
        elif rect.bottom() < pos.y() + margin:
            return True
        # noinspection PyTypeChecker
        return (
            rect.contains(pos, True)
            and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled)
            and pos.y() >= rect.center().y()
        )

    def populateTable(self):
        # first erase rows but don't use .clear()
        self.cmodel.setRowCount(0)
        for i, com in enumerate(self.clist):
            # User can edit the text, but doesn't handle drops.
            # TODO: YUCK! (how do I get the pagegroup)
            pg = int(self.parent.parent.parent.pageGroup)
            if not commentVisibleInQuestion(com, pg):
                continue
            txti = QStandardItem(com["text"])
            txti.setEditable(True)
            txti.setDropEnabled(False)
            dlt = com["delta"]
            # If delta>0 then should be "+n"
            if dlt == ".":
                delti = QStandardItem(".")
            elif int(dlt) > 0:
                delti = QStandardItem("+{}".format(int(dlt)))
            else:
                # is zero or negative - is "0" or "-n"
                delti = QStandardItem("{}".format(dlt))
            # User can edit the delta, but doesn't handle drops.
            delti.setEditable(True)
            delti.setDropEnabled(False)
            delti.setTextAlignment(Qt.AlignCenter)
            idxi = QStandardItem(str(i))
            idxi.setEditable(False)
            idxi.setDropEnabled(False)
            # Append it to the table.
            self.cmodel.appendRow([delti, txti, idxi])

    def handleClick(self, index=0):
        # When an item is clicked, grab the details and emit
        # the comment signal for the annotator to read.
        if index == 0:  # make sure something is selected
            self.currentItem()
        r = self.selectedIndexes()[0].row()
        self.commentSignal.emit(
            [self.cmodel.index(r, 0).data(), self.cmodel.index(r, 1).data()]
        )

    def saveCommentList(self):
        commentSaveList(self.clist)

    def deleteItem(self):
        # Remove the selected row (or do nothing if no selection)
        sel = self.selectedIndexes()
        if len(sel) == 0:
            return
        idx = int(self.cmodel.index(sel[0].row(), 2).data())
        self.clist.pop(idx)
        #self.cmodel.removeRow(sel[0].row())
        # TODO: maybe sloppy to rebuild, need automatic cmodel ontop of clist
        self.populateTable()

    def currentItem(self):
        # If no selected row, then select row 0.
        # else select current row - triggers a signal.
        sel = self.selectedIndexes()
        if len(sel) == 0:
            self.selectRow(0)
        else:
            self.selectRow(sel[0].row())

    def getCurrentItemRow(self):
        if self.selectedIndexes():
            return self.selectedIndexes()[0].row()

    def setCurrentItemRow(self, r):
        self.selectRow(r)

    def nextItem(self):
        # Select next row (wraps around)
        sel = self.selectedIndexes()
        if len(sel) == 0:
            self.selectRow(0)
        else:
            self.selectRow((sel[0].row() + 1) % self.cmodel.rowCount())

    def previousItem(self):
        # Select previous row (wraps around)
        sel = self.selectedIndexes()
        if len(sel) == 0:
            self.selectRow(0)
        else:
            self.selectRow((sel[0].row() - 1) % self.cmodel.rowCount())

    def insertItem(self, com):
        self.clist.append(com)
        self.populateTable()

    def editRow(self, tableIndex):
        r = tableIndex.row()
        idx = int(self.cmodel.index(r, 2).data())
        com = self.clist[idx]
        newcom = self.parent.editCurrent(com)
        if newcom is not None:
            self.clist[idx] = newcom
            self.populateTable()

    def focusInEvent(self, event):
        super(SimpleCommentTable, self).focusInEvent(event)
        # Now give focus back to the annotator
        self.parent.setFocus()


class AddCommentBox(QDialog):
    def __init__(self, parent, maxMark, lst, questnum, com=None):
        super(QDialog, self).__init__()
        self.parent = parent
        self.questnum = questnum
        self.setWindowTitle("Edit comment")
        self.CB = QComboBox()
        self.TE = QTextEdit()
        self.SB = QSpinBox()
        self.DE = QCheckBox("Delta-mark enabled")
        self.DE.setCheckState(Qt.Checked)
        self.DE.stateChanged.connect(self.toggleSB)
        self.TEtag = QTextEdit()
        # TODO: how to make it smaller vertically than the TE?
        #self.TEtag.setMinimumHeight(self.TE.minimumHeight() // 2)
        #self.TEtag.setMaximumHeight(self.TE.maximumHeight() // 2)
        self.QSpecific = QCheckBox("Available only in question {}".format(questnum))
        self.QSpecific.stateChanged.connect(self.toggleQSpecific)
        self.quickHelp = QLabel('Prepend with "tex:" to use math.  You can "Choose text" from an existing annotation.')
        self.quickHelp.setWordWrap(True)

        flay = QFormLayout()
        flay.addRow("Enter text", self.TE)
        flay.addRow("", self.quickHelp)
        flay.addRow("Choose text", self.CB)
        flay.addRow("Set delta", self.SB)
        flay.addRow("", self.DE)
        flay.addRow("", self.QSpecific)
        flay.addRow("Tags", self.TEtag)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        vlay = QVBoxLayout()
        vlay.addLayout(flay)
        vlay.addWidget(buttons)
        self.setLayout(vlay)

        # set up widgets
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.SB.setRange(-maxMark, maxMark)
        self.CB.addItem("")
        self.CB.addItems(lst)
        # Set up TE and CB so that when CB changed, text is updated
        self.CB.currentTextChanged.connect(self.changedCB)
        # If supplied with current text/delta then set them
        if com:
            if com["text"]:
                self.TE.clear()
                self.TE.insertPlainText(com["text"])
            if com["tags"]:
                self.TEtag.clear()
                self.TEtag.insertPlainText(com["tags"])
            if com["delta"]:
                if com["delta"] == ".":
                    self.SB.setValue(0)
                    self.DE.setCheckState(Qt.Unchecked)
                else:
                    self.SB.setValue(int(com["delta"]))
        # TODO: ideally we would do this on TE change signal
        if commentHasMultipleQTags(com):
            self.QSpecific.setEnabled(False)
        elif commentTaggedQn(com, self.questnum):
            self.QSpecific.setCheckState(Qt.Checked)
        else:
            self.QSpecific.setCheckState(Qt.Unchecked)

    def changedCB(self):
        self.TE.clear()
        self.TE.insertPlainText(self.CB.currentText())

    def toggleSB(self):
        if self.DE.checkState() == Qt.Checked:
            self.SB.setEnabled(True)
        else:
            self.SB.setEnabled(False)

    def toggleQSpecific(self):
        tags = self.TEtag.toPlainText().split()
        Qn = "Q{}".format(self.questnum)
        if self.QSpecific.checkState() == Qt.Checked:
            if not Qn in tags:
                tags.insert(0, Qn)
                self.TEtag.clear()
                self.TEtag.insertPlainText(" ".join(tags))
        else:
            if Qn in tags:
                tags.remove(Qn)
                self.TEtag.clear()
                self.TEtag.insertPlainText(" ".join(tags))


class AddTagBox(QDialog):
    def __init__(self, parent, currentTag, tagList=[]):
        super(QDialog, self).__init__()
        self.parent = parent
        self.CB = QComboBox()
        self.TE = QTextEdit()

        flay = QFormLayout()
        flay.addRow("Enter tag\n(max 256 char)", self.TE)
        flay.addRow("Choose tag", self.CB)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        vlay = QVBoxLayout()
        vlay.addLayout(flay)
        vlay.addWidget(buttons)
        self.setLayout(vlay)

        # set up widgets
        buttons.accepted.connect(self.accept)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.CB.addItem("")
        self.CB.addItems(tagList)
        # Set up TE and CB so that when CB changed, text is updated
        self.CB.currentTextChanged.connect(self.changedCB)
        # If supplied with current text/delta then set them
        if currentTag is not None:
            self.TE.clear()
            self.TE.insertPlainText(currentTag)

    def changedCB(self):
        self.TE.clear()
        self.TE.insertPlainText(self.CB.currentText())
