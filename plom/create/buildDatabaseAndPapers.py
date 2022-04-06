# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020 Andrew Rechnitzer
# Copyright (C) 2021-2022 Colin B. Macdonald
# Copyright (C) 2021 Peter Lee

from pathlib import Path

from plom import check_version_map
from plom.misc_utils import working_directory
from plom.create.buildNamedPDF import build_papers_backend
from plom.create.buildNamedPDF import check_pdf_and_id_if_needed
from plom.create import paperdir as paperdir_name
from plom.create import with_manager_messenger


@with_manager_messenger
def build_papers(
    *,
    basedir=Path("."),
    fakepdf=False,
    no_qr=False,
    indexToMake=None,
    xcoord=None,
    ycoord=None,
    msgr=None,
):
    """Build the blank papers using version information from server and source PDFs.

    Keyword Args:
        msgr (plom.Messenger/tuple): either a connected Messenger or a
            tuple appropriate for credientials.
        basedir (pathlib.Path/str): Look for the source version PDF files
            in `basedir/sourceVersions`.  Produce the printable PDF files
            in `basedir/papersToPrint`.
        fakepdf (bool): when true, the build empty pdfs (actually empty files)
            for use when students upload homework or similar (and only 1 version).
        no_qr (bool): when True, don't stamp with QR codes.  Default: False
            (which means *do* stamp with QR codes).
        indexToMake (int/None): prepare a particular paper, or None to make
            all papers.
        xcoord (float/None): tweak the x-coordinate of the stamped name/id
            box for prenamed papers.  None for a default value.
        ycoord (float/None): tweak the y-coordinate of the stamped name/id
            box for prenamed papers.  None for a default value.

    Raises:
        PlomConflict: server does not yet have a version map database, say
            b/c build_database has not yet been called.
    """
    basedir = Path(basedir)
    paperdir = basedir / paperdir_name
    paperdir.mkdir(exist_ok=True)
    classlist = None

    # TODO: temporarily avoid changing indent
    if True:
        spec = msgr.get_spec()
        # pvmap = msgr.getGlobalPageVersionMap()
        qvmap = msgr.getGlobalQuestionVersionMap()
        if spec["numberToName"] > 0:
            classlist = msgr.IDrequestClasslist()
            # TODO: Issue #1646 mostly student number (w fallback)
            if len(classlist) < spec["numberToName"]:
                raise ValueError(
                    "Classlist is too short for {} pre-named papers".format(
                        spec["numberToName"]
                    )
                )
    if indexToMake:
        # TODO: Issue #1745?
        if (indexToMake < 1) or (indexToMake > spec["numberToProduce"]):
            raise ValueError(
                f"Index out of range. Must be in range [1,{ spec['numberToProduce']}]"
            )

    if not classlist:
        classlist_by_papernum = {}
    elif classlist[0].get("papernum", None):
        # use the existing papernum column
        # note ignoring negative papernum: used to indicate blank
        # first some sanity checks
        papernums = [r["papernum"] for r in classlist if int(r["papernum"]) > 0]
        if len(set(papernums)) != len(papernums):
            raise ValueError('repeated "papernum": must be unique')
        del papernums
        # TODO: why are the papernum str not int?
        classlist_by_papernum = {
            int(r["papernum"]): {k: v for k, v in r.items() if k != "papernum"}
            for r in classlist
            if int(r["papernum"]) > 0
        }
    else:
        # no existing papernum column so map by the order in the classlist
        classlist_by_papernum = {(i + 1): x for i, x in enumerate(classlist)}

    del classlist

    # filter if we're not making all them
    if spec["numberToName"] > 0:
        # TODO: not totally precise how we want this to work with user-specified map
        classlist_by_papernum = {
            i: row
            for i, row in classlist_by_papernum.items()
            if i <= spec["numberToName"]
        }
    if any(i > spec["numberToProduce"] for i in classlist_by_papernum.keys()):
        raise ValueError(
            "Not enough papers to prename everything in the filtered classlist"
        )

    if indexToMake and indexToMake in classlist_by_papernum:
        print(f"Building only specific paper {indexToMake} (prenamed) in {paperdir}...")
    elif indexToMake:
        print(f"Building only specific paper {indexToMake} (blank) in {paperdir}...")
    elif classlist_by_papernum:
        print(
            f"Building {len(classlist_by_papernum)} prenamed papers and "
            f'{spec["numberToProduce"] - len(classlist_by_papernum)} blank '
            f"papers in {paperdir}..."
        )
    else:
        print(f'Building {spec["numberToProduce"]} blank papers in {paperdir}...')

    with working_directory(basedir):
        build_papers_backend(
            spec,
            qvmap,
            classlist_by_papernum=classlist_by_papernum,
            fakepdf=fakepdf,
            no_qr=no_qr,
            indexToMake=indexToMake,
            xcoord=xcoord,
            ycoord=ycoord,
        )

    print("Checking papers produced and ID-ing any pre-named papers into the database")
    check_pdf_and_id_if_needed(
        spec,
        msgr,
        classlist_by_papernum=classlist_by_papernum,
        paperdir=paperdir,
        indexToCheck=indexToMake,
    )


@with_manager_messenger
def build_database(*, msgr, vermap={}, verbose=True):
    """Build the database from a pre-set version map.

    Keyword Args:
        msgr (plom.Messenger/tuple): either a connected Messenger or a
            tuple appropriate for credientials.
        vermap (dict): question version map.  If empty dict, server will
            make its own mapping.  For the map format see
            :func:`plom.finish.make_random_version_map`.
        verbose (bool): default True, print status of each DB row
            creation to stdout.

    return:
        None

    raises:
        PlomExistingDatabase
        PlomServerNotReady
    """
    check_version_map(vermap)

    new_vmap = msgr.InitialiseDB(vermap)
    # sanity check the version maps
    if vermap:
        assert new_vmap == vermap, RuntimeError(
            "Report a bug in version_map code - difference between one you gave me and one server gave back at build!"
        )
    # now build the tests one at a time
    for t in sorted(new_vmap):
        status_msg = msgr.appendTestToDB(t, new_vmap[t])
        if verbose:
            print(status_msg)

    # more version map sanity checks
    qvmap = msgr.getGlobalQuestionVersionMap()
    assert qvmap == new_vmap, RuntimeError(
        "Report a bug in version_map code - difference between one you gave me and one server gave back after build!"
    )
