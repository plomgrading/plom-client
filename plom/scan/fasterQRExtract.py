# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2019-2020 Andrew Rechnitzer
# Copyright (C) 2020-2021 Colin B. Macdonald

import json
import os
import sys
from statistics import mean

from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from PIL import Image


def findCorner(qr, dim):
    mx = mean([p.x for p in qr.polygon])
    my = mean([p.y for p in qr.polygon])
    width, height = dim

    NS = "?"
    EW = "?"
    if my < 0.4 * height:
        NS = "N"
    elif my > 0.6 * height:
        NS = "S"
    else:
        return "??"
    if mx < 0.4 * width:
        EW = "W"
    elif mx > 0.6 * width:
        EW = "E"
    else:
        return "??"
    return NS + EW


def QRextract(image_name, write_to_file=True, try_harder=True):
    """Decode QR codes in an image, return or save them in .qr file.

    args:
        image_name (str/pathlib.Path): an image file, either in local
            dir or specified e.g., using `pathlib.Path`.
        write_to_file (bool): by default, the results are written into
            a file named `img_name.qr` (i.e., the same as input name
            with `.qr` appended, so something like `foo.jpg.qr`).
        try_harder (bool): Try to find QRs on a smaller resolution.
            Defaults to True.  Sometimes this seems work around high
            failure rates in the synthetic images used in CI testing.
            Details blow.

    returns:
        dict: Keys "NW", "NE", "SW", "SE", which with a list of the
            strings extracted from QR codes, one string per code.

    Without the `try_harder` flag, we observe high failure rates when
    the vertical resolution is near 2000 pixels (our current default).
    This is Issue #967 [1].  Its is not prevelant in real-life images,
    but causes a roughly 5% to 10% failure rate in our CI runs.
    The workaround (on by default) uses Pillow's `.reduce()` to quickly
    downscale the image.  This does increase the run time (have not
    checked by how much: I assume between 25% and 50%) so if that is
    more of a concern that error rate, turn off this flag.

    TODO: this issue should be reported to the ZBar project.

    Here are the results of an experiment shows the failure rate without
    this fix:

    vertical dim | failure rate
    -------------|-------------
    1600         | 0%
    1900         | 0%
    1950         | 7%
    1998         | 2%
    1999         | 5%
    2000         | 29%
    2001         | 1%
    2002         | 23%
    2003         | 17%
    2004         | 8%
    2005         | 23%
    2010         | 3%
    2100         | 1%
    3000         | 0%

    [1] https://gitlab.com/plom/plom/-/issues/967
    """

    if write_to_file:
        qrname = "{}.qr".format(image_name)
        if os.path.exists(qrname) and os.path.getsize(qrname) != 0:
            return

    cornerQR = {"NW": [], "NE": [], "SW": [], "SE": []}

    img = Image.open(image_name)
    qrlist = decode(img, symbols=[ZBarSymbol.QRCODE])
    for qr in qrlist:
        cnr = findCorner(qr, img.size)
        if cnr in cornerQR.keys():
            cornerQR[cnr].append(qr.data.decode())

    if try_harder:
        # try again on smaller image: avoids random CI failures #967?
        img = img.reduce(2)
        qrlist = decode(img, symbols=[ZBarSymbol.QRCODE])
        for qr in qrlist:
            cnr = findCorner(qr, img.size)
            if cnr in cornerQR.keys():
                s = qr.data.decode()
                if s not in cornerQR[cnr]:
                    # TODO: log instead of printing
                    print(
                        'Found QR-code "{}" at {} on reduced image, not found at original size'.format(
                            s, cnr
                        )
                    )
                    cornerQR[cnr].append(s)

    if write_to_file:
        with open(qrname, "w") as fh:
            json.dump(cornerQR, fh)
    return cornerQR


if __name__ == "__main__":
    # Take the bitmap file name as argument.
    imgName = sys.argv[1]
    QRextract(imgName)
