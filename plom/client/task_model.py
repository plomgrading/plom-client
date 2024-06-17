# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2021 Andrew Rechnitzer
# Copyright (C) 2018 Elvis Cai
# Copyright (C) 2019-2024 Colin B. Macdonald
# Copyright (C) 2020 Victoria Schuster
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2022 Lior Silberman
# Copyright (C) 2024 Bryan Tanady

"""Client-side model for tasks, implementation details for MVC stuff."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QModelIndex, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItem, QStandardItemModel

from .useful_classes import ErrorMsg


log = logging.getLogger("marker")


def _marking_time_as_str(m):
    if m < 10:
        # show 2 sigfigs if less than 10
        return f"{m:.2g}"
    else:
        # otherwise show integer
        return f"{m:.0f}"


class MarkerExamModel(QStandardItemModel):
    """A tablemodel for handling the group image marking data."""

    def __init__(self, parent=None):
        """Initializes a new MarkerExamModel.

        Args:
            parent (QStandardItemModel): MarkerExamModel's Parent.
        """
        super().__init__(parent)
        self.setHorizontalHeaderLabels(
            [
                "Task",
                "Status",
                "Mark",
                "Time (s)",
                "Tag",
                "OriginalFiles",
                "AnnotatedFile",
                "PlomFile",
                "PaperDir",
                "integrity_check",
                "src_img_data",
            ]
        )

    def addPaper(
        self,
        task_id_str: str,
        *,
        src_img_data: list[dict[str, Any]] = [],
        status: str = "untouched",
        mark: int = -1,
        marking_time: float = 0,
        tags: list[str] = [],
        integrity_check: str = "",
    ) -> int:
        """Adds a paper to self.

        Args:
            task_id_str: the Task ID for the page being uploaded. Takes the form
                "q1234g9" for paper 1234 question 9.
            status: test status string.
            mark: the mark of the question.
            marking_time (float/int): marking time spent on that page in seconds.
            tags: Tags corresponding to the exam.  We will flatten to a
                space-separated string.  TODO: maybe we should do that for display
                but store as repr/json.
            integrity_check: something from the server, especially legacy
                servers, generally a concat of md5sums of underlying images.
                The server expects us to be able to give it back to them.
            src_img_data: a list of dicts of md5sums, filenames and other
                metadata of the images for the test question.

        Returns:
            The integer row identifier of the added paper.
        """
        # check if paper is already in model - if so, delete it and add it back with the new data.
        # **but** be careful - if annotation in progress then ??
        try:
            r = self._findTask(task_id_str)
        except ValueError:
            pass
        else:
            # TODO: why is the model opening dialogs?!  Issue #2145.
            ErrorMsg(
                None,
                f"Task {task_id_str} has been modified by server - you will need to annotate it again.",
            ).exec()
            self.removeRow(r)
        # Append new groupimage to list and append new row to table.
        r = self.rowCount()
        # hide -1 which something might be using for "not yet marked"
        try:
            markstr = str(mark) if int(mark) >= 0 else ""
        except ValueError:
            markstr = ""
        # these *must* be strings but I don't understand why
        self.appendRow(
            [
                QStandardItem(task_id_str),
                QStandardItem(status),
                QStandardItem(markstr),
                QStandardItem(_marking_time_as_str(marking_time)),
                QStandardItem(" ".join(tags)),
                QStandardItem("placeholder"),
                QStandardItem(""),  # annotatedFile,
                QStandardItem(""),  # plomFile
                QStandardItem("placeholder"),
                # todo - reorder these?
                QStandardItem(integrity_check),
                QStandardItem(repr(src_img_data)),
            ]
        )
        return r

    def _getPrefix(self, r: int) -> str:
        """Return the prefix of the image.

        Args:
            r: the row identifier of the paper.

        Returns:
            the string prefix of the image
        """
        return self.data(self.index(r, 0))

    def _getStatus(self, r: int) -> str:
        """Returns the status of the image.

        Args:
            r: the row identifier of the paper.

        Returns:
            The status of the image
        """
        return self.data(self.index(r, 1))

    def _setStatus(self, r: int, stat: str) -> None:
        """Sets the status of the image.

        Args:
            r: the row identifier of the paper.
            stat: the new status string of the image.

        Returns:
            None
        """
        self.setData(self.index(r, 1), stat)

    def _setAnnotatedFile(self, r: int, aname: str, pname: str) -> None:
        """Set the file name for the annotated image.

        Args:
            r: the row identifier of the paper.
            aname (str): the name for the annotated file.
            pname (str): the name for the .plom file

        Returns:
            None
        """
        self.setData(self.index(r, 6), aname)
        self.setData(self.index(r, 7), pname)

    def _setPaperDir(self, r: int, tdir: str | None) -> None:
        """Sets the paper directory for the given paper.

        Args:
            r: the row identifier of the paper.
            tdir: None or the name of a temporary directory for this paper.

        Returns:
            None
        """
        self.setData(self.index(r, 8), tdir)

    def _clearPaperDir(self, r: int) -> None:
        """Clears the paper directory for the given paper.

        Args:
            r: the row identifier of the paper.

        Returns:
            None
        """
        self._setPaperDir(r, None)

    def _getPaperDir(self, r: int) -> str:
        """Returns the paper directory for the given paper.

        Args:
            r: the row identifier of the paper.

        Returns:
            Name of a temporary directory for this paper.
        """
        return self.data(self.index(r, 8))

    def _get_marking_time(self, r):
        # TODO: instead of packing/unpacking a string, there should be a model
        return float(self.data(self.index(r, 3)))

    def _set_marking_time(self, r, marking_time):
        self.setData(self.index(r, 3), _marking_time_as_str(marking_time))

    def _findTask(self, task: str) -> int:
        """Return the row index of this task.

        Args:
            task (str): the task for the image files to be loaded from.
                Takes the form "q1234g9" = test 1234 question index 9.

        Returns:
            The row index of the task.

        Raises:
             ValueError if not found.
        """
        r0 = []
        for r in range(self.rowCount()):
            if self._getPrefix(r) == task:
                r0.append(r)

        if len(r0) == 0:
            raise ValueError("task {} not found!".format(task))
        elif not len(r0) == 1:
            raise ValueError(
                "Repeated task {} in rows {}  This should not happen!".format(task, r0)
            )
        return r0[0]

    def _setDataByTask(self, task, n, stuff):
        """Find the row identifier with `task` and sets `n`th column to `stuff`.

        Args:
            task (str): the task for the image files to be loaded from.
            n (int): the column to be loaded into.
            stuff: whatever is being added.

        Returns:
            None
        """
        r = self._findTask(task)
        self.setData(self.index(r, n), stuff)

    def _getDataByTask(self, task, n):
        """Returns contents of task in `n`th column.

        Args:
            task (str): the task for the image files to be loaded from.
            n (int): the column to return from.

        Returns:
            Contents of task in `n`th column.
        """
        r = self._findTask(task)
        return self.data(self.index(r, n))

    def getStatusByTask(self, task):
        """Return status for task."""
        return self._getDataByTask(task, 1)

    def setStatusByTask(self, task, st):
        """Set status for task."""
        self._setDataByTask(task, 1, st)

    def getTagsByTask(self, task):
        """Return a list of tags for task.

        TODO: can we draw flat, but use list for storing?
        """
        return self._getDataByTask(task, 4).split()

    def setTagsByTask(self, task, tags):
        """Set a list of tags for task.

        Note: internally stored as flattened string.
        """
        return self._setDataByTask(task, 4, " ".join(tags))

    def get_marking_time_by_task(self, task):
        """Return total marking time (s) for task (str), return float."""
        r = self._findTask(task)
        return self._get_marking_time(r)

    def getAnnotatedFileByTask(self, task):
        """Returns the filename of the annotated image."""
        return Path(self._getDataByTask(task, 6))

    def getPlomFileByTask(self, task):
        """Returns the filename of the plom json data."""
        return Path(self._getDataByTask(task, 7))

    def getPaperDirByTask(self, task):
        """Return temporary directory for this task."""
        return self._getDataByTask(task, 8)

    def setPaperDirByTask(self, task, tdir):
        """Set temporary directory for this grading.

        Args:
            task (str): the task for the image files to be loaded from.
            tdir (dir): the temporary directory for task to be set to.

        Returns:
            None
        """
        self._setDataByTask(task, 8, tdir)

    def _setImageData(self, task, src_img_data):
        """Set the md5sums etc of the original image files."""
        log.debug("Setting img data to {}".format(src_img_data))
        self._setDataByTask(task, 10, repr(src_img_data))

    def get_source_image_data(self, task):
        """Return the image data (as a list of dicts) for task."""
        # dangerous repr/eval pair?  Is json safer/better?
        r = eval(self._getDataByTask(task, 10))
        return r

    def setOriginalFilesAndData(self, task, src_img_data):
        """Set the original un-annotated image filenames and other metadata."""
        self._setImageData(task, src_img_data)

    def setAnnotatedFile(self, task, aname, pname):
        """Set the annotated image and .plom file names."""
        self._setDataByTask(task, 6, aname)
        self._setDataByTask(task, 7, pname)

    def getIntegrityCheck(self, task):
        """Return integrity_check for task as string."""
        return self._getDataByTask(task, 9)

    def markPaperByTask(self, task, mrk, aname, pname, marking_time, tdir) -> None:
        """Add marking data for the given task.

        Args:
            task (str): the task for the image files to be loaded from.
            mrk (int): the mark for this paper.
            aname (str): the annotated file name.
            pname (str): the .plom file name.
            marking_time (int/float): total marking time in seconds.
            tdir (dir): the temporary directory for task to be set to.

        Returns:
            None
        """
        # There should be exactly one row with this Task
        r = self._findTask(task)
        # When marked, set the annotated filename, the plomfile, the mark,
        # and the total marking time (in case it was annotated earlier)
        t = self._get_marking_time(r)
        self._set_marking_time(r, marking_time + t)
        self._setStatus(r, "uploading...")
        self.setData(self.index(r, 2), str(mrk))
        self._setAnnotatedFile(r, aname, pname)
        self._setPaperDir(r, tdir)

    def deferPaper(self, task):
        """Sets the status for the task's paper to deferred."""
        self.setStatusByTask(task, "deferred")

    def removePaper(self, task):
        """Removes the task's paper from self."""
        r = self._findTask(task)
        self.removeRow(r)

    def countReadyToMark(self):
        """Returns the number of untouched Papers."""
        count = 0
        for r in range(self.rowCount()):
            if self._getStatus(r) == "untouched":
                count += 1
        return count


##########################
class ProxyModel(QSortFilterProxyModel):
    """A proxymodel wrapper to handle filtering and sorting of table model."""

    def __init__(self, parent=None):
        """Initializes a new ProxyModel object.

        Args:
            parent (QObject): self's parent.
        """
        super().__init__(parent)
        self.setFilterKeyColumn(4)
        self.filterString = ""
        self.invert = False

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """Sees if left data is less than right data.

        Args:
            left (QModelIndex):
            right (QModelIndex):

        Returns:
            bool: if both can be converted to int, compare as ints.
            Otherwise, convert to strings and compare.
        """
        # try to compare as integers
        try:
            return int(left.data()) < int(right.data())
        except (ValueError, TypeError):
            pass
        # else compare as strings
        return str(left.data()) < str(right.data())

    def setFilterString(self, flt: str) -> None:
        """Sets the Filter String.

        Args:
            flt: the string on which to filter.

        Returns:
            None
        """
        self.filterString = flt

    def filterTags(self, invert=False):
        """Sets the Filter Tags based on string.

        Args:
            invert (bool): True if looking for files that do not have given
                filter string, false otherwise.

        Returns:
            None
        """
        self.invert = invert
        self.setFilterFixedString(self.filterString)

    def filterAcceptsRow(self, pos, index):
        """Checks if a row matches the current filter.

        Notes:
            Overrides base method.

        Args:
            pos (int): row being checked.
            index (any): unused.

        Returns:
            bool: True if filter accepts the row, False otherwise.

        The filter string is first broken into words.  All of those words
        must be in the tags of the row, in any order.  The `invert` flag
        inverts that logic: at least one of the words must not be in the
        tags.
        """
        search_terms = self.filterString.casefold().split()
        tags = self.sourceModel().data(self.sourceModel().index(pos, 4)).casefold()
        all_search_terms_in_tags = all(x in tags for x in search_terms)
        if self.invert:
            return not all_search_terms_in_tags
        return all_search_terms_in_tags

    def getPrefix(self, r: int) -> str:
        """Returns the task code of inputted row index.

        Args:
            r (int): the row identifier of the paper.

        Returns:
            str: the prefix of the paper indicated by r.
        """
        return self.data(self.index(r, 0))

    def getStatus(self, r: int) -> str:
        """Returns the status of inputted row index.

        Args:
            r (int): the row identifier of the paper.

        Returns:
            str: the status of the paper indicated by r.
        """
        # Return the status of the image
        return self.data(self.index(r, 1))

    def getAnnotatedFile(self, r: int) -> str:
        """Returns the file names of an annotated image.

        Args:
            r (int): the row identifier of the paper.

        Returns:
            str: the file name of the annotated image of the paper in r.
        """
        return self.data(self.index(r, 6))

    def rowFromTask(self, task):
        """Return the row index (int) of this task (str) or None if absent."""
        r0 = []
        for r in range(self.rowCount()):
            if self.getPrefix(r) == task:
                r0.append(r)

        if len(r0) == 0:
            return None
        elif not len(r0) == 1:
            raise ValueError(
                "Repeated task {} in rows {}  This should not happen!".format(task, r0)
            )
        return r0[0]
