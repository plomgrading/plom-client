# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020-2023 Colin B. Macdonald

import logging
from pathlib import Path
import subprocess

import exif
from PIL import Image


log = logging.getLogger("scan")


def rotate_bitmap(fname, angle, *, cw=None, ccw=None):
    """Rotate bitmap counterclockwise, possibly in metadata.

    args:
        filename (pathlib.Path/str): name of a file
        angle (int): CCW angle of rotation: 0, 90, 180, 270, or -90.

    keyword args:
        cw (bool): clockwise, currently not default.
        ccw (bool): counter-clockwise, currently the default..

    If its a jpeg, we have special handling, otherwise, we use PIL and resave
    the image.
    """
    if cw is None and ccw is None:
        ccw = True
    if cw and ccw:
        raise RuntimeError("Cannot specify both cw and ccw")
    assert angle in (0, 90, 180, 270, -90), f"Invalid rotation angle {angle}"
    fname = Path(fname)
    if cw:
        if angle == 90:
            angle = -90
        elif angle == -90 or angle == 270:
            angle = 90

    if fname.suffix.lower() in (".jpg", ".jpeg"):
        return rotate_bitmap_jpeg_exif(fname, angle)

    if angle == 0:
        return
    # Note PIL does CCW (Issue #2585)
    img = Image.open(fname)
    new_img = img.rotate(angle, expand=True)
    new_img.save(fname)


def rotate_bitmap_jpeg_exif(fname, angle):
    """Rotate jpeg using exif metadata rotations.

    args:
        filename (pathlib.Path): name of a file
        angle (int): CCW angle of rotation 0, 90, 180, 270, or -90.

    If the image already had a exif rotation tag it is ignored: the
    rotation is absolute, NOT relative to that existing transform.
    This is b/c the QR code reading bits earlier in the pipeline do not
    support exif tags: perhaps they should and we revisit this decision.
    """
    assert angle in (0, 90, 180, 270, -90), f"Invalid rotation angle {angle}"
    log.info(f"Rotation of {angle:3} on JPEG {fname}: doing metadata EXIF rotations")
    with open(fname, "rb") as f:
        im = exif.Image(f)
    if im.has_exif:
        log.info(f'{fname} has exif already, orientation: {im.get("orientation")}')
    # Notation is OrigTop_OrigLeft -> RIGHT_TOP (-90 degree rot CCW)
    table = {
        0: exif.Orientation.TOP_LEFT,
        90: exif.Orientation.LEFT_BOTTOM,
        180: exif.Orientation.BOTTOM_RIGHT,
        -90: exif.Orientation.RIGHT_TOP,
        270: exif.Orientation.RIGHT_TOP,
    }
    im.set("orientation", table[angle])
    with open(fname, "wb") as f:
        f.write(im.get_file())
