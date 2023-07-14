# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Brennen Chiu
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Natalie Balashov

import pathlib
import uuid

from plom.tpv_utils import encodePaperPageVersion

from django.db import transaction
from django.core.files import File

from Scan.models import (
    StagingImage,
)

from Papers.models import (
    Bundle,
    Image,
    DiscardPage,
    CreateImageTask,
    FixedPage,
    MobilePage,
    QuestionPage,
    IDPage,
    Paper,
)
from .paper_info import PaperInfoService
from .validated_spec_service import SpecificationService


class ImageBundleService:
    """
    Class to encapsulate all functions around validated page images and bundles.
    """

    def create_bundle(self, name, hash):
        """
        Create a bundle and store its name and sha256 hash.
        """
        if Bundle.objects.filter(hash=hash).exists():
            raise RuntimeError("A bundle with that hash already exists.")
        bundle = Bundle(name=name, hash=hash)
        bundle.save()
        return bundle

    def get_bundle(self, hash):
        """
        Get a bundle from its hash.
        """
        return Bundle.objects.get(hash=hash)

    def get_or_create_bundle(self, name, hash):
        """
        Get a Bundle instance, or create if it doesn't exist
        """

        if not Bundle.objects.filter(hash=hash).exists():
            return self.create_bundle(name, hash)
        else:
            return self.get_bundle(hash)

    def image_exists(self, hash):
        """
        Return True if a page image with the input hash exists in the database.
        """
        return Image.objects.filter(hash=hash).exists()

    @transaction.atomic
    def get_image_pushing_status(self, staged_image):
        """
        Return the status of a staged image's associated CreateImageTask instance
        """
        try:
            task_obj = CreateImageTask.objects.get(staging_image=staged_image)
            return task_obj.status
        except CreateImageTask.DoesNotExist:
            return None

    @transaction.atomic
    def get_image_pushing_message(self, staged_image):
        """
        Return the error message of a staged image's CreateImageTask instance
        """
        try:
            task_obj = CreateImageTask.objects.get(staging_image=staged_image)
            return task_obj.message
        except CreateImageTask.DoesNotExist:
            return None

    @transaction.atomic
    def is_image_pushing_in_progress(self, completed_images):
        """
        Return True if at least one CreateImageTask for a bundle has the status 'queued'
        or 'running'.
        """
        for img in completed_images:
            status = self.get_image_pushing_status(img)
            if status == "queued" or status == "running":
                return True
        return False

    def upload_valid_bundle(self, staged_bundle, user_obj):
        """
        Assuming all of the pages in the bundle are valid (i.e. have a valid page number,
        paper number, and don't collide with any currently uploaded pages) upload all the pages
        using bulk ORM calls.

        1. Check that all the staging images have page numbers and test numbers
        2. Check that no staging images collide with each other
        3. Check that no staging images collide with any uploaded images
        4. Bulk-create images
        """

        bundle_images = StagingImage.objects.filter(
            bundle=staged_bundle
        ).prefetch_related(
            "knownstagingimage", "extrastagingimage", "discardstagingimage"
        )

        # Staging has checked this - but we check again here to be very sure
        if not self.all_staged_imgs_valid(bundle_images):
            raise RuntimeError("Some pages in this bundle do not have QR data.")

        # Staging has checked this - but we check again here to be very sure
        collide = self.find_internal_collisions(bundle_images)
        if len(collide) > 0:
            raise RuntimeError(f"Some pages in the staged bundle collide - {collide}")

        # Staging has not checked this - we need to do it here
        collide = self.find_external_collisions(bundle_images)
        if len(collide) > 0:
            raise RuntimeError(
                f"Some pages in the staged bundle collide with uploaded pages - {collide}"
            )

        uploaded_bundle = Bundle(
            name=staged_bundle.slug,
            hash=staged_bundle.pdf_hash,
            user=user_obj,
            staging_bundle=staged_bundle,
        )
        uploaded_bundle.save()

        pi_service = PaperInfoService()

        def image_save_name(staged):
            if staged.image_type == StagingImage.KNOWN:
                known = staged.knownstagingimage
                prefix = f"known_{known.paper_number}_{known.page_number}_"
            elif staged.image_type == StagingImage.EXTRA:
                extra = staged.extrastagingimage
                prefix = f"extra_{extra.paper_number}_"
                for q in extra.question_list:
                    prefix += f"{q}_"
            elif staged.image_type == StagingImage.DISCARD:
                prefix = "discard_"
            else:
                prefix = ""

            suffix = pathlib.Path(staged.image_file.name).suffix
            return prefix + str(uuid.uuid4()) + suffix

        for staged in bundle_images:
            with staged.image_file.open("rb") as fh:
                image = Image(
                    bundle=uploaded_bundle,
                    bundle_order=staged.bundle_order,
                    original_name=staged.image_file.name,
                    image_file=File(fh, name=image_save_name(staged)),
                    hash=staged.image_hash,
                    rotation=staged.rotation,
                    parsed_qr=staged.parsed_qr,
                )
                image.save()

            if staged.image_type == StagingImage.KNOWN:
                known = staged.knownstagingimage
                # Note that since fixedpage is polymorphic, this will handle question, ID and DNM pages.
                page = FixedPage.objects.get(
                    paper__paper_number=known.paper_number,
                    page_number=known.page_number,
                )
                page.image = image
                page.save(update_fields=["image"])
            elif staged.image_type == StagingImage.EXTRA:
                # need to make one mobile page for each question in the question-list
                extra = staged.extrastagingimage
                paper = Paper.objects.get(paper_number=extra.paper_number)
                for q in extra.question_list:
                    # get the version from the paper/question info
                    v = pi_service.get_version_from_paper_question(
                        extra.paper_number, q
                    )
                    MobilePage.objects.create(
                        paper=paper, image=image, question_number=q, version=v
                    )
            elif staged.image_type == StagingImage.DISCARD:
                disc = staged.discardstagingimage
                DiscardPage.objects.create(
                    image=image, discard_reason=disc.discard_reason
                )
            else:
                raise ValueError(
                    f"Pushed images must be known, extra or discards - found {staged.image_type}"
                )

        from Mark.services import MarkingTaskService
        from Identify.services import IdentifyTaskService

        mts = MarkingTaskService()
        its = IdentifyTaskService()
        questions = self.get_ready_questions(uploaded_bundle)
        for paper, question in questions["ready"]:
            paper_instance = Paper.objects.get(paper_number=paper)
            mts.create_task(paper_instance, question)

        for id_page in self.get_id_pages_in_bundle(uploaded_bundle):
            paper = id_page.paper
            if not its.id_task_exists(paper):
                its.create_task(paper)

    def get_staged_img_location(self, staged_image):
        """
        Get the image's paper number and page number from its QR code dict
        TODO: this same thing is implemented in ScanService. We need to choose which one stays!

        Args:
            staged_image: A StagingImage instance

        Returns:
            (int or None, int or None): paper number and page number
        """

        if not staged_image.parsed_qr:
            return (None, None)

        # The values are the same in all of the child QR dicts, so it's safe to choose any
        any_qr = list(staged_image.parsed_qr.values())[0]
        paper_number = any_qr["paper_id"]
        page_number = any_qr["page_num"]

        return paper_number, page_number

    @transaction.atomic
    def all_staged_imgs_valid(self, staged_imgs):
        """Check that all staged images in the bundle are ready to be
        uploaded. Each image must be "known" or "discard" or be
        "extra" with data. There can be no "unknown", "unread",
        "error" or "extra"-without-data.

        Args:
            staged_imgs: QuerySet, a list of all staged images for a bundle

        Returns:
            bool: True if all images are valid, false otherwise

        """
        # while this is done by staging, we redo it here to be **very** sure.
        if staged_imgs.filter(
            image_type__in=[
                StagingImage.UNREAD,
                StagingImage.UNKNOWN,
                StagingImage.ERROR,
            ]
        ).exists():
            return False
        if staged_imgs.filter(
            image_type=StagingImage.EXTRA, extrastagingimage__paper_number__isnull=True
        ).exists():
            return False
        # to do the complement of this search we'd need to count
        # knowns, discards and extra-with-data and make sure that
        # total matches number of pages in the bundle.
        return True

    @transaction.atomic
    def find_internal_collisions(self, staged_imgs):
        """Check for collisions *within* a bundle

        Args:
            staged_imgs: QuerySet, a list of all staged images for a bundle

        Returns:
            list [[StagingImage1.pk, StagingImage2.pk, StagingImage3.pk]]: list
                of unordered collisions so that in each sub-list each image (as
                determined by its primary key) collides with others in that sub-list.
        """

        known_imgs = {}  # dict of short-tpv to list of known-images with that tpv
        # if that list is 2 or more then that it is an internal collision.
        collisions = []

        # note - only known-images will create collisions.
        # extra pages and discards will never collide.
        for image in staged_imgs.filter(image_type=StagingImage.KNOWN):
            knw = image.knownstagingimage
            tpv = encodePaperPageVersion(knw.paper_number, knw.page_number, knw.version)
            # append this image.primary-key to the list of images with that tpv
            known_imgs.setdefault(tpv, []).append(image.pk)
        for tpv, image_list in known_imgs.items():
            if len(image_list) == 1:  # no collision at this tpv
                continue
            collisions.append(image_list)

        return collisions

    @transaction.atomic
    def find_external_collisions(self, staged_imgs):
        """
        Check for collisions between images in the input list and all the
        *currently uploaded* images.

        Args:
            staged_imgs: QuerySet, a list of all staged images for a bundle

        Returns:
            list [(StagingImage, Image)]: list of unordered collisions.
        """

        collisions = []
        # note that only known images can cause collisions
        for image in staged_imgs.filter(image_type=StagingImage.KNOWN):
            known = image.knownstagingimage
            colls = Image.objects.filter(
                fixedpage__paper__paper_number=known.paper_number,
                fixedpage__page_number=known.page_number,
            )
            for colliding_img in colls:
                collisions.append(
                    (image, colliding_img, known.paper_number, known.page_number)
                )
        return collisions

    @transaction.atomic
    def get_ready_questions(self, bundle):
        """Find questions across all test-papers in the database that
        now ready.  A question is ready when either it has all of its
        fixed-pages, or it has no fixed-pages but has some
        mobile-pages.

        Note: tasks are created on a per-question basis, so a test paper across multiple bundles
        could have some "ready" and "unready" questions.

        Args:
            bundle: a Bundle instance that has just been uploaded.

        Returns:
            dict {}: Two lists of (int, int). "ready" is the list of paper_number/question_number pairs
            that have pages in this bundle, and are now ready to be marked. "not_ready" are
            paper_number/question_number pairs that have pages in this bundle, but are not ready to be
            marked yet.

        """

        # find all question-pages (ie fixed pages) that attach to images in the current bundle.
        question_pages = QuestionPage.objects.filter(image__bundle=bundle)
        # find all mobile pages (extra pages) that attach to images in the current bundle
        extras = MobilePage.objects.filter(image__bundle=bundle)

        # now make list of all papers/questions updated by this bundle
        # note that values_list does not return a list, it returns a "query-set"
        papers_in_bundle = list(
            question_pages.values_list("paper__paper_number", "question_number")
        ) + list(extras.values_list("paper__paper_number", "question_number"))
        # remove duplicates by casting to a set
        papers_questions_updated_by_bundle = set(papers_in_bundle)

        # for each paper/question that has been updated, check if has either
        # all fixed pages, or no fixed pages but some mobile-pages.
        # if some, but not all, fixed pages then is not ready.

        result = {"ready": [], "not_ready": []}

        for paper_number, question_number in papers_questions_updated_by_bundle:
            q_pages = QuestionPage.objects.filter(
                paper__paper_number=paper_number, question_number=question_number
            )
            pages_no_img = q_pages.filter(image__isnull=True).count()
            if pages_no_img == 0:  # all fixed pages have images
                result["ready"].append((paper_number, question_number))
                continue
            # question has some images
            pages_with_img = q_pages.filter(image__isnull=False).count()
            if (
                pages_with_img > 0
            ):  # question has some pages with and some without images - not ready
                result["not_ready"].append((paper_number, question_number))
                continue
            # all fixed pages without images - check if has any mobile pages
            if (
                MobilePage.objects.filter(
                    paper__paper_number=paper_number, question_number=question_number
                ).count()
                > 0
            ):
                result["ready"].append((paper_number, question_number))

        return result

    @transaction.atomic
    def get_id_pages_in_bundle(self, bundle):
        """
        Get all of the ID pages in an uploaded bundle, in order to
        initialize ID tasks.

        Args:
            bundle: a Bundle instance

        Returns:
            QuerySet [IDPage]: a query of only the ID pages in the input bundle
        """

        return IDPage.objects.filter(image__bundle=bundle)
