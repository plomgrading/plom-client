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
from testReassembler import reassemble

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
    return (int(t), sname, sid, arg)
    #makeCover(int(t), sname, sid, arg)


def reassembleTestCMD(shortName, outDir, t, sid):
    fnames = finishMessenger.RgetAnnotatedFiles(t)
    if len(fnames) == 0:
        return
    covername = "coverPages/cover_{}.pdf".format(str(t).zfill(4))
    rnames = ["../newServer/" + fn for fn in fnames]
    outname = os.path.join(outDir, "{}_{}.pdf".format(shortName, sid))
    return (outname, shortName, sid, covername, rnames)
    #reassemble(outname, shortName, sid, covername, rnames)


if __name__ == "__main__":
    # get commandline args if needed
    parser = argparse.ArgumentParser(
        description="Returns list of tests that have been completed. No arguments = run as normal."
    )
    parser.add_argument("-w", "--password", type=str)
    parser.add_argument(
        "-s", "--server", help="Which server to contact (must specify port as well)."
    )
    parser.add_argument(
        "-p", "--port", help="Which port to use (must specify server as well)."
    )
    args = parser.parse_args()

    # must spec both server+port or neither.
    if args.server and args.port:
        finishMessenger.startMessenger(altServer=args.server, altPort=args.port)
    elif args.server is None and args.port is None:
        finishMessenger.startMessenger()
    else:
        print("You must specify both the server and the port. Quitting.")
        quit()

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

    # get data for cover pages and reassembly
    pagelists = []
    coverpagelist = []
    if True:
        for t in completedTests:
            if (
                completedTests[t][0] == True
                and completedTests[t][2] == numberOfQuestions
            ):
                if identifiedTests[t][0] is not None:
                    dat1 = buildCoverPage(shortName, outDir, t, maxMarks)
                    dat2 = reassembleTestCMD(shortName, outDir, t, identifiedTests[t][0])
                    coverpagelist.append(dat1)
                    pagelists.append(dat2)
                else:
                    print(">>WARNING<< Test {} has no ID".format(t))

    def f(z):
        x, y = z
        if x and y:
            makeCover(*x)
            reassemble(*y)
    from multiprocessing import Pool
    pool = Pool()
    pool.map(f, zip(coverpagelist, pagelists))
    # Serial
    #for z in zip(coverpagelist, pagelists):
    #    f(z)
    finishMessenger.closeUser()
    finishMessenger.stopMessenger()

    print(">>> Warning <<<")
    print(
        "This still gets files by looking into server directory. In future this should be done over http."
    )
