#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Andrew Rechnitzer"
__copyright__ = "Copyright (C) 2019 Andrew Rechnitzer and Colin Macdonald"
__credits__ = ["Andrew Rechnitzer", "Colin Macdonald"]
__license__ = "AGPL-3.0-or-later"
# SPDX-License-Identifier: AGPL-3.0-or-later

from glob import glob
import hashlib
import json
import os
import requests
from requests_toolbelt import MultipartEncoder
import ssl
import urllib3
import threading

# ----------------------
from plom_exceptions import *
from specParser import SpecParser

_userName = "kenneth"

# ----------------------


# If we use unverified ssl certificates we get lots of warnings,
# so put in this to hide them.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sslContext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
sslContext.check_hostname = False
# Server defaults
server = "0.0.0.0"
message_port = 41984
SRmutex = threading.Lock()


# ----------------------


def uploadKnownPage(code, test, page, version, sname, fname, md5sum):
    SRmutex.acquire()
    try:
        param = {
            "user": _userName,
            "fileName": sname,
            "test": test,
            "page": page,
            "version": version,
            "md5sum": md5sum,
        }
        dat = MultipartEncoder(
            fields={
                "param": json.dumps(param),
                "originalImage": (sname, open(fname, "rb"), "image/png"),  # image
            }
        )
        response = session.put(
            "https://{}:{}/admin/knownPages/{}".format(server, message_port, code),
            data=dat,
            headers={"Content-Type": dat.content_type},
            verify=False,
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 401:
            raise PlomSeriousException("You are not authenticated.")
        else:
            raise PlomSeriousException("Some other sort of error {}".format(e))
    finally:
        SRmutex.release()

    return True


# ----------------------


def buildDirectories(spec):
    """Build the directories that this script needs"""
    # the list of directories. Might need updating.
    lst = ["sentPages", "sentPages/problemImages"]
    for dir in lst:
        try:
            os.mkdir(dir)
        except FileExistsError:
            pass
    for p in range(1, spec["numberOfPages"] + 1):
        for v in range(1, spec["numberOfVersions"] + 1):
            dir = "sentPages/page_{}/version_{}".format(str(p).zfill(2), v)
            os.makedirs(dir, exist_ok=True)


def extractTPV(name):
    # TODO - replace this with something less cludgy.
    # should be tXXXXpYYvZ.blah
    assert name[0] == "t"
    k = 1
    ts = ""
    while name[k].isnumeric():
        ts += name[k]
        k += 1

    assert name[k] == "p"
    k += 1
    ps = ""
    while name[k].isnumeric():
        ps += name[k]
        k += 1

    assert name[k] == "v"
    k += 1
    vs = ""
    while name[k].isnumeric():
        vs += name[k]
        k += 1
    return (ts, ps, vs)


def sendFiles(fileList):
    for fname in fileList:
        shortName = os.path.split(fname)[1]
        ts, ps, vs = extractTPV(shortName)
        # print("**********************")
        print("Upload {},{},{} = {} to server".format(ts, ps, vs, shortName))
        print(
            "If successful then move {} to sentPages subdirectory else move to problemImages".format(
                shortName
            )
        )
        md5 = hashlib.md5(open(fname, "rb").read()).hexdigest()
        code = "t{}p{}v{}".format(ts.zfill(4), ps.zfill(2), vs)
        uploadKnownPage(code, int(ts), int(ps), int(vs), shortName, fname, md5)


if __name__ == "__main__":
    print(">> This is still a dummy script, but gives you the idea? <<")
    # Look for pages in decodedPages
    spec = SpecParser().spec
    buildDirectories(spec)
    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=50))

    for p in range(1, spec["numberOfPages"] + 1):
        sp = str(p).zfill(2)
        if not os.path.isdir("decodedPages/page_{}".format(sp)):
            continue
        for v in range(1, spec["numberOfVersions"] + 1):
            print("Looking for page {} version {}".format(sp, v))
            if not os.path.isdir("decodedPages/page_{}/version_{}".format(sp, v)):
                continue
            fileList = glob("decodedPages/page_{}/version_{}/t*.png".format(sp, v))
            sendFiles(fileList)
