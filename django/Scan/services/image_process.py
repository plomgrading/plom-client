# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Natalie Balashov

import numpy as np
import cv2 as cv
from PIL import Image
from warnings import warn


class PageImageProcessor:
    """Functions for processing a page-image: rotation.

    (TODO: gamma correction, etc?)
    """

    # values used for QR code centre locations and page dimensions
    # obtained by running QRextract on un-rotated demo page images
    TOP = 139.5
    BOTTOM = 1861.5
    RIGHT = 1419.5
    LEFT = 126.5
    PWIDTH = 1546
    PHEIGHT = 2000

    # dimensions of the QR-bounded region
    WIDTH = RIGHT - LEFT
    HEIGHT = BOTTOM - TOP

    def get_page_orientation(self, qr_code_data):
        """Return a string representing a page orientation.

        The choices are:
            upright: page doesn't need to be rotated
            upside_down: page should be rotated 180 degrees
            turned_left: page should be rotated -90 degrees
            turned_right: page should be rotated 90 degrees

        The "expected" quadrants are the "quadrant" values in qr_code_data,
        and are labelled 1-4. The "actual" quadrants are the keys in qr_code_data,
        and are labelled NW, NE, SW, SE:

        upright:
            2---1   NW---NE
            |   |    |   |
            |   |    |   |
            3---4   SW---SE

        turned_right:
            3------2    NW---NE
            |      |     |   |
            4------1     |   |
                        SW---SE

        turned_left:
            1------4    NW---NE
            |      |     |   |
            2------3     |   |
                        SW---SE

        upside_down:
            4---3    NW---NE
            |   |     |   |
            |   |     |   |
            1---2    SW---SE

        Args:
            qr_code_data: (dict) data parsed from page-image QR codes

        Returns:
            str: short description of the orientation.

        Raises:
            RuntimeError: something inconsistent in the QR data.
        """
        northeast_orientation = None
        if "NE" in qr_code_data:
            expected_corner = qr_code_data["NE"]["quadrant"]
            northeast_orientation = self.check_corner(
                val_from_qr=expected_corner,
                upright="1",
                turned_right="2",
                turned_left="4",
                upside_down="3",
            )

        northwest_orientation = None
        if "NW" in qr_code_data:
            expected_corner = qr_code_data["NW"]["quadrant"]
            northwest_orientation = self.check_corner(
                val_from_qr=expected_corner,
                upright="2",
                turned_right="3",
                turned_left="1",
                upside_down="4",
            )

        southeast_orientation = None
        if "SE" in qr_code_data:
            expected_corner = qr_code_data["SE"]["quadrant"]
            southeast_orientation = self.check_corner(
                val_from_qr=expected_corner,
                upright="4",
                turned_right="1",
                turned_left="3",
                upside_down="2",
            )

        southwest_orientation = None
        if "SW" in qr_code_data:
            expected_corner = qr_code_data["SW"]["quadrant"]
            southwest_orientation = self.check_corner(
                val_from_qr=expected_corner,
                upright="3",
                turned_right="4",
                turned_left="2",
                upside_down="1",
            )

        # make sure at least one corner is truthy, and they all agree
        truthy_results = [
            corner
            for corner in [
                northeast_orientation,
                northwest_orientation,
                southwest_orientation,
                southeast_orientation,
            ]
            if corner
        ]

        result_vals = set(truthy_results)
        if len(result_vals) != 1:
            raise RuntimeError("Unable to determine page orientation.")

        return truthy_results[0]

    def check_corner(
        self, val_from_qr, upright, turned_right, turned_left, upside_down
    ):
        """Check a page corner for its actual orientation.

        Args:
            val_from_qr (str): one of "1", "2", "3", "4"
            upright (str): the quadrant value for an upright orientation,
                           one of "1", "2", "3", "4"
            turned_right (str): value for a turned_right orientation
            turned_left (str): value for a turned_left orientation
            upside_down (str): value for an upside_down orientation
        """
        if val_from_qr == upright:
            return "upright"
        elif val_from_qr == turned_right:
            return "turned_right"
        elif val_from_qr == turned_left:
            return "turned_left"
        elif val_from_qr == upside_down:
            return "upside_down"

    def get_rotation_angle_from_QRs(self, qr_data):
        """Get the current orientation of a page-image using its parsed QR code data.

        If it isn't upright, return the angle by which the image needs to be rotated,
        in degrees counter-clockwise.

        Args:
            qr_data (dict): parsed QR code data

        Returns:
            int: rotation angle by which the page needs to be rotated.
            If page is already upright, rotation angle of 0 is returned.
            Currently also returns zero if the orientation cannot be
            determined: this might not be what you want (TODO).
            See also also ``get_page_orientation``, although these two
            methods should perhaps converge in the future (TODO).
        """
        try:
            orientation = self.get_page_orientation(qr_data)
        except RuntimeError:
            # We cannot get the page orientation, so just return 0.
            return 0

        if orientation == "upright":
            return 0

        if orientation == "turned_right":
            rotate_angle = 90
        elif orientation == "turned_left":
            rotate_angle = -90
        else:
            rotate_angle = 180

        return rotate_angle

    def create_affine_transformation_matrix(self, qr_dict):
        """Given QR data for an image, determine the affine transformation needed to correct the image's orientation.

        Args:
            qr_dict (dict): the QR information for the image

        Returns:
            numpy.ndarray: the affine transformation matrix for correcting the image
        """
        if "NW" in qr_dict:
            dest_three_points = np.float32(
                [
                    [self.LEFT, self.TOP],
                    [self.LEFT, self.BOTTOM],
                    [self.RIGHT, self.BOTTOM],
                ]
            )
            src_three_points = np.float32(
                [
                    [qr_dict["NW"]["x_coord"], qr_dict["NW"]["y_coord"]],
                    [qr_dict["SW"]["x_coord"], qr_dict["SW"]["y_coord"]],
                    [qr_dict["SE"]["x_coord"], qr_dict["SE"]["y_coord"]],
                ]
            )
        elif "NE" in qr_dict:
            dest_three_points = np.float32(
                [
                    [self.RIGHT, self.TOP],
                    [self.LEFT, self.BOTTOM],
                    [self.RIGHT, self.BOTTOM],
                ]
            )
            src_three_points = np.float32(
                [
                    [qr_dict["NE"]["x_coord"], qr_dict["NE"]["y_coord"]],
                    [qr_dict["SW"]["x_coord"], qr_dict["SW"]["y_coord"]],
                    [qr_dict["SE"]["x_coord"], qr_dict["SE"]["y_coord"]],
                ]
            )
        else:
            return np.float64([[1, 0, 0], [0, 1, 0]])
        return cv.getAffineTransform(src_three_points, dest_three_points)

    def extract_rect_region(
        self, image_path, orientation, qr_dict, top, bottom, left, right
    ):
        """Given an image, get a particular sub-rectangle, after applying an affine transformation to correct it.

        Args:
            image_path (str/pathlib.Path): path to image file
            orientation (): a pre-rotation to be applied before calculating
                the affine transform.
            qr_dict (dict): parsed QR code data, used to calculate the
                transformation.
            top (float): fractional value in roughly in ``[0, 1]``
                which define the top boundary of the desired subsection of
                the image.
            left (float): same as top, defining the left boundary
            bottom (float): same as top, defining the bottom boundary
            right (float): same as top, defining the right boundary

        Returns:
            PIL.Image: the requested subsection of the original image, or
            the full, righted image if an invalid box range is specified.
        """
        pil_img = rotate.pil_load_with_jpeg_exif_rot_applied(image_path)
        pil_img.rotate(orientation)

        # convert the PIL.Image to OpenCV format
        opencv_img = cv.cvtColor(np.array(pil_img), cv.COLOR_RGB2BGR)

        affine_matrix = self.create_affine_transformation_matrix(qr_dict)
        righted_img = cv.warpAffine(
            opencv_img,
            affine_matrix,
            (self.PWIDTH, self.PHEIGHT),
            flags=cv.INTER_LINEAR,
        )

        top = round(self.TOP + top * self.HEIGHT)
        bottom = round(self.TOP + bottom * self.HEIGHT)
        left = round(self.LEFT + left * self.WIDTH)
        right = round(self.LEFT + right * self.WIDTH)

        if top < 0:
            warn(f"Top input of {top} is outside of image pixel range, capping at 0.")
        top = max(top, 0)
        if left < 0:
            warn(f"Left input of {left} is outside of image pixel range, capping at 0.")
        left = max(left, 0)
        if right > pil_img.width:
            warn(
                f"Right input of {right} is outside of image pixel range,"
                f" capping at {pil_img.width}."
            )
        right = min(right, pil_img.width)
        if bottom > pil_img.height:
            warn(
                f"Bottom input of {bottom} is outside of image pixel range,"
                f" capping at {pil_img.height}."
            )
        bottom = min(bottom, pil_img.height)

        cropped_img = righted_img[top:bottom, left:right]

        # convert the result to a PIL.Image
        result = Image.fromarray(cv.cvtColor(cropped_img, cv.COLOR_BGR2RGB))
        return result
