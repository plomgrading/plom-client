# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Julian Lapenna

import fitz
import os
from pathlib import Path
from plom.create.demotools import buildDemoSourceFiles
from plom.create.buildDatabaseAndPapers import check_equal_page_count


def test_equal_page_count_true(tmpdir):
    """Checks that the page counts of each source version pdf are equal.

    Arguments:
        tmpdir (dir): The directory holding the source version pdfs.
    """
    # check that it passes when the page counts are equal
    tmp = Path(tmpdir)
    # build the source version pdfs in sourceVersions/
    buildDemoSourceFiles(tmp)
    check_true = check_equal_page_count(tmp / "sourceVersions")
    assert check_true


def test_equal_page_count_false(tmpdir):
    # check that it fails when the page counts are not equal
    tmp = Path(tmpdir)
    # build the source version pdfs in sourceVersions/
    buildDemoSourceFiles(tmp)
    # create a new file with a single page
    clone = fitz.open()
    clone.new_page()
    clone.save(tmp / "sourceVersions/version3.pdf")
    # check that the page counts are no longer equal
    check_false = check_equal_page_count(tmp / "sourceVersions")
    assert not check_false
    # delete version3.pdf
    os.remove(tmp / "sourceVersions/version3.pdf")
