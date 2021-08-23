# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2021 Colin B. Macdonald
# Copyright (C) 2018-2020 Andrew Rechnitzer
# Copyright (C) 2020 Dryden Wiebe

from stdiomask import getpass
import os
from multiprocessing import Pool
import os
from pathlib import Path
import shutil
import tempfile

from tqdm import tqdm

from plom.messenger import FinishMessenger
from plom.plom_exceptions import PlomExistingLoginException
from plom.finish.locationSpecCheck import locationAndSpecCheck
from plom.finish.examReassembler import reassemble


def _parfcn(y):
    """Parallel function used below, must be defined in root of module. Reassemble a pdf from the cover and question images.

    Leave coverfname as None to omit it (e.g., when totalling).

    Args:
        y : arguments to testReassembler.reassemble
    """
    reassemble(*y)


def download_page_images(msgr, tmpdir, outdir, short_name, t, sid):
    """Reassembles a test with a filename that includes the directory and student id.

    Args:
        msgr (FinishMessenger): the messenger to the plom server.
        tmpdir (pathlib.Path): where to store the temporary files.
        outdir (pathlib.Path): where to put the reassembled test.
        short_name (str): the name of the test.
        t (int/str): test number.
        sid (str): student id.

    Returns:
        tuple (outname, short_name, sid, None, rnames): descriptions below.
            outname (str): the full name of the file.
            short_name (str): same as argument.
            sid (str): sane as argument.
            None: placeholder for the coverpage which is not used here
            id_pages: pages flagged as id_pages, empty
            question_pagess: we pass all pages here
            dnm_pages: pages flagged as do-not-mark, empty
    """
    fnames = msgr.RgetOriginalFiles(t)  # uses deprecated filesystem access
    outname = outdir / f"{short_name}_{sid}.pdf"
    return (outname, short_name, sid, None, [], fnames, [])


def main(server=None, pwd=None):
    if server and ":" in server:
        s, p = server.split(":")
        msgr = FinishMessenger(s, port=p)
    else:
        msgr = FinishMessenger(server)
    msgr.start()

    if not pwd:
        pwd = getpass("Please enter the 'manager' password: ")

    try:
        msgr.requestAndSaveToken("manager", pwd)
    except PlomExistingLoginException:
        print(
            "You appear to be already logged in!\n\n"
            "  * Perhaps a previous session crashed?\n"
            "  * Do you have another finishing-script or manager-client running,\n"
            "    e.g., on another computer?\n\n"
            "In order to force-logout the existing authorization run `plom-finish clear`."
        )
        exit(1)

    try:
        shortName = msgr.getInfoShortName()
        spec = msgr.get_spec()
        if not locationAndSpecCheck(spec):
            raise RuntimeError("Problems confirming location and specification.")

        outdir = Path("reassembled_ID_but_not_marked")
        outdir.mkdir(exist_ok=True)
        tmpdir = Path(tempfile.mkdtemp(prefix="tmp_images_", dir=os.getcwd()))
        print(f"Downloading to temp directory {tmpdir}")

        identifiedTests = msgr.RgetIdentified()
        pagelists = []
        for t in identifiedTests:
            if identifiedTests[t][0] is not None:
                dat = download_page_images(
                    msgr, tmpdir, outdir, shortName, t, identifiedTests[t][0]
                )
                pagelists.append(dat)
            else:
                print(">>WARNING<< Test {} has no ID".format(t))
    finally:
        msgr.closeUser()
        msgr.stop()

    N = len(pagelists)
    print("Reassembling {} papers...".format(N))
    with Pool() as p:
        r = list(tqdm(p.imap_unordered(_parfcn, pagelists), total=N))

    print(">>> Warning <<<")
    print(
        "This still gets files by looking into server directory. In future this should be done over http."
    )
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
