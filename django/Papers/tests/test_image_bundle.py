# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Andrew Rechnitzer
# Copyright (C) 2023 Julian Lapenna

from django.test import TestCase
from django.conf import settings
from model_bakery import baker

from django.contrib.auth.models import User

from Papers.services import ImageBundleService
from Papers.models import (
    Bundle,
    Image,
    Paper,
    Specification,
    DNMPage,
    FixedPage,
    QuestionPage,
)
from Scan.models import StagingImage, StagingBundle, KnownStagingImage
from Preparation.models import StagingPQVMapping


class ImageBundleTests(TestCase):
    """
    Tests for Papers.services.ImageBundelService
    """

    def setUp(self):
        # make a spec and a paper
        self.spec = baker.make(
            Specification, spec_dict={"question": {"1": {"pages": [1]}}}
        )
        self.user = baker.make(User, username="testScanner")
        self.paper = baker.make(Paper, paper_number=1)
        self.page1 = baker.make(DNMPage, paper=self.paper, page_number=2)
        # make a staged bundle with one known image.
        self.staged_bundle = baker.make(StagingBundle, pdf_hash="abcde", user=self.user)
        self.staged_image = baker.make(
            StagingImage,
            bundle=self.staged_bundle,
            bundle_order=1,
            # image_file="page2.png",
            image_hash="abcdef",
            rotation=90,
            image_type=StagingImage.KNOWN,
            _create_files=True,  # argument to tell baker to actually make the file
        )

        # supply p,p,v to this since we will need to cast it to a short-tpv code
        # and we don't (yet) fix maximum size of p,p,v in our models
        self.staged_known = baker.make(
            KnownStagingImage,
            staging_image=self.staged_image,
            paper_number=17,
            page_number=2,
            version=3,
        )

        return super().setUp()

    def test_create_bundle(self):
        """
        Test ImageBundlseService.create_bundle()
        """

        n_bundles = Bundle.objects.all().count()
        self.assertEqual(n_bundles, 0)

        ibs = ImageBundleService()
        ibs.create_bundle("bundle1", "abcde")

        n_bundles = Bundle.objects.all().count()
        self.assertEqual(n_bundles, 1)

        with self.assertRaises(RuntimeError):
            ibs.create_bundle("bundle2", "abcde")

        n_bundles = Bundle.objects.all().count()
        self.assertEqual(n_bundles, 1)

    def test_all_staged_imgs_valid(self):
        """
        Test ImageBundleService.all_staged_imgs_valid().

        If the input collection of staging images is empty, return True.
        If there are one or more images that are not "known" return False.
        Otherwise, return True.
        """

        ibs = ImageBundleService()
        imgs = StagingImage.objects.all()
        self.assertTrue(ibs.all_staged_imgs_valid(imgs))

        # make some known_pages
        for paper_num in range(2):
            for page_num in range(5):
                X = baker.make(
                    StagingImage,
                    parsed_qr={"NW": "Not empty!"},
                    image_type=StagingImage.KNOWN,
                    bundle=self.staged_bundle,
                    _create_files=True,
                )
                baker.make(
                    KnownStagingImage,
                    staging_image=X,
                    paper_number=paper_num,
                    page_number=page_num,
                )
        imgs = StagingImage.objects.all()
        self.assertTrue(ibs.all_staged_imgs_valid(imgs))
        # add in an unread page
        baker.make(
            StagingImage,
            image_type=StagingImage.UNREAD,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        imgs = StagingImage.objects.all()
        self.assertFalse(ibs.all_staged_imgs_valid(imgs))

    def test_find_internal_collisions(self):
        """
        Test ImageBundleService.find_internal_collisions()
        """

        ibs = ImageBundleService()
        imgs = StagingImage.objects.all()
        res = ibs.find_internal_collisions(imgs)
        self.assertEqual(res, [])

        img1 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img1,
            paper_number=1,
            page_number=1,
            version=1,
        )
        imgs = StagingImage.objects.all()
        self.assertEqual(res, [])

        # Add one collision
        img2 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img2,
            paper_number=1,
            page_number=1,
            version=1,
        )
        imgs = StagingImage.objects.all()
        res = ibs.find_internal_collisions(imgs)
        self.assertEqual(res, [[img1.pk, img2.pk]])

        # Add more collisions
        img3 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img3,
            paper_number=1,
            page_number=1,
            version=1,
        )

        img4 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img4,
            paper_number=2,
            page_number=1,
            version=1,
        )

        img5 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img5,
            paper_number=2,
            page_number=1,
            version=1,
        )

        img6 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img6,
            paper_number=2,
            page_number=1,
            version=1,
        )

        imgs = StagingImage.objects.all()
        res = ibs.find_internal_collisions(imgs)
        set_res = set([frozenset(X) for X in res])
        # Make lists into sets in order to compare in an unordered-way.
        # need to use "frozenset" because python does not like sets of sets.
        self.assertEqual(
            set_res,
            set(
                [
                    frozenset([img1.pk, img2.pk, img3.pk]),
                    frozenset([img4.pk, img5.pk, img6.pk]),
                ]
            ),
        )

    def test_find_external_collisions(self):
        """
        Test ImageBundleService.find_external_collisions()
        """

        ibs = ImageBundleService()
        res = ibs.find_external_collisions(StagingImage.objects.all())
        self.assertEqual(res, [])

        img1 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(KnownStagingImage, staging_image=img1, paper_number=2, page_number=1)

        img2 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(KnownStagingImage, staging_image=img2, paper_number=2, page_number=2)

        img3 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(KnownStagingImage, staging_image=img3, paper_number=2, page_number=3)

        img4 = baker.make(Image)
        img5 = baker.make(Image)

        baker.make(Paper, paper_number=2)
        paper3 = baker.make(Paper, paper_number=3)
        baker.make(FixedPage, paper=paper3, page_number=1, image=img4)
        baker.make(FixedPage, paper=paper3, page_number=2, image=img5)

        res = ibs.find_external_collisions(StagingImage.objects.all())
        self.assertEqual(res, [])

        st_img6 = baker.make(
            StagingImage,
            image_type=StagingImage.KNOWN,
            bundle=self.staged_bundle,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage, staging_image=st_img6, paper_number=3, page_number=1
        )

        res = ibs.find_external_collisions(StagingImage.objects.all())

        self.assertEqual(res, [(st_img6, img4, 3, 1)])

    def test_perfect_bundle(self):
        """
        Test that upload_valid_bundle() works as intended with a valid
        staged bundle.
        """

        bundle = baker.make(StagingBundle, pdf_hash="abcdef", user=self.user)
        baker.make(StagingPQVMapping, paper_number=2, question=1, version=1)
        paper2 = baker.make(Paper, paper_number=2)
        paper3 = baker.make(Paper, paper_number=3)
        baker.make(QuestionPage, paper=paper2, page_number=1, question_number=1)
        baker.make(DNMPage, paper=paper3, page_number=2)

        img1 = baker.make(
            StagingImage,
            bundle=bundle,
            parsed_qr={"NW": "abcde"},
            image_hash="ghijk",
            image_type=StagingImage.KNOWN,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img1,
            paper_number=2,
            page_number=1,
            version=1,
        )
        img2 = baker.make(
            StagingImage,
            bundle=bundle,
            parsed_qr={"NW": "abcde"},
            image_type=StagingImage.KNOWN,
            _create_files=True,
        )
        baker.make(
            KnownStagingImage,
            staging_image=img2,
            paper_number=3,
            page_number=2,
            version=1,
        )

        ibs = ImageBundleService()
        ibs.upload_valid_bundle(bundle)

        self.assertEqual(Bundle.objects.all()[0].hash, bundle.pdf_hash)
        self.assertEqual(
            Image.objects.get(fixedpage__page_number=1, fixedpage__paper=paper2).hash,
            img1.image_hash,
        )
