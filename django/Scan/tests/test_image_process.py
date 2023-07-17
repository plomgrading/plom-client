# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2023 Natalie Balashov
# Copyright (C) 2023 Colin B. Macdonald

from django.test import TestCase
from django.conf import settings

import cv2 as cv
import numpy as np
import pathlib
import tempfile
from PIL import Image

from Scan.services import PageImageProcessor, ScanService
from plom.scan import QRextract


class PageImageProcessorTests(TestCase):
    """Test the functions in services.PageImageProcessor."""

    def setUp(self):
        self.upright_page_full = {
            "NE": {"quadrant": "1"},
            "NW": {"quadrant": "2"},
            "SE": {"quadrant": "4"},
            "SW": {"quadrant": "3"},
        }

        self.upright_page_flaky = {"NE": {"quadrant": "1"}}

        self.turned_left_page_full = {
            "NE": {"quadrant": "4"},
            "NW": {"quadrant": "1"},
            "SE": {"quadrant": "3"},
            "SW": {"quadrant": "2"},
        }

        self.turned_left_page_flaky = {
            "NW": {"quadrant": "1"},
            "SE": {"quadrant": "3"},
        }

        self.turned_right_page_full = {
            "NE": {"quadrant": "2"},
            "NW": {"quadrant": "3"},
            "SE": {"quadrant": "1"},
            "SW": {"quadrant": "4"},
        }

        self.turned_right_page_flaky = {
            "NE": {"quadrant": "2"},
            "NW": {"quadrant": "3"},
            "SW": {"quadrant": "4"},
        }

        self.upside_down_page_full = {
            "NE": {"quadrant": "3"},
            "NW": {"quadrant": "4"},
            "SE": {"quadrant": "2"},
            "SW": {"quadrant": "1"},
        }

        self.upside_down_page_flaky = {
            "SW": {"quadrant": "1"},
        }

        self.bogus_page = {
            "NE": {"quadrant": "4"},
            "NW": {"quadrant": "3"},
            "SE": {"quadrant": "2"},
            "SW": {"quadrant": "1"},
        }

        self.qr_dict = {
            "NW": {
                "x_coord": 181.0,
                "y_coord": 387.5,
            },
            "SW": {
                "x_coord": 325.75,
                "y_coord": 3006.75,
            },
            "SE": {
                "x_coord": 2289.5,
                "y_coord": 2892.5,
            },
        }

        return super().setUp()

    def test_check_corner(self):
        """Test PageImageProcessor.check_corner()."""
        pipr = PageImageProcessor()
        orientation = pipr.check_corner(
            val_from_qr="1",
            upright="1",
            turned_right="2",
            turned_left="4",
            upside_down="3",
        )
        self.assertEqual(orientation, "upright")

    def test_get_page_orientation(self):
        """Test PageImageProcessor.get_page_orientation()."""
        pipr = PageImageProcessor()

        upright = pipr.get_page_orientation(self.upright_page_full)
        upright_flaky = pipr.get_page_orientation(self.upright_page_flaky)
        self.assertEqual(upright, "upright")
        self.assertEqual(upright_flaky, "upright")

        turned_left = pipr.get_page_orientation(self.turned_left_page_full)
        turned_left_flaky = pipr.get_page_orientation(self.turned_left_page_flaky)
        self.assertEqual(turned_left, "turned_left")
        self.assertEqual(turned_left_flaky, "turned_left")

        turned_right = pipr.get_page_orientation(self.turned_right_page_full)
        turned_right_flaky = pipr.get_page_orientation(self.turned_right_page_flaky)
        self.assertEqual(turned_right, "turned_right")
        self.assertEqual(turned_right_flaky, "turned_right")

        upside_down = pipr.get_page_orientation(self.upside_down_page_full)
        upside_down_flaky = pipr.get_page_orientation(self.upside_down_page_flaky)
        self.assertEqual(upside_down, "upside_down")
        self.assertEqual(upside_down_flaky, "upside_down")

        with self.assertRaises(RuntimeError):
            pipr.get_page_orientation(self.bogus_page)

        with self.assertRaises(RuntimeError):
            pipr.get_page_orientation({})

    def test_affine_matrix_correct_5_deg_rot(self):
        """Test PageImageProcessor.create_affine_transformation_matrix() for an image with 5-degree rotation."""
        pipr = PageImageProcessor()
        img_path = settings.BASE_DIR / "Scan" / "tests" / "id_page_img.png"
        test_img = Image.open(img_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            img_rot_path = pathlib.Path(tmpdir) / "rot_5_deg_img.png"
            img_rot = test_img.rotate(5, expand=True)
            img_rot.save(img_rot_path)

            codes = QRextract(img_rot_path)
            scanner = ScanService()
            qr_dict_id = scanner.parse_qr_code([codes])
            affine_matrix = pipr.create_affine_transformation_matrix(qr_dict_id)
            expected_matrix = np.float64(
                [[0.996, -0.087, 10.855], [0.087, 0.996, -134.659]]
            )
            err = np.linalg.norm(affine_matrix - expected_matrix, "fro")
            relative_err = err / np.linalg.norm(expected_matrix, "fro")
            self.assertTrue(relative_err < 0.01)

    def test_affine_matrix_no_correction(self):
        """Test PageImageProcessor.create_affine_transformation_matrix() with an image that does not need correction."""
        pipr = PageImageProcessor()
        img_path = settings.BASE_DIR / "Scan" / "tests" / "id_page_img.png"
        # test_img = Image.open(img_path)

        codes = QRextract(img_path)
        scanner = ScanService()
        qr_dict_id = scanner.parse_qr_code([codes])
        affine_matrix = pipr.create_affine_transformation_matrix(qr_dict_id)
        expected_matrix = np.float64([[1, 0, 0], [0, 1, 0]])
        self.assertTrue(np.linalg.norm(affine_matrix - expected_matrix, "fro") < 0.001)

    def test_ID_box_corrected_and_extracted(self):
        """Test PageImageProcessor rectangle extractor on an image with 3-degree rotation.

        Verify that the extracted ID box is upright by checking the interior of the blank "Signature" box,
        which is a subsection of the image that should be white.
        """
        in_top = 0.28
        in_bottom = 0.58
        in_left = 0.09
        in_right = 0.91
        pipr = PageImageProcessor()
        img_path = settings.BASE_DIR / "Scan" / "tests" / "id_page_img.png"
        test_img = Image.open(img_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            img_rot_path = pathlib.Path(tmpdir) / "rotated_img.png"
            img_rot = test_img.rotate(3, expand=True)
            img_rot.save(img_rot_path)

            codes = QRextract(img_rot_path)
            scanner = ScanService()
            qr_dict_id = scanner.parse_qr_code([codes])

            output_img = pipr.extract_rect_region(
                img_rot_path, 0, qr_dict_id, in_top, in_bottom, in_left, in_right
            )
            output_opencv = cv.cvtColor(np.array(output_img), cv.COLOR_RGB2BGR)
            white_subimage = output_opencv[395:490, 300:1030]
            self.assertTrue((np.mean(white_subimage) - 255) < 0.001)
