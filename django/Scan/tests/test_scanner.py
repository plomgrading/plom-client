# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2023 Natalie Balashov
# Copyright (C) 2023 Andrew Rechnitzer

import exif
import fitz
import shutil
import pathlib
import tempfile
from PIL import Image

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files import File
from model_bakery import baker

from plom.scan import QRextract, rotate
from Scan.services import ScanService, PageImageProcessor
from Scan.models import StagingBundle, StagingImage


class ScanServiceTests(TestCase):
    def setUp(self):
        self.user0 = baker.make(User, username="user0")
        self.pdf_path = settings.BASE_DIR / "Scan" / "tests" / "test_bundle.pdf"
        self.pdf = fitz.Document(self.pdf_path)  # has 28 pages
        media_folder = settings.MEDIA_ROOT
        media_folder.mkdir(exist_ok=True)
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT / "user0", ignore_errors=True)
        return super().tearDown()

    def test_upload_bundle(self):
        """
        Test ScanService.upload_bundle() and assert that the uploaded PDF file
        has been saved to the right place on disk.
        """

        scanner = ScanService()
        timestamp = timezone.now().timestamp()
        # open the pdf-file to create a file-object to pass to the upload command.
        with open(self.pdf_path, "rb") as fh:
            pdf_file_object = File(fh)

        scanner.upload_bundle(
            pdf_file_object, "test_bundle", self.user0, timestamp, "abcde", 28
        )

        the_bundle = StagingBundle.objects.get(user=self.user0, slug="test_bundle")
        bundle_path = the_bundle.pdf_file.path
        self.assertTrue(
            bundle_path,
            str(
                settings.BASE_DIR
                / "media"
                / "user0"
                / "bundles"
                / str(timestamp)
                / f"{timestamp}.pdf"
            ),
        )
        self.assertTrue(pathlib.Path(bundle_path).exists())

    def test_remove_bundle(self):
        """
        Test ScanService.remove_bundle() and assert that the uploaded PDF file
        has been removed from disk.
        """
        timestamp = timezone.now().timestamp()
        # make a pdf and save it to a tempfile
        with tempfile.NamedTemporaryFile() as ntf:
            self.pdf.save(ntf.name)

            # open that file to get django to save it to disk as per the models File("upload_to")
            with ntf:
                bundle = StagingBundle(
                    slug="test_bundle",
                    pdf_file=File(ntf, name=f"{timestamp}.pdf"),
                    user=self.user0,
                    timestamp=timestamp,
                    pdf_hash="abcde",
                    has_page_images=False,
                )
                bundle.save()
        # the pdf should now have been saved to the upload-to of the bundle-object
        bundle_path = pathlib.Path(bundle.pdf_file.path)
        self.assertTrue(bundle_path.exists())
        # now remove it using the scan services
        scanner = ScanService()
        scanner.remove_bundle(timestamp, self.user0)
        # that path should no longer exist, nor should the bundle
        self.assertFalse(bundle_path.exists())
        self.assertFalse(StagingBundle.objects.exists())

    def test_duplicate_hash(self):
        """
        Test ScanService.check_for_duplicate_hash()
        """
        baker.make(StagingBundle, pdf_hash="abcde")
        scanner = ScanService()
        duplicate_detected = scanner.check_for_duplicate_hash("abcde")
        self.assertTrue(duplicate_detected)

    def test_parse_qr_codes(self):
        """
        Test ScanService.parse_qr_code() and assert that the test QR codes
        have been successfully read and parsed into the correct format.
        """
        img_path = settings.BASE_DIR / "Scan" / "tests" / "page_img_good.png"
        codes = QRextract(img_path)
        scanner = ScanService()
        parsed_codes = scanner.parse_qr_code([codes])

        assert parsed_codes
        code_dict = {
            "NW": {
                "page_info": {
                    "paper_id": 6,
                    "page_num": 4,
                    "version_num": 1,
                    "public_code": "93849",
                },
                "quadrant": "2",
                "tpv": "00006004001",
                "x_coord": 166.5,
                "y_coord": 272,
            },
            "SW": {
                "page_info": {
                    "paper_id": 6,
                    "page_num": 4,
                    "version_num": 1,
                    "public_code": "93849",
                },
                "quadrant": "3",
                "tpv": "00006004001",
                "x_coord": 173.75,
                "y_coord": 2895.5,
            },
            "SE": {
                "page_info": {
                    "paper_id": 6,
                    "page_num": 4,
                    "version_num": 1,
                    "public_code": "93849",
                },
                "quadrant": "4",
                "tpv": "00006004001",
                "x_coord": 2141,
                "y_coord": 2883.5,
            },
        }
        for quadrant in code_dict:
            self.assertEqual(
                parsed_codes[quadrant]["page_info"]["paper_id"],
                code_dict[quadrant]["page_info"]["paper_id"],
            )
            self.assertEqual(
                parsed_codes[quadrant]["page_info"]["page_num"],
                code_dict[quadrant]["page_info"]["page_num"],
            )
            self.assertEqual(
                parsed_codes[quadrant]["page_info"]["version_num"],
                code_dict[quadrant]["page_info"]["version_num"],
            )
            self.assertEqual(
                parsed_codes[quadrant]["page_info"]["public_code"],
                code_dict[quadrant]["page_info"]["public_code"],
            )
            self.assertEqual(
                parsed_codes[quadrant]["tpv"],
                code_dict[quadrant]["tpv"],
            )
            self.assertTrue(
                (parsed_codes[quadrant]["x_coord"] - code_dict[quadrant]["x_coord"])
                / code_dict[quadrant]["x_coord"]
                < 0.01
            )
            self.assertTrue(
                (parsed_codes[quadrant]["y_coord"] - code_dict[quadrant]["y_coord"])
                / code_dict[quadrant]["y_coord"]
                < 0.01
            )

    def test_parse_qr_codes_png_rotated_180(self):
        """
        Test ScanService.parse_qr_code() and assert that the QR codes
        are read correctly after the page image is rotated.
        """
        scanner = ScanService()

        image_upright_path = settings.BASE_DIR / "Scan" / "tests" / "page_img_good.png"

        qrs_upright = QRextract(image_upright_path)
        codes_upright = scanner.parse_qr_code([qrs_upright])

        image_upright = Image.open(image_upright_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            image_flipped_path = pathlib.Path(tmpdir) / "flipped.png"
            image_flipped = image_upright.rotate(180)
            image_flipped.save(image_flipped_path)

            qrs_flipped = QRextract(image_flipped_path)
            codes_flipped = scanner.parse_qr_code([qrs_flipped])

            pipr = PageImageProcessor()
            has_had_rotation = pipr.rotate_page_image(image_flipped_path, codes_flipped)
            self.assertEquals(has_had_rotation, 180)

            # read QR codes a second time due to rotation of image
            qrs_flipped = QRextract(image_flipped_path)
            codes_flipped = scanner.parse_qr_code([qrs_flipped])

        xy_upright = []
        xy_flipped = []

        for q, p in zip(codes_upright, codes_flipped):
            xy_upright.append(
                [codes_upright[q]["x_coord"], codes_upright[q]["y_coord"]]
            )
            xy_flipped.append(
                [codes_flipped[p]["x_coord"], codes_flipped[p]["y_coord"]]
            )

        for original, rotated in zip(xy_upright, xy_flipped):
            self.assertTrue((original[0] - rotated[0]) / rotated[0] < 0.01)
            self.assertTrue((original[1] - rotated[1]) / rotated[1] < 0.01)

    def test_parse_qr_codes_jpeg_rotated_180_no_exif(self):
        """
        Test ScanService.parse_qr_code() and assert that the QR codes are read correctly
        after an upside down jpeg page image with no exif is rotated.
        """
        scanner = ScanService()

        image_original_path = settings.BASE_DIR / "Scan" / "tests" / "page_img_good.png"
        qrs_original = QRextract(image_original_path)
        codes_original = scanner.parse_qr_code([qrs_original])

        image_original = Image.open(image_original_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            image_flipped_path = pathlib.Path(tmpdir) / "flipped_no_exif.jpeg"
            image_flipped = image_original.rotate(180)
            image_flipped.save(image_flipped_path)
            with open(image_flipped_path, "rb") as f:
                im = exif.Image(f)
            assert not im.has_exif

            qrs_flipped = QRextract(image_flipped_path)
            codes_flipped = scanner.parse_qr_code([qrs_flipped])

            pipr = PageImageProcessor()
            has_had_rotation = pipr.rotate_page_image(image_flipped_path, codes_flipped)
            self.assertEquals(has_had_rotation, 180)

            with open(image_flipped_path, "rb") as f:
                im = exif.Image(f)
            self.assertEquals(im.get("orientation"), 3)

            # read QR codes a second time due to rotation of image
            qrs_flipped = QRextract(image_flipped_path)
            codes_flipped = scanner.parse_qr_code([qrs_flipped])

            xy_upright = []
            xy_flipped = []

            for q, p in zip(codes_original, codes_flipped):
                xy_upright.append(
                    [codes_original[q]["x_coord"], codes_original[q]["y_coord"]]
                )
                xy_flipped.append(
                    [codes_flipped[p]["x_coord"], codes_flipped[p]["y_coord"]]
                )

            for upright, rotated in zip(xy_upright, xy_flipped):
                self.assertTrue((upright[0] - rotated[0]) / rotated[0] < 0.01)
                self.assertTrue((upright[1] - rotated[1]) / rotated[1] < 0.01)

    def test_parse_qr_codes_jpeg_upright_exif_rot_180(self):
        """
        Test ScanService.parse_qr_code() and assert that the QR codes are read correctly
        after an upright page image with exif rotation of 180 is rotated.
        """
        scanner = ScanService()

        image_original_path = settings.BASE_DIR / "Scan" / "tests" / "page_img_good.png"
        qrs_original = QRextract(image_original_path)
        codes_original = scanner.parse_qr_code([qrs_original])

        image_original = Image.open(image_original_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            image_exif_180_path = pathlib.Path(tmpdir) / "upright_exif_180.jpeg"
            image_original.save(image_exif_180_path)
            rotate.rotate_bitmap_jpeg_exif(image_exif_180_path, 180)
            with open(image_exif_180_path, "rb") as f:
                im = exif.Image(f)
            self.assertEquals(im.get("orientation"), 3)

            qrs_exif_180 = QRextract(image_exif_180_path)
            codes_exif_180 = scanner.parse_qr_code([qrs_exif_180])

            pipr = PageImageProcessor()
            has_had_rotation = pipr.rotate_page_image(
                image_exif_180_path, codes_exif_180
            )
            self.assertEquals(has_had_rotation, 180)

            with open(image_exif_180_path, "rb") as f:
                im = exif.Image(f)
            self.assertEquals(im.get("orientation"), 1)

    def test_parse_qr_codes_jpeg_upside_down_exif_180(self):
        """
        Test ScanService.parse_qr_code() when image is upside down, but exif indicates 180 rotation
        """
        scanner = ScanService()

        image_original_path = settings.BASE_DIR / "Scan" / "tests" / "page_img_good.png"
        qrs_original = QRextract(image_original_path)
        codes_original = scanner.parse_qr_code([qrs_original])

        image_original = Image.open(image_original_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            image_flipped_path = pathlib.Path(tmpdir) / "flipped_exif_180.jpeg"
            image_flipped = image_original.rotate(180)
            image_flipped.save(image_flipped_path)
            rotate.rotate_bitmap_jpeg_exif(image_flipped_path, 180)
            with open(image_flipped_path, "rb") as f:
                im = exif.Image(f)
            self.assertEquals(im.get("orientation"), 3)

            qrs_flipped = QRextract(image_flipped_path)
            codes_flipped = scanner.parse_qr_code([qrs_flipped])

            pipr = PageImageProcessor()
            has_had_rotation = pipr.rotate_page_image(image_flipped_path, codes_flipped)
            self.assertEquals(has_had_rotation, 0)

            with open(image_flipped_path, "rb") as f:
                im = exif.Image(f)
            self.assertEquals(im.get("orientation"), 3)

            # read QR codes a second time due to rotation of image
            qrs_flipped = QRextract(image_flipped_path)
            codes_flipped = scanner.parse_qr_code([qrs_flipped])

            xy_upright = []
            xy_flipped = []

            for q, p in zip(codes_original, codes_flipped):
                xy_upright.append(
                    [codes_original[q]["x_coord"], codes_original[q]["y_coord"]]
                )
                xy_flipped.append(
                    [codes_flipped[p]["x_coord"], codes_flipped[p]["y_coord"]]
                )

            for original, rotated in zip(xy_upright, xy_flipped):
                self.assertTrue((original[0] - rotated[0]) / rotated[0] < 0.01)
                self.assertTrue((original[1] - rotated[1]) / rotated[1] < 0.01)

    def test_known_images(self):
        """
        Test ScanService.get_all_known_images()
        """
        scanner = ScanService()
        bundle = baker.make(
            StagingBundle, user=self.user0, timestamp=timezone.now().timestamp()
        )
        # there are no images in the bundle
        imgs = scanner.get_all_known_images(bundle)
        self.assertEqual(imgs, [])

        # now make an image with no qr-codes, so known is false
        baker.make(StagingImage, parsed_qr={}, bundle=bundle, image_type="unknown")
        imgs = scanner.get_all_known_images(bundle)
        self.assertEqual(imgs, [])
        # now make an image with a qr-code and known=true.
        with_data = baker.make(
            StagingImage, parsed_qr={"dummy": "dict"}, bundle=bundle, image_type="known"
        )
        imgs = scanner.get_all_known_images(bundle)
        self.assertEqual(imgs, [with_data])
