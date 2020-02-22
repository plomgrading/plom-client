#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Andrew Rechnitzer"
__copyright__ = "Copyright (C) 2020 Andrew Rechnitzer and Colin Macdonald"
__credits__ = ["Andrew Rechnitzer", "Colin Macdonald"]
__license__ = "AGPL-3.0-or-later"
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import getpass
import os
import shlex
import subprocess


# ----------------------

from coverPageBuilder import makeCover
import finishMessenger
from plom_exceptions import *

numberOfTests = 0
numberOfQuestions = 0

# ----------------------


def buildCoverPage(shortName, outDir, t, maxMarks):
    # should be [ [sid, sname], [q,v,m], [q,v,m] etc]
    cpi = finishMessenger.RgetCoverPageInfo(t)
    sid = cpi[0][0]
    sname = cpi[0][1]
    # for each Q [q, v, mark, maxPossibleMark]
    arg = []
    for qvm in cpi[1:]:
        # append quads of [q,v,m,Max]
        arg.append([qvm[0], qvm[1], qvm[2], maxMarks[str(qvm[0])]])
    makeCover(int(t), sname, sid, arg)


def reassembleTestCMD(shortName, outDir, t, sid):
    fnames = finishMessenger.RgetAnnotatedFiles(t)
    if len(fnames) == 0:
        return
    covername = "coverPages/cover_{}.pdf".format(str(t).zfill(4))
    rnames = ["../newServer/" + fn for fn in fnames]

    return 'python3 testReassembler.py {} {} {} {} "{}"\n'.format(
        shortName, sid, outDir, covername, rnames
    )


if __name__ == "__main__":
    # get commandline args if needed
    parser = argparse.ArgumentParser(
        description="Returns list of tests that have been completed. No arguments = run as normal."
    )
    parser.add_argument("-w", "--password", type=str)
    parser.add_argument(
        "-s",
        "--server",
        metavar="SERVER[:PORT]",
        action="store",
        help="Which server to contact.",
    )
    args = parser.parse_args()
    if args.server and ":" in args.server:
        s, p = args.server.split(":")
        finishMessenger.startMessenger(s, port=p)
    else:
        finishMessenger.startMessenger(args.server)

    # get the password if not specified
    if args.password is None:
        try:
            pwd = getpass.getpass("Please enter the 'manager' password:")
        except Exception as error:
            print("ERROR", error)
    else:
        pwd = args.password

    # get started
    try:
        finishMessenger.requestAndSaveToken("manager", pwd)
    except PlomExistingLoginException:
        print(
            "You appear to be already logged in!\n\n"
            "  * Perhaps a previous session crashed?\n"
            "  * Do you have another finishing-script or manager-client running,\n"
            "    e.g., on another computer?\n\n"
            "In order to force-logout the existing authorisation run the 029_clearManagerLogin.py script."
        )
        exit(0)

    shortName = finishMessenger.getInfoShortName()
    spec = finishMessenger.getInfoGeneral()
    numberOfTests = spec["numberOfTests"]
    numberOfQuestions = spec["numberOfQuestions"]

    outDir = "reassembled"
    os.makedirs("coverPages", exist_ok=True)
    os.makedirs(outDir, exist_ok=True)

    completedTests = finishMessenger.RgetCompletions()
    # dict key = testnumber, then list id'd, tot'd, #q's marked
    identifiedTests = finishMessenger.RgetIdentified()
    # dict key = testNumber, then pairs [sid, sname]
    maxMarks = finishMessenger.MgetAllMax()

    # Build coverpages
    # Doing this in a loop approx 4 times faster than using GNU Parallel
    for t in completedTests:
        if (
            completedTests[t][0] == True
            and completedTests[t][2] == numberOfQuestions
        ):
            buildCoverPage(shortName, outDir, t, maxMarks)

    # now reassemble papers
    with open("./commandlist.txt", "w") as fh:
        for t in completedTests:
            if (
                completedTests[t][0] == True
                and completedTests[t][2] == numberOfQuestions
            ):
                if identifiedTests[t][0] is not None:
                    fh.write(
                        reassembleTestCMD(shortName, outDir, t, identifiedTests[t][0])
                    )
                else:
                    print(">>WARNING<< Test {} has no ID".format(t))

    # pipe the commandlist into gnu-parallel
    cmd = shlex.split("parallel --bar -a commandlist.txt")
    subprocess.run(cmd, check=True)
    os.unlink("commandlist.txt")

    finishMessenger.closeUser()
    finishMessenger.stopMessenger()

    print(">>> Warning <<<")
    print(
        "This still gets files by looking into server directory. In future this should be done over http."
    )
