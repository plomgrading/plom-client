# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2019-2020 Andrew Rechnitzer
# Copyright (C) 2019-2022 Colin B. Macdonald
# Copyright (C) 2020 Vala Vakilian
# Copyright (C) 2020 Dryden Wiebe
# Copyright (C) 2021 Peter Lee

import csv
from multiprocessing import Pool
from pathlib import Path

from tqdm import tqdm

from plom.create import paperdir as paperdir_name
from .mergeAndCodePages import make_PDF


def _make_PDF(x):
    """Call make_PDF from mergeAndCodePages with arguments expanded.

    *Note*: this is a little bit of glue to make the parallel Pool code
    elsewhere work.

    Arguments:
        x (tuple): this is expanded as the arguments to :func:`make_PDF`.
    """
    make_PDF(*x)


def outputProductionCSV(spec, make_PDF_args):
    """Output a csv with info on produced papers. Take the make_PDF_args that were used and dump them in a csv

    Arguments:
        spec (dict): exam specification, see :func:`plom.SpecVerifier`.
        make_PDF_args (list): a list of tuples of info for each paper
    """
    numberOfPages = spec["numberOfPages"]
    numberOfQuestions = spec["numberOfQuestions"]

    header = ["test_number", "sID", "sname"]
    for q in range(1, numberOfQuestions + 1):
        header.append("q{}.version".format(q))
    for p in range(1, numberOfPages + 1):
        header.append("p{}.version".format(p))
    with open("produced_papers.csv", "w") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)
        for paper in make_PDF_args:
            # we need only a few bits of the tuple
            idx, qver, pver, ptog, student_info = paper[4:9]
            # we don't actually need ptog = page to group mapping.
            if student_info:
                row = [idx, student_info["id"], student_info["name"]]
            else:  # just skip those columns
                row = [idx, None, None]
            for q in range(1, numberOfQuestions + 1):
                row.append(qver[q])
            for p in range(1, numberOfPages + 1):
                row.append(pver[p])
            csv_writer.writerow(row)


def build_page_group_dict(spec):
    # start with the id page
    page_to_group = {spec['idPage']: 'id'}
    # now any dnm
    for pg in spec['doNotMarkPages']:
        page_to_group[pg] = 'dnm'
    # now the questions
    for q in spec['question']:
        for pg in spec['question'][q]['pages']:
            page_to_group[pg] = f'q{q}'
    return page_to_group


def build_papers_backend(
    spec,
    global_question_version_map,
    global_page_version_map,
    classlist,
    *,
    fakepdf=False,
    no_qr=False,
    indexToMake=None,
    xcoord=None,
    ycoord=None,
):
    """Builds the papers using _make_PDF.

    Based on `numberToName` this uses `_make_PDF` to create some
    papers with names stamped on the front as well as some papers without.

    For the prenamed papers, names and IDs are taken in order from the
    classlist.

    Arguments:
        spec (dict): exam specification, see :func:`plom.SpecVerifier`.
        global_question_version_map (dict): dict of dicts mapping first by
            paper number (int) then by question number (int) to version (int).
        global_page_version_map (dict): dict of dicts mapping first by
            paper number (int) then by page number (int) to version (int).
        classlist (list, None): ordered list of (sid, sname) pairs.

    Keyword arguments:
        fakepdf (bool): when true, the build empty pdfs (actually empty files)
            for use when students upload homework or similar (and only 1 version).
        no_qr (bool): when True, don't stamp with QR codes.  Default: False
            (which means *do* stamp with QR codes).
        indexToMake (int/None): specified paper number to be built.  If
            None then build all papers.  If this parameter is specified,
            only this paper will be built and the others will be ignored.
        xcoord (float): percentage from left to right of page to place
            ID/Signature box.
        ycoord (float): percentage from top to bottom of page to place
            ID/Signature box.

    Raises:
        ValueError: classlist is invalid in some way.
    """

    if spec["numberToName"] > 0:
        if not classlist:
            raise ValueError("You must provide a classlist to prename papers")
        if len(classlist) < spec["numberToName"]:
            raise ValueError(
                "Classlist is too short for {} pre-named papers".format(
                    spec["numberToName"]
                )
            )
    # mapping from pages to groups for labelling top of pages
    page_to_group = build_page_group_dict(spec)
    make_PDF_args = []
    if indexToMake is None:
        papersToMake = range(1, spec["numberToProduce"] + 1)
    else:
        papersToMake = [indexToMake]
    for paper_index in papersToMake:
        question_version_map = global_question_version_map[paper_index]
        page_version_map = global_page_version_map[paper_index]
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
                question_version_map,
                page_version_map,
                page_to_group,
                student_info,
                no_qr,
                fakepdf,
                xcoord,
                ycoord,
            )
        )

    # Same as:
    # for x in make_PDF_args:
    #     make_PDF(*x)
    num_PDFs = len(make_PDF_args)
    with Pool() as pool:
        list(tqdm(pool.imap_unordered(_make_PDF, make_PDF_args), total=num_PDFs))
    # output CSV with all this info in it
    print("Writing produced_papers.csv.")
    outputProductionCSV(spec, make_PDF_args)


def check_pdf_and_id_if_needed(
    spec, msgr, classlist, *, paperdir=Path(paperdir_name), indexToCheck=None
):
    """Check pdf(s) are present on disk and id papers that are prenamed.

    Arguments:
        spec (dict): exam specification, see :func:`plom.SpecVerifier`.
        msgr (Messenger): an open active connection to the server.
        classlist (list, None): ordered list of (sid, sname) pairs.

    Keyword Arguments:
        paperdir (pathlib.Path): where to find the papers to print.
        indexToID (int,None): the index of single paper to ID or (if none), then ID all.

    Raises:
        RuntimeError: raised if any of the expected PDF files not found.
        ValueError: classlist is invalid in some way.
    """
    paperdir = Path(paperdir)
    if indexToCheck:
        range_to_check = [indexToCheck]
    else:  # check production of all papers
        range_to_check = range(1, spec["numberToProduce"] + 1)
    # now check that paper(s) are actually on disk
    for papernum in range_to_check:
        if papernum <= spec["numberToName"]:
            sid, sname = classlist[papernum - 1]
            pdf_file = paperdir / f"exam_{papernum:04}_{sid}.pdf"
            # if file is not there - error, else tell DB it is ID'd
            if not pdf_file.is_file():
                raise RuntimeError(f'Cannot find pdf for paper "{pdf_file}"')
            else:
                msgr.id_paper(papernum, sid, sname)
        else:
            pdf_file = paperdir / f"exam_{papernum:04}.pdf"
            # if file is not there - error.
            if not pdf_file.is_file():
                raise RuntimeError(f'Cannot find pdf for paper "{pdf_file}"')
