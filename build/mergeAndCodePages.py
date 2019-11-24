__author__ = "Andrew Rechnitzer"
__copyright__ = "Copyright (C) 2018-2019 Andrew Rechnitzer"
__license__ = "AGPLv3"

import sys
import shlex
import subprocess
import os
import fitz
import pyqrcode
import tempfile

# this allows us to import from ../resources
sys.path.append("..")
from resources.tpv_utils import encodeTPV


# Take command line parameters
# 1 = name
# 2 = code
# 3 = length (ie number of pages)
# 4 = number of versions
# 5 = the test test number
# 6 = list of the version number for each page
name = sys.argv[1]
code = sys.argv[2]
length = int(sys.argv[3])
versions = int(sys.argv[4])
test = int(sys.argv[5])
pageVersions = eval(sys.argv[6])

# Command line parameters to imagemagick's mogrify
# puts a frame around the image.
mogParams = ' -mattecolor black -frame 1x1 -background "#FFFFFF" ' "-flatten"

# Which pdfsource file from which to extract each page version
V = {}
for v in range(1, versions + 1):
    V[v] = fitz.open("sourceVersions/version{}.pdf".format(v))

# Create test pdf as "exam"
exam = fitz.open()
# Insert the relevant page-versions into this pdf.
for p in range(1, length + 1):
    # Pymupdf starts pagecounts from 0 rather than 1. So offset things.
    exam.insertPDF(V[pageVersions[str(p)]], from_page=p - 1, to_page=p - 1, start_at=-1)

# Start to decorate the pages with qr-codes etc
# Get page width and height
pW = exam[0].bound().width
pH = exam[0].bound().height
# create a box for the test number near top-centre
rTC = fitz.Rect(pW // 2 - 50, 20, pW // 2 + 50, 40)
# put marks at top left/right so students don't write near
# staple or near where client will stamp marks
# create two "do not write" rectangles accordingly
rDNW0 = fitz.Rect(15, 15, 90, 90)
rDNW1 = fitz.Rect(pW - 90, 15, pW - 15, 90)
# 70x70 page-corner boxes for the QR codes
rNW = fitz.Rect(15, 20, 85, 90)
rNE = fitz.Rect(pW - 85, 20, pW - 15, 90)
rSW = fitz.Rect(15, pH - 90, 85, pH - 20)
rSE = fitz.Rect(pW - 85, pH - 90, pW - 15, pH - 20)

# Build all relevant pngs in a temp directory
with tempfile.TemporaryDirectory() as tmpDir:
    # filenames for testname QR and dnw rectangles
    nameFile = os.path.join(tmpDir, "name.png")
    dnw0File = os.path.join(tmpDir, "dnw0.png")
    dnw1File = os.path.join(tmpDir, "dnw1.png")
    # make a little grey triangle with the test name
    # put this in corner where staple is
    cmd = shlex.split(
        'convert -pointsize 18 -antialias -size 232x116 xc:white -draw "stroke black fill grey '
        "path 'M 114,0  L 0,114  L 228,114 L 114,0 Z'\"  -gravity south "
        "-annotate +0+8 '{}' -rotate -45 -trim {}".format(name, dnw0File)
    )
    subprocess.call(cmd)

    # and one for the other corner (back of page) in other orientation
    cmd = shlex.split(
        'convert -pointsize 18 -size 232x116 xc:white -draw "stroke black fill grey '
        "path 'M 114,0  L 0,114  L 228,114 L 114,0 Z'\"  -gravity south "
        "-annotate +0+8 '{}' -rotate +45 -trim {}".format(name, dnw1File)
    )
    subprocess.call(cmd)

    # create QR codes and other stamps for each test/page/version
    qrFile = {}
    tpFile = {}
    for p in range(1, length + 1):
        # 4 qr codes for the corners (one will be omitted for the staple)
        qrFile[p] = {}
        for i in range(1, 5):
            tpv = encodeTPV(test, p, pageVersions[str(p)], i, code)
            qr = pyqrcode.create(tpv, error="H")
            # save it in the associated file
            qrFile[p][i] = os.path.join(tmpDir, "page{}_{}.png".format(p, i))
            qr.png(qrFile[p][i], scale=4)
            # put a border around it
            cmd = shlex.split("mogrify {} {}".format(mogParams, qrFile[p][i]))
            subprocess.call(cmd)

    # After creating all of the QRcodes etc we can put them onto
    # the actual pdf pages as pixmaps using pymupdf
    # read the DNW triangles in to pymupdf
    dnw0 = fitz.Pixmap(dnw0File)
    dnw1 = fitz.Pixmap(dnw1File)
    for p in range(length):
        # test/page stamp in top-centre of page
        # Rectangle size hacked by hand. TODO = do this more algorithmically
        rect = fitz.Rect(pW // 2 - 40, 20, pW // 2 + 40, 44)
        text = "{}.{}".format(str(test).zfill(4), str(p + 1).zfill(2))
        rc = exam[p].insertTextbox(
            rect,
            text,
            fontsize=18,
            color=[0, 0, 0],
            fontname="Helvetica",
            fontfile=None,
            align=1,
        )
        exam[p].drawRect(rect, color=[0, 0, 0])
        assert rc > 0

        # grab the tpv QRcodes for current page
        qr = {}
        for i in range(1, 5):
            qr[i] = fitz.Pixmap(qrFile[p + 1][i])
        if p % 2 == 0:
            # if even page then stamp DNW near staple
            exam[p].insertImage(rDNW0, pixmap=dnw0, overlay=True)
            exam[p].insertImage(rNE, pixmap=qr[1], overlay=True)
            exam[p].insertImage(rSE, pixmap=qr[4], overlay=True)
            exam[p].insertImage(rSW, pixmap=qr[3], overlay=True)
        else:
            # odd page - put DNW stamp near staple
            exam[p].insertImage(rDNW1, pixmap=dnw1, overlay=True)
            exam[p].insertImage(rNW, pixmap=qr[2], overlay=True)
            exam[p].insertImage(rSW, pixmap=qr[3], overlay=True)
            exam[p].insertImage(rSE, pixmap=qr[4], overlay=True)
    if "id" in pageVersions and "name" in pageVersions:
        # a file for the student-details
        txt = "{}\n{}".format(pageVersions["id"], pageVersions["name"])
        sidW = (
            max(
                fitz.getTextlength(
                    pageVersions["id"], fontsize=36, fontname="Helvetica"
                ),
                fitz.getTextlength(
                    pageVersions["name"], fontsize=36, fontname="Helvetica"
                ),
                fitz.getTextlength(
                    "Please sign here", fontsize=36, fontname="Helvetica"
                ),
            )
            * 1.3
            * 0.5
        )
        sidH = 36 * 1.3
        sidRect = fitz.Rect(
            pW // 2 - sidW, pH // 2 - sidH, pW // 2 + sidW, pH // 2 + sidH
        )
        sidRect2 = fitz.Rect(sidRect.x0, sidRect.y1, sidRect.x1, sidRect.y1 + sidH)
        sidRect3 = fitz.Rect(
            sidRect.x0 - 8, sidRect.y0 - 8, sidRect.x1 + 8, sidRect2.y1 + 8
        )
        exam[0].drawRect(sidRect3, color=[0, 0, 0], fill=[1, 1, 1], width=4)
        exam[0].drawRect(sidRect, color=[0, 0, 0], fill=[1, 1, 1], width=2)
        exam[0].drawRect(sidRect2, color=[0, 0, 0], fill=[1, 1, 1], width=2)
        rc = exam[0].insertTextbox(
            sidRect,
            txt,
            fontsize=36,
            color=[0, 0, 0],
            fontname="Helvetica",
            fontfile=None,
            align=1,
        )
        rc = exam[0].insertTextbox(
            sidRect2,
            "Please sign here",
            fontsize=36,
            color=[0.9, 0.9, 0.9],
            fontname="Helvetica",
            fontfile=None,
            align=1,
        )


# Finally save the resulting pdf.
# Add the deflate option to compress the embedded pngs
# see https://pymupdf.readthedocs.io/en/latest/document/#Document.save
# also do garbage collection to remove duplications within pdf
# and try to clean up as much as possible.
# `linear=True` causes https://gitlab.math.ubc.ca/andrewr/MLP/issues/284
exam.save(
    "examsToPrint/exam_{}.pdf".format(str(test).zfill(4)),
    garbage=4,
    deflate=True,
    clean=True,
)
