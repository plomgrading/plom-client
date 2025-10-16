# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2023 Andrew Rechnitzer
# Copyright (C) 2020-2025 Colin B. Macdonald
# Copyright (C) 2022-2023 Natalie Balashov
# Copyright (C) 2024 Aden Chan
# Copyright (C) 2025 Aidan Murphy

"""The Plom Identifier client."""

from __future__ import annotations

import logging
from pathlib import Path
import sys
import tempfile

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

from PyQt6 import QtGui, uic
from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QStringListModel,
    Qt,
    QTimer,
    QVariant,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QCompleter,
    QDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QWidget,
)
from PyQt6.QtGui import QKeySequence, QShortcut

from plomclient.plom_exceptions import (
    PlomBenignException,
    PlomConflict,
    PlomNoClasslist,
    PlomSeriousException,
    PlomTakenException,
)
from plomclient.rules import isValidStudentID
from plomclient.rules import censorStudentName as censorName

from . import ui_files
from .about_dialog import show_about_dialog
from .image_view_widget import ImageViewWidget
from .useful_classes import (
    BlankIDBox,
    ErrorMsg,
    InfoMsg,
    SimpleQuestion,
    SNIDBox,
    WarningQuestion,
    WarnMsg,
)
from .viewers import WholeTestView


log = logging.getLogger("identr")

no_style = ""
angry_orange_style = "background-color: #FF7F50; color: #000;"
warning_yellow_style = "background-color: #FFD700; color: #000"
safe_green_style = "background-color: #00FA9A; color: #000;"
notice_blue_style = "background-color: #89CFF0; color: #000"


# future translation support
def _(x: str) -> str:
    return x


class Paper:
    """A simple container for storing a test's idgroup code (tgv) and associated filename for the image.

    Once identified also store the studentName and ID-number.
    """

    def __init__(
        self, test, fname=None, *, orientation=0, stat="unidentified", id="", name=""
    ):
        # tgv = t0000p00v0
        # ... = 0123456789
        # The test number
        self.test = test
        # Set status as unid'd
        self.status = stat
        # no name or id-number yet.
        self.sname = name
        self.sid = id
        self.originalFile = fname
        self.orientation = orientation

    def setStatus(self, st):
        self.status = st

    def setReverted(self):
        # reset the test as unidentified and no ID or name.
        self.status = "unidentified"
        self.sid = ""
        self.sname = ""

    def setID(self, sid, sname):
        # tgv = t0000p00v0
        # ... = 0123456789
        # Set the test as ID'd and store name / number.
        self.status = "identified"
        self.sid = sid
        self.sname = sname


class ExamModel(QAbstractTableModel):
    """A tablemodel for handling the test-ID-ing data."""

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        # Data stored in this ordered list.
        self.paperList = []
        # Headers.
        self.header = ["Test", "Status", "ID", "Name"]

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        # Columns are [code, status, ID and Name]
        # Put data in appropriate box when setting.
        if role != Qt.ItemDataRole.EditRole:
            return False
        if index.column() == 0:
            self.paperList[index.row()].test = value
            self.dataChanged.emit(index, index)
            return True
        elif index.column() == 1:
            self.paperList[index.row()].status = value
            self.dataChanged.emit(index, index)
            return True
        elif index.column() == 2:
            self.paperList[index.row()].sid = value
            self.dataChanged.emit(index, index)
            return True
        elif index.column() == 3:
            self.paperList[index.row()].sname = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def identifyStudent(self, index, sid, sname):
        # When ID'd - set status, ID and Name.
        self.setData(index[1], "identified")
        self.setData(index[2], sid)
        self.setData(index[3], sname)

    def revertStudent(self, index):
        # When reverted - set status, ID and Name appropriately.
        self.setData(index[1], "unidentified")
        self.setData(index[2], "")
        self.setData(index[3], "")

    def addPaper(self, rho):
        # Append paper to list and update last row of table
        r = self.rowCount()
        self.beginInsertRows(QModelIndex(), r, r)
        self.paperList.append(rho)
        self.endInsertRows()
        return r

    def rowCount(self, parent=None):
        return len(self.paperList)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # Columns are [code, status, ID and Name]
        # Get data from appropriate box when called.
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        elif index.column() == 0:
            return self.paperList[index.row()].test
        elif index.column() == 1:
            return self.paperList[index.row()].status
        elif index.column() == 2:
            return self.paperList[index.row()].sid
        elif index.column() == 3:
            return self.paperList[index.row()].sname
        return QVariant()

    def headerData(self, c, orientation, role):
        # Return the correct header.
        if role != Qt.ItemDataRole.DisplayRole:
            return
        elif orientation == Qt.Orientation.Horizontal:
            return self.header[c]
        return c


# TODO: should be a QMainWindow but at any rate not a Dialog
class IDClient(QWidget):
    my_shutdown_signal = pyqtSignal(int)

    def __init__(self, Qapp, tmpdir=None):
        """Initialize the Identifier Client.

        Args:
            Qapp(QApplication): Main client application
            tmpdir (pathlib.Path/str/None): a temporary directory for
                storing image files and other data.  In principle can
                be shared with Marker although this may not be implemented.
                If `None`, we will make our own.
        """
        super().__init__()
        self.Qapp = Qapp

        uic.loadUi(resources.files(ui_files) / "identifier.ui", self)
        # TODO: temporary workaround
        self.ui = self
        self.ui.explainButton0.setText("FAQ:\nwhy confirm\nprenames?")
        self.ui.explainButton0.clicked.connect(self.prenamed_help)

        # instance vars that get initialized later
        # Save the local temp directory for image files and the class list.
        if not tmpdir:
            tmpdir = tempfile.mkdtemp(prefix="plom_")
        self.workdir = Path(tmpdir)
        self.msgr = None

        self._store_QShortcuts = []

        # controls default behaviour on titlebar close button
        self._hack_prevent_shutdown = True

    def setup(self, messenger):
        """Performs setup procedure for the IDClient.

        Args:
            messenger (Messenger): handles communication with server.

        TODO: move all this into init?
        """
        self.msgr = messenger
        # List of papers we have to ID.
        self.paperList = []
        self.ui.userLabel.setText("logged in as " + self.msgr.username)
        # Exam model for the table of papers - associate to table in GUI.
        self.exM = ExamModel()
        self.ui.tableView.setModel(self.exM)
        # A view window for the papers so user can zoom in as needed.
        # Paste into appropriate location in gui.
        self.testImg = ImageViewWidget(self)
        self.ui.rightPaneLayout.addWidget(self.testImg, 10)

        self.ui.hamMenuButton.setMenu(self.build_hamburger())
        self.ui.hamMenuButton.setText("\N{TRIGRAM FOR HEAVEN}")
        self.ui.hamMenuButton.setToolTip("Menu (F10)")
        self.ui.hamMenuButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        sc = QShortcut(QKeySequence("F10"), self)
        sc.activated.connect(self.ui.hamMenuButton.animateClick)
        self._store_QShortcuts.append(sc)

        self.ui.closeButton.clicked.connect(self._close_but_dont_quit)

        # Get the classlist from server for name/ID completion.
        try:
            self.getClassList()
        except PlomNoClasslist as e:
            WarnMsg(
                self,
                "Cannot identify papers until server has a classlist.",
                info=str(e),
            ).exec()
            return

        # Init the name/ID completers and a validator for ID
        self.setCompleters()
        # Get the predicted list from server for ID guesses.
        self.getPredictions()

        # Connect buttons and key-presses to functions.
        self.ui.idEdit.returnPressed.connect(self.enterID)
        self.ui.saveButton.clicked.connect(self.enterID)
        self.ui.nextButton.clicked.connect(self.skipOnClick)
        self.ui.predButton0.clicked.connect(self.acceptPrediction0)
        self.ui.blankButton.clicked.connect(self.blankPaper)
        self.ui.viewButton.clicked.connect(self.viewWholePaper)

        # Make sure no button is clicked by a return-press
        self.ui.nextButton.setAutoDefault(False)
        self.ui.closeButton.setAutoDefault(False)

        # Make sure window is maximised and request a paper from server.
        self.showMaximized()
        # Get list of papers already ID'd and add to table.
        self.getAlreadyIDList()

        # Connect the view **after** list updated.
        # Connect the table's model sel-changed to appropriate function.
        self.ui.tableView.selectionModel().selectionChanged.connect(self.selChanged)
        self.requestNext()

        # TODO: seems to behave ok without this hack: delete?
        # self.testImg.forceRedrawOrSomeBullshit()

        # Create variable to store ID/Name conf window position
        # Initially set to top-left corner of window
        self.msgGeometry = None

    def build_hamburger(self):
        m = QMenu()

        # TODO: use \N{CLOCKWISE OPEN CIRCLE ARROW} as the icon
        # m.addAction("Refresh task list", self.refresh_server_data)
        m.addAction("View whole paper...", self.viewWholePaper)
        m.addSeparator()

        # m.addAction("Help", self.show_help)
        m.addAction("About Plom", lambda: show_about_dialog(self))

        m.addSeparator()

        key = "ctrl+w"
        command = self._close_but_dont_quit
        sc = QShortcut(QKeySequence(key), self)
        sc.activated.connect(command)
        self._store_QShortcuts.append(sc)
        key = QKeySequence(key).toString(QKeySequence.SequenceFormat.NativeText)
        m.addAction(f"Change task or server\t{key}", command)

        key = "ctrl+q"
        command = self._close_and_quit
        sc = QShortcut(QKeySequence(key), self)
        sc.activated.connect(command)
        self._store_QShortcuts.append(sc)
        key = QKeySequence(key).toString(QKeySequence.SequenceFormat.NativeText)
        m.addAction(f"Quit\t{key}", command)

        return m

    def _close_but_dont_quit(self):
        # unpleasant hackery but gets job done
        self._hack_prevent_shutdown = True
        self.close()

    def _close_and_quit(self):
        # unpleasant hackery but gets job done
        self._hack_prevent_shutdown = False
        self.close()

    def skipOnClick(self):
        """Skip the current, moving to the next or loading a new one."""
        index = self.ui.tableView.selectedIndexes()
        if len(index) == 0:
            return
        r = index[0].row()  # which row is selected
        if r == self.exM.rowCount() - 1:  # the last row is selected.
            if self.requestNext():
                return
        self.moveToNextUnID()

    def getClassList(self):
        """Get the classlist from the server.

        Here and throughout 'snid' means "student_id_and_name" as one string.

        Returns nothing but modifies the state of self, adding three
        dicts to the class data:

        `snid_to_student_id`
        `snid_to_student_name`
        `student_id_to_snid`

        Raises:
            PlomNoClasslist
        """
        classlist = self.msgr.IDrequestClasslist()
        self.snid_to_student_id = dict()
        self.snid_to_student_name = dict()
        self.student_id_to_snid = dict()
        name_list = []
        for person in classlist:
            # TODO: Issue #1646 here we want student number with id fallback?
            sid = person["id"]
            sname = person["name"]
            snid = f"{sid}: {sname}"
            self.snid_to_student_id[snid] = sid
            self.snid_to_student_name[snid] = sname
            self.student_id_to_snid[sid] = snid

            if sname in name_list:
                log.warning(
                    'Just FYI: multiple students with name "%s"', censorName(sname)
                )
            name_list.append(sname)

    def getPredictions(self):
        """Send request for prediction list to server."""
        self.predictions = self.msgr.IDgetPredictions()

    def setCompleters(self):
        """Set up the studentname + studentID line-edit completers.

        Means that user can enter the first few numbers (or letters) and
        be prompted with little pop-up with list of possible completions.
        """
        # Build stringlistmodels - one for combined student_name_and_id = snid
        snidlist = QStringListModel()
        # Feed in the numbers and names.
        snidlist.setStringList(list(self.snid_to_student_id.keys()))
        # Build the snid-completer = substring matching and case insensitive
        snidcompleter = QCompleter()
        snidcompleter.setModel(snidlist)
        snidcompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        snidcompleter.setFilterMode(Qt.MatchFlag.MatchContains)
        # Link the ID-completer to the ID-lineedit in the gui.
        self.ui.idEdit.setCompleter(snidcompleter)
        # Make sure lineedit has little "Clear this" button.
        self.ui.idEdit.setClearButtonEnabled(True)

    def shutDownError(self):
        """Shuts down self due to error."""
        log.error("Shutting down due to error")
        self.close()

    def closeEvent(self, event: None | QtGui.QCloseEvent) -> None:
        log.debug("Something has triggered a shutdown event")
        log.debug("Revoking login token")
        self.msgr.closeUser(revoke_token=True)
        log.debug("Emitting Identifier shutdown signal")
        retval = 2 if self._hack_prevent_shutdown else 1
        self.my_shutdown_signal.emit(retval)
        if event:
            event.accept()
        log.debug("Identifier: goodbye!")

    def getAlreadyIDList(self):
        # Ask server for list of previously ID'd papers
        idList = self.msgr.IDrequestDoneTasks()
        for x in idList:
            self.addPaperToList(
                Paper(
                    x[0],
                    fname=None,
                    orientation=0,
                    stat="identified",
                    id=x[1],
                    name=x[2],
                ),
                update=False,
            )

    def selChanged(self, selnew, selold):
        # When the selection changes, update the ID and name line-edit boxes
        # with the data from the table - if it exists.
        # Update the displayed image with that of the newly selected test.
        self.ui.idEdit.setText(self.exM.data(selnew.indexes()[2]))
        self.updateImage(selnew.indexes()[0].row())
        self.ui.idEdit.setFocus()

    def checkFiles(self, r):
        # grab the selected tgv
        test = self.exM.paperList[r].test
        # check if we have a copy
        if self.exM.paperList[r].originalFile is not None:
            return
        # else try to grab it from server
        pagedata = self.msgr.get_pagedata(test)
        id_pages = []
        for row in pagedata:
            # Issue #2707: better use a image-type key
            if not row["pagename"].casefold().startswith("id"):
                continue
            img_bytes = self.msgr.get_image(row["id"], row["md5"])
            ext = Path(row["server_path"]).suffix
            filename = self.workdir / f'img_{int(test):04}_{row["pagename"]}{ext}'
            with open(filename, "wb") as fh:
                fh.write(img_bytes)
            angle = row["orientation"]
            id_pages.append([filename, angle])
        if not id_pages:
            InfoMsg(
                self,
                "Unexpectedly no ID page: see Issue #2722 and related.  "
                "Could happen if someone is mucking around in the management tool.",
            ).exec()
            return
        assert len(id_pages) == 1, "Expected exactly one ID page"
        (
            imageName,
            angle,
        ) = id_pages[0]

        self.exM.paperList[r].originalFile = imageName
        self.exM.paperList[r].orientation = angle

    def updateImage(self, r=0):
        # Here the system should check if imagefile exist and grab if needed.
        self.checkFiles(r)
        # Update the test-image pixmap with the image in the indicated file.
        self.testImg.updateImage(
            [
                {
                    "filename": self.exM.paperList[r].originalFile,
                    "orientation": self.exM.paperList[r].orientation,
                }
            ],
            keep_zoom=True,
        )
        # update the prediction if present
        tn = int(self.exM.paperList[r].test)

        all_predictions = self.predictions.get(str(tn), None)

        # helper function to hide all this SNID garbage
        def get_name_from_id(sid) -> str | None:
            try:
                _snid = self.student_id_to_snid[sid]
                return self.snid_to_student_name[_snid]
            except KeyError:
                return None

        # Reset everything, fonts, etc then hide the boxes
        fnt = self.font()
        fnt.setPointSize(fnt.pointSize() * 2)
        self.ui.pNameLabel0.setFont(fnt)
        # also tweak size of "accept prediction" button font
        self.ui.predButton0.setFont(fnt)
        # make the SID larger still.
        fnt.setPointSizeF(fnt.pointSize() * 1.5)
        self.ui.pSIDLabel0.setFont(fnt)
        self.ui.pSIDLabel0.setText("")
        self.ui.pNameLabel0.setText("")
        self.ui.predictionBox0.setTitle("No prediction")
        self.ui.predictionBox0.setStyleSheet(no_style)
        self.ui.predButton0.hide()
        self.ui.predictionBox0.hide()
        self.ui.predictionBox1.setTitle("No prediction")
        self.ui.predictionBox1.setStyleSheet(no_style)
        # remove the old widgets
        lay = self.ui.predictionBox1.layout()
        for i in reversed(range(lay.count())):
            # print(f"deleting i={i}")
            w = lay.itemAt(i).widget()
            if w:
                w.deleteLater()
            del w
        del lay
        self.ui.predictionBox1.hide()
        self.ui.explainButton0.hide()

        # # Debugging
        # if len(all_predictions) >= 1:
        #     from random import random
        #
        #     if random() > 0.7:
        #         all_predictions[0]["student_id"] = "12345678"
        #     if len(all_predictions) > 1:
        #         if random() > 0.7:
        #             all_predictions[1]["student_id"] = "12345678"
        #     if len(all_predictions) > 2:
        #         if random() > 0.7:
        #             all_predictions[2]["student_id"] = "12345678"

        if not all_predictions:
            pass
        elif (
            len(all_predictions) == 1
            and all_predictions[0]["predictor"].casefold() == "prename"
        ):
            (pred,) = all_predictions
            predicted_name = get_name_from_id(pred["student_id"])

            self.ui.explainButton0.show()
            self.ui.predictionBox0.show()

            self.ui.pSIDLabel0.setText(pred["student_id"])
            if predicted_name:
                self.ui.pNameLabel0.setText(predicted_name)
                self.ui.predButton0.show()
            else:
                self.ui.pNameLabel0.setText("<b>[" + _("Not in classlist!") + "]</b>")
                self.ui.predButton0.hide()

            self.ui.predictionBox0.setTitle(
                "Prenamed paper: is it signed?  if not signed, is it blank?"
            )
            self.ui.predButton0.setText("Confirm\n&Prename")
            self.ui.predictionBox0.setStyleSheet(notice_blue_style)

        else:
            pred0 = all_predictions[0]
            if all(p["student_id"] == pred0["student_id"] for p in all_predictions):
                self.ui.predictionBox0.show()
                self.ui.pSIDLabel0.setText(pred0["student_id"])
                predicted_name = get_name_from_id(pred0["student_id"])
                if predicted_name:
                    self.ui.pNameLabel0.setText(predicted_name)
                    self.ui.predButton0.show()
                else:
                    self.ui.pNameLabel0.setText(
                        "<b>[" + _("Not in classlist!") + "]</b>"
                    )
                    self.ui.predButton0.hide()
                self.ui.predictionBox0.setTitle(
                    "All predictions agree: "
                    + "; ".join(
                        [
                            f"certainty {round(p['certainty'], 3)} by {p['predictor']}"
                            for p in all_predictions
                        ]
                    )
                )
                # only single option shown, so keep alt-a shortcut
                self.ui.predButton0.setText("&Accept\nPrediction")
                if all(p["certainty"] >= 0.3 for p in all_predictions):
                    self.ui.predictionBox0.setStyleSheet(safe_green_style)
                else:
                    self.ui.predictionBox0.setStyleSheet(angry_orange_style)

            else:
                warn = False
                serious_warn = False

                # so meta, so annoying!
                def _func_factory(zelf, sid, name):
                    def f():
                        zelf.accept_prediction(sid, name)

                    return f

                lay = self.ui.predictionBox1.layout()
                lay.setSpacing(12)

                # messy proprocessing to get histgram-like representation of duplicate predictions
                preds_dup_dict = {}
                for i, p in enumerate(all_predictions):
                    sid = p["student_id"]
                    if sid in preds_dup_dict.keys():
                        continue
                    preds_dup_dict[sid] = []
                    for j, q in enumerate(all_predictions):
                        if j < i:
                            continue
                        if q["student_id"] == sid:
                            preds_dup_dict[sid].append(q)
                preds_hist = [(len(pl), pl) for k, pl in preds_dup_dict.items()]
                preds_hist.sort(reverse=True, key=lambda x: x[0])
                # discard the counts
                preds_hist = [pl for (count, pl) in preds_hist]

                if (
                    len(preds_hist) == 2
                    and len(preds_hist[1]) == 1
                    and preds_hist[1][0]["predictor"].casefold() == "mlbestguess"
                ):
                    log.debug("Prediction: Only 'MLBestGuess' disagrees so don't warn")
                else:
                    warn = True

                for i, predlist in enumerate(preds_hist):
                    sid = predlist[0]["student_id"]
                    name = get_name_from_id(sid)
                    in_classlist = True
                    disp_name = name
                    if not name:
                        disp_name = "[" + _("Not in classlist!") + "]"
                        in_classlist = False
                        if (
                            len(predlist) == 1
                            and predlist[0]["predictor"].casefold() == "mlbestguess"
                        ):
                            # MLBestGuess doesn't consider the classlist so it often a bit wrong
                            pass
                        else:
                            # but in other cases, we consider this to be a serious problem
                            serious_warn = True

                    predstr = "; ".join(
                        f"{p['predictor']} ({round(p['certainty'], 3)})"
                        for p in predlist
                    )
                    lay.addItem(
                        QSpacerItem(
                            32,
                            10,
                            QSizePolicy.Policy.MinimumExpanding,
                            QSizePolicy.Policy.Minimum,
                        ),
                        i,
                        0,
                    )
                    if not in_classlist:
                        lay.addWidget(QLabel("<b>*</b>"), i, 1)
                    lay.addWidget(QLabel(predstr), i, 2)
                    lay.addWidget(QLabel(sid), i, 3)
                    lay.addWidget(QLabel(f"<em>{disp_name}</em>"), i, 4)
                    if in_classlist:
                        q = QPushButton(f"Accept {sid}")
                        q.setToolTip(f"Identify this paper as {sid}, {disp_name}")
                        f = _func_factory(self, sid, name)
                        q.clicked.connect(f)
                        fnt = self.font()
                        fnt.setPointSizeF(fnt.pointSize() * 1.5)
                        q.setFont(fnt)
                        lay.addWidget(q, i, 5)

                # TODO: "and at least one not in class"?
                self.ui.predictionBox1.setTitle(
                    f"Disagreement among {len(all_predictions)} predictors"
                )
                self.ui.predictionBox1.show()
                if warn:
                    self.ui.predictionBox1.setStyleSheet(warning_yellow_style)
                if serious_warn:
                    self.ui.predictionBox1.setStyleSheet(angry_orange_style)

        # now update the snid entry line-edit.
        # if test is already identified then populate the ID-lineedit accordingly
        if self.exM.paperList[r].status == "identified":
            snid = "{}: {}".format(
                self.exM.paperList[r].sid, self.exM.paperList[r].sname
            )
            self.ui.idEdit.setText(snid)
        else:  # leave it blank.
            self.ui.idEdit.clear()
        self.ui.idEdit.setFocus()

    def addPaperToList(self, paper, update=True):
        # Add paper to the exam-table-model - get back the corresponding row.
        r = self.exM.addPaper(paper)
        # select that row and display the image
        if update:
            # One more unid'd paper
            self.ui.tableView.selectRow(r)
            self.updateImage(r)

    def updateProgress(self):
        # update progressbars
        v, m = self.msgr.IDprogressCount()
        if m == 0:
            v, m = (0, 1)  # avoid (0, 0) indeterminate animation
            self.ui.idProgressBar.setFormat("No papers to identify")
            InfoMsg(self, "No papers to identify.").exec()
        else:
            self.ui.idProgressBar.resetFormat()
        self.ui.idProgressBar.setMaximum(m)
        self.ui.idProgressBar.setValue(v)

    def requestNext(self):
        """Ask the server for an unID'd paper, get file, add to list, update image."""
        self.updateProgress()

        attempts = 0
        while True:
            # TODO - remove this little sanity check else replace with a pop-up warning thingy.
            if attempts >= 5:
                return False
            else:
                attempts += 1
            # ask server for ID of next task
            try:
                test = self.msgr.IDaskNextTask()
                if test is None:
                    InfoMsg(self, "No more tasks left on server.").exec()
                    return False
            except PlomSeriousException as err:
                log.exception("Unexpected error getting next task: %s", err)
                ErrorMsg(
                    self,
                    "Unexpected error getting next task:\n"
                    f"{err}\nClient will now crash!",
                ).exec()
                raise

            try:
                self.msgr.IDclaimThisTask(test)
                break
            except PlomTakenException as err:
                log.info("will keep trying as task already taken: {}".format(err))
                continue

        pagedata = self.msgr.get_pagedata(test)
        id_pages = []
        for row in pagedata:
            # Issue #2707: better use a image-type key
            if not row["pagename"].casefold().startswith("id"):
                continue
            img_bytes = self.msgr.get_image(row["id"], row["md5"])
            ext = Path(row["server_path"]).suffix
            filename = self.workdir / f'img_{int(test):04}_{row["pagename"]}{ext}'
            with open(filename, "wb") as fh:
                fh.write(img_bytes)
            angle = row["orientation"]
            id_pages.append([filename, angle])
        if not id_pages:
            InfoMsg(
                self,
                "Unexpectedly no ID page: see Issue #2722 and related.  "
                "Could happen if someone is mucking around in the management tool.",
            ).exec()
            return False
        assert len(id_pages) == 1, "Expected exactly one ID page"
        (
            filename,
            angle,
        ) = id_pages[0]

        # Add the paper [code, filename, etc] to the list
        self.addPaperToList(Paper(test, filename, orientation=angle))

        # Clean up table - and set focus on the ID-lineedit so user can
        # just start typing in the next ID-number.
        self.ui.tableView.resizeColumnsToContents()
        self.ui.idEdit.setFocus()
        return True

    def acceptPrediction0(self):
        sname = self.ui.pNameLabel0.text()
        sid = self.ui.pSIDLabel0.text()
        self.accept_prediction(sid, sname)

    def accept_prediction(self, sid: str, sname: str) -> None:
        log.info("Accepting id=%s, name='%s' from prediction...", sid, sname)
        # first check currently selected paper is unidentified - else do nothing
        index = self.ui.tableView.selectedIndexes()
        status = self.exM.data(index[1])
        if status != "unidentified":
            msg = SimpleQuestion(self, "Do you want to change the ID?")
            # Put message popup on top-corner of identifier window
            if msg.exec() == QMessageBox.StandardButton.No:
                return
        # code = self.exM.data(index[0])

        if not self.identifyStudent(index, sid, sname):
            return

        if index[0].row() == self.exM.rowCount() - 1:  # at bottom of table.
            self.requestNext()  # updates progressbars.
        else:  # else move to the next unidentified paper.
            self.moveToNextUnID()  # doesn't
            self.updateProgress()

    def identifyStudent(
        self,
        index,
        sid: str | None,
        sname: str,
        *,
        blank: bool = False,
        no_id: bool = False,
    ) -> bool | None:
        """Push identification of a paper to the server and misc UI table.

        User ID's the student of the current paper. Some care around whether
        or not the paper was ID'd previously. Not called directly - instead
        is called by "enterID" or "accept_prediction" when user hits return on the line-edit.

        Args:
            index: an index into the UI table of the currently
                highlighted row.
            sid: The student ID or None.
                - note that this is either 'None' (but only if blank or no_id is true), or
                should have passed the 'is_valid_id' test.
            sname: The student name or special placeholder.
                - note that this should always be non-trivial string.

        Keyword Args:
            blank (bool): the paper was blank: `sid` must be None and
                `sname` must be `"Blank paper"`.
            no_id (bool): paper is not blank but student did not fill-in
                the ID page(s).  `sid` must be None and `sname` must be
                `"No ID given"`.

        Returns:
            True/False/None: True on success, False/None on failure.
        """
        log.info(
            "Identifying id=%s, name='%s', blank=%s, no_id=%s...",
            sid,
            sname,
            blank,
            no_id,
        )
        # do some sanity checks on inputs.
        assert isinstance(sname, str), "Student must be a string"
        assert len(sname) > 0, "Student name cannot be empty"
        # check that sid is none only when blank or no_id is true
        if sid is None:
            assert (
                blank or no_id
            ), "Student ID is only None-type when blank paper or no ID given."
        # similarly blank only when sid=None and sname = "Blank paper"
        if blank:
            assert (sid is None) and (
                sname == "Blank paper"
            ), "Blank should only be true when sid=None and sname = 'Blank paper'"
        # similarly no_id only when sid=None and sname = "No ID given"
        if no_id:
            assert (sid is None) and (
                sname == "No ID given"
            ), "No_id should only be true when sid=None and sname = 'No ID given'"

        # Pass the info to the exam model to put data into the table.
        self.exM.identifyStudent(index, sid, sname)
        code = self.exM.data(index[0])
        # Return paper to server with the code, ID, name.
        log.info(
            "Sending identity to server for code=%s: id=%s, name='%s', blank=%s, no_id=%s",
            code,
            sid,
            sname,
            blank,
            no_id,
        )
        try:
            self.msgr.IDreturnIDdTask(code, sid, sname)
        except PlomConflict as err:
            log.warning("Conflict when returning paper %s: %s", code, err)
            hints = """
                <p>If you are unable to resolve this conflict, you may need
                to use the Manager tool to "Un-ID" the other paper.</p>
            """
            WarnMsg(self, str(err), info=hints, info_pre=False).exec()
            self.exM.revertStudent(index)
            return False
        except PlomBenignException as err:
            log.error("Somewhat unexpected error when returning %s: %s", code, err)
            WarnMsg(self, f'Unexpected but benign exception:\n"{err}"').exec()
            self.exM.revertStudent(index)
            return False
        # successful ID
        # Issue #23: Use timer to avoid macOS conflict between completer and
        # clearing the line-edit. Very annoying but this fixes it.
        QTimer.singleShot(0, self.ui.idEdit.clear)
        self.updateProgress()
        return True

    def moveToNextUnID(self):
        # Move to the next test in table which is not ID'd.
        rt = self.exM.rowCount()
        if rt == 0:
            return
        rstart = self.ui.tableView.selectedIndexes()[0].row()
        r = (rstart + 1) % rt
        # Be careful to not get stuck in loop if all are ID'd.
        while self.exM.data(self.exM.index(r, 1)) == "identified" and r != rstart:
            r = (r + 1) % rt
        self.ui.tableView.selectRow(r)

    def enterID(self):
        """Triggered when user hits return in the ID-lineedit.

        For example, when they have entered a full student ID.
        """
        # check that the student name / id line-edit has some text.
        if len(self.ui.idEdit.text()) == 0:
            InfoMsg(
                self,
                'Please use the "Blank page" button if student has not '
                "given their name or ID.",
            ).exec()
            return

        # if no papers then simply return.
        if self.exM.rowCount() == 0:
            return
        # Grab table-index and code of current test.
        index = self.ui.tableView.selectedIndexes()
        code = self.exM.data(index[0])
        # No code then return.
        if code is None:
            return
        # Get the status of the test
        status = self.exM.data(index[1])
        alreadyIDd = False
        # If the paper is already ID'd ask the user if they want to
        # change it - set the alreadyIDd flag to true.
        if status == "identified":
            msg = SimpleQuestion(self, "Do you want to change the ID?")
            # Put message popup on top-corner of identifier window
            if msg.exec() == QMessageBox.StandardButton.No:
                return
            else:
                alreadyIDd = True

        # Check if the entered SNID (student name and id) is in the list from the classlist.
        if self.ui.idEdit.text() in self.snid_to_student_id:
            # Ask user to confirm ID/Name
            msg = SimpleQuestion(
                self,
                f'Student "<b>{self.ui.idEdit.text()}</b>".',
                "Save and move to next?",
            )
            # Put message popup in its last location
            if self.msgGeometry is not None:
                msg.setGeometry(self.msgGeometry)

            # If user says "no" then just return from function.
            if msg.exec() == QMessageBox.StandardButton.No:
                self.msgGeometry = msg.geometry()
                return
            self.msgGeometry = msg.geometry()

            snid = self.ui.idEdit.text()
            sid = self.snid_to_student_id[snid]
            sname = self.snid_to_student_name[snid]

        else:
            msg = WarningQuestion(
                self,
                f'Student "{self.ui.idEdit.text()}" not found in classlist.',
                "Do you want to input the ID and name manually?",
            )
            # Put message popup on top-corner of identifier window
            msg.move(self.pos())
            # If no then return from function.
            if msg.exec() == QMessageBox.StandardButton.No:
                self.msgPosition = msg.pos()
                return
            self.msgPosition = msg.pos()
            # Otherwise get an id and name from the user (and the okay)
            snidbox = SNIDBox(self, self.ui.idEdit.text())
            if snidbox.exec() != QDialog.DialogCode.Accepted:
                return
            sid = snidbox.sid.strip()
            sname = snidbox.sname.strip()
            # note sid, sname will not be None-types.
            if not isValidStudentID(sid):  # this should not happen as snidbox checks.
                return
            if not sname:  # this should not happen as snidbox checks.
                return

            # check if SID is actually in classlist.
            if sid in self.student_id_to_snid:
                WarnMsg(
                    self,
                    f"<p>ID &ldquo;{sid}&rdquo; is in classlist as "
                    f"&ldquo;{self.student_id_to_snid[sid]}&rdquo;.</p>"
                    "<p>Cannot enter them into the classlist without "
                    "a unique ID.</p>",
                ).exec()
                return
            snid = f"{sid}: {sname}"
            # update our lists
            self.snid_to_student_id[snid] = sid
            self.snid_to_student_name[snid] = sname
            self.student_id_to_snid[sid] = snid
            # finally update the line-edit.  TODO: remove? used to be for identifyStudent call below but not needed anymore?
            self.ui.idEdit.setText(snid)

        # Run identify student command (which talks to server)
        if self.identifyStudent(index, sid, sname):
            if alreadyIDd:
                self.moveToNextUnID()
                return
            if index[0].row() == self.exM.rowCount() - 1:  # last row is highlighted
                if self.requestNext():
                    return
            self.moveToNextUnID()

    def viewWholePaper(self):
        index = self.ui.tableView.selectedIndexes()
        if len(index) == 0:
            return
        testnum = self.exM.data(index[0])
        pagedata = self.msgr.get_pagedata(testnum)
        pagedata = self.Qapp.downloader.sync_downloads(pagedata)
        labels = [x["pagename"] for x in pagedata]
        WholeTestView(testnum, pagedata, labels, parent=self).exec()

    def blankPaper(self) -> None:
        # first check currently selected paper is unidentified - else do nothing
        index = self.ui.tableView.selectedIndexes()
        if len(index) == 0:
            return
        # status = self.exM.data(index[1])
        # if status != "unidentified":
        # return
        code = self.exM.data(index[0])
        rv = BlankIDBox(self, code).exec()
        # return values 0=cancel, 1=blank paper, 2=no id given.
        if rv == 0:
            return
        elif rv == 1:
            # return with sname ='blank paper', and sid = None
            self.identifyStudent(index, None, "Blank paper", blank=True)
        else:
            # return with sname ='no id given', and sid = None
            self.identifyStudent(index, None, "No ID given", no_id=True)

        if index[0].row() == self.exM.rowCount() - 1:  # at bottom of table.
            self.requestNext()  # updates progressbars.
        else:  # else move to the next unidentified paper.
            self.moveToNextUnID()  # doesn't
            self.updateProgress()
        return

    def prenamed_help(self) -> None:
        InfoMsg(
            self,
            "<p>It might seem unnecessary to confirm the prenamed papers "
            "but there are several situations to watch out for:</p>"
            "<ul>"
            "<li>Student X wrote paper N: they likely scratched out the "
            "name and substituted their own.</li>"
            "<li>Student X did not sit the assessment, but the prenamed "
            "paper was accidentally scanned: it will be "
            "unsigned&mdash;click the &ldquo;Blank&rdquo; button.</li>"
            "</ul>",
        ).exec()
