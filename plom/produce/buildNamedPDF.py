# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2019-2020 Andrew Rechnitzer
# Copyright (C) 2019-2020 Colin B. Macdonald

import os
from pathlib import Path
from multiprocessing import Pool
from tqdm import tqdm

from .mergeAndCodePages import make_PDF
from . import paperdir


def _make_PDF(x):
    """Call make_PDF from mergeAndCodePages with arguments expanded.

    *Note*: this is a little bit of glue to make the parallel Pool code
    elsewhere work.

    Arguments:
        x (tuple): this is expanded as the arguments to :func:`make_PDF`.
    """
    make_PDF(*x)


def build_all_papers(spec, global_page_version_map, classlist):
    """Builds the papers using _make_PDF.

    Based on `numberToName` this uses `_make_PDF` to create some
    papers with names stamped on the front as well as some papers without.

    For the prenamed papers, names and IDs are taken in order from the
    classlist.

    Arguments:
        spec {dict} -- A dictionary embedding the exam info. This dictionary does not have a normal format.
                       Example below:
                       {
                       'name': 'plomdemo',
                       'longName': 'Midterm Demo using Plom',
                       'numberOfVersions': 2,
                       'numberOfPages': 6,
                       'numberToProduce': 20,
                       'numberToName': 10,
                       'numberOfQuestions': 3,
                       'privateSeed': '1001378822317872',
                       'publicCode': '270385',
                       'idPages': {'pages': [1]},
                       'doNotMark': {'pages': [2]},
                       'question': {
                           '1': {'pages': [3], 'mark': 5, 'select': 'shuffle'},
                           '2': {'pages': [4], 'mark': 10, 'select': 'fix'},
                           '3': {'pages': [5, 6], 'mark': 10, 'select': 'shuffle'} }
                          }
                       }
        global_page_version_map (dict): dict of dicts mapping first by
            paper number (int) then by page number (int) to version (int).
        classlist (list, None): ordered list of (sid, sname) pairs.

    Raises:
        ValueError: classlist is invalid in some way.
    """
    if spec["numberToName"] > 0:
        if not classlist:
            raise ValueError("You must provide a classlist to prename papers")
        if len(classlist) < spec["numberToName"]:
            raise ValueError(
                "Classlist is too short for {} pre-named papers".format(spec["numberToName"])
            )
    make_PDF_args = []
    for paper_index in range(1, spec["numberToProduce"] + 1):
        page_version = global_page_version_map[paper_index]
        if paper_index <= spec["numberToName"]:
            student_info = {
                "id": classlist[paper_index - 1][0],
                "name": classlist[paper_index - 1][1],
            }
        else:
            student_info = None
        make_PDF_args.append(
            (
                spec["name"],
                spec["publicCode"],
                spec["numberOfPages"],
                spec["numberOfVersions"],
                paper_index,
                page_version,
                student_info,
            )
        )

    # Same as:
    # for x in make_PDF_args:
    #     make_PDF(*x)
    num_PDFs = len(make_PDF_args)
    with Pool() as pool:
        r = list(tqdm(pool.imap_unordered(_make_PDF, make_PDF_args), total=num_PDFs))


def confirm_processed(spec, msgr, classlist):
    """Checks that each PDF file was created and notify server.

    Arguments:
        spec (dict): exam specification, see :func:`plom.SpecVerifier`.
        msgr (Messenger): an open active connection to the server.
        classlist (list, None): ordered list of (sid, sname) pairs.

    Raises:
        RuntimeError: raised if any of the expected PDF files not found.
        ValueError: classlist is invalid in some way.
    """
    if spec["numberToName"] > 0:
        if not classlist:
            raise ValueError("You must provide a classlist for pre-named papers")
        if len(classlist) < spec["numberToName"]:
            raise ValueError(
                "Classlist is too short for {} pre-named papers".format(spec["numberToName"])
            )
    for paper_index in range(1, spec["numberToProduce"] + 1):
        if paper_index <= spec["numberToName"]:
            PDF_file_name = Path(paperdir) / "exam_{}_{}.pdf".format(
                str(paper_index).zfill(4), classlist[paper_index - 1][0]
            )
        else:
            PDF_file_name = Path(paperdir) / "exam_{}.pdf".format(
                str(paper_index).zfill(4)
            )

        # We will raise and error if the pdf file was not found
        if os.path.isfile(PDF_file_name):
            msgr.notify_pdf_of_paper_produced(paper_index)
        else:
            raise RuntimeError('Cannot find pdf for paper "{}"'.format(PDF_file_name))


def identify_prenamed(spec, msgr, classlist):
    """Identify papers that pre-printed names on the server.

    Arguments:
        spec (dict): exam specification, see :func:`plom.SpecVerifier`.
        msgr (Messenger): an open active connection to the server.
        classlist (list, None): ordered list of (sid, sname) pairs.

    Raises:
        RuntimeError: raised if any of the expected PDF files not found.
        ValueError: classlist is invalid in some way.
    """
    if spec["numberToName"] > 0:
        if not classlist:
            raise ValueError("You must provide a classlist to prename papers")
        if len(classlist) < spec["numberToName"]:
            raise ValueError(
                "Classlist is too short for {} pre-named papers".format(spec["numberToName"])
            )
    for paper_index in range(1, spec["numberToProduce"] + 1):
        if paper_index <= spec["numberToName"]:
            sid, sname = classlist[paper_index - 1]
            PDF_file_name = Path(paperdir) / "exam_{}_{}.pdf".format(
                str(paper_index).zfill(4), sid
            )
            if os.path.isfile(PDF_file_name):
                msgr.id_paper(paper_index, sid, sname)
            else:
                raise RuntimeError(
                    'Cannot find pdf for paper "{}"'.format(PDF_file_name)
                )
