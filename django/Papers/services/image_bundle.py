# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Brennen Chiu

import shutil
import itertools

from django.db import transaction
from django.conf import settings
from django_huey import db_task

from Scan.models import (
    StagingImage,
)

from Papers.models import (
    Bundle,
    Image,
    CreateImageTask,
    CollidingImage,
    Paper,
    BasePage,
)
from .paper_creator import PaperCreatorService
from .paper_info import PaperInfoService


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

    def create_image(
        self, bundle, bundle_order, original_name, file_name, hash, rotation
    ):
        """
        Create an image.
        """

        if Image.objects.filter(hash=hash).exists():
            raise RuntimeError("An image with that hash already exists.")
        image = Image(
            bundle=bundle,
            bundle_order=bundle_order,
            original_name=original_name,
            file_name=file_name,
            hash=hash,
            rotation=rotation,
        )
        image.save()
        return image

    def push_staged_image(self, staged_image, test_paper, page_number):
        """
        Save a staged bundle image to the database, after it has been
        successfully validated.

        Args:
            staged_image: StagingImage instance
            test_paper: string, test-paper ID of the image
            page_number: int, page number in the test (not the bundle)
        """
        push_task = self._push_staged_image(staged_image, test_paper, page_number)
        push_obj = CreateImageTask(
            huey_id=push_task.id, staging_image=staged_image, status="queued"
        )
        push_obj.save()

    def create_colliding_image(
        self, staged_image, test_paper, page_number, make_dirs=True
    ):
        """
        Save a colliding image to the database.

        Args:
            staged_image: StagingImage instance
            test_paper: int, test-paper ID of the image
            page_number: int, page number in the test (not the bundle)
            make_dirs (optional): bool, set to False for testing
        """

        if Image.objects.filter(hash=hash).exists():
            raise RuntimeError("An image with that hash already exists.")

        root_folder = settings.MEDIA_ROOT / "page_images" / "colliding_pages"
        test_folder = root_folder / str(test_paper)
        image_path = test_folder / f"page{page_number}_{staged_image.image_hash}.png"

        staged_bundle = staged_image.bundle
        bundle = self.get_or_create_bundle(staged_bundle.slug, staged_bundle.pdf_hash)

        colliding_image = CollidingImage(
            bundle=bundle,
            bundle_order=staged_image.bundle_order,
            original_name=staged_image.file_name,
            file_name=str(image_path),
            hash=staged_image.image_hash,
            rotation=staged_image.rotation,
            paper_number=test_paper,
            page_number=page_number,
        )
        colliding_image.save()

        if make_dirs:
            root_folder.mkdir(exist_ok=True)
            test_folder.mkdir(exist_ok=True)
            shutil.copy(staged_image.file_path, image_path)

    # wrapper in the atomic
    @db_task(queue="tasks")
    def _push_staged_image(staged_image, test_paper, page_number, make_dirs=True):
        """
        Save a staged bundle image to the database, after it has been
        successfully validated.

        Args:
            staged_image: StagingImage instance
            test_paper: int, test-paper ID of the image
            page_number: int, page number in the test (not the bundle)
            make_dirs (optional): bool, set to False for testing (otherwise, creates directories in the file system.)
        """

        image_bundle = ImageBundleService()
        papers = PaperCreatorService()
        info = PaperInfoService()

        if not info.is_this_paper_in_database(test_paper):
            raise RuntimeError(f"Test paper {test_paper} is not in the database.")

        if image_bundle.image_exists(staged_image.image_hash):
            raise RuntimeError(f"Page image already exists in the database.")

        if info.page_has_image(test_paper, page_number):
            image_bundle.create_colliding_image(
                staged_image, test_paper, page_number, make_dirs=make_dirs
            )
            staged_image.colliding = True
            staged_image.save()
            raise RuntimeError(
                f"Collision page detected: test {test_paper} already has page {page_number}."
            )

        staged_bundle = staged_image.bundle
        bundle = image_bundle.get_or_create_bundle(
            staged_bundle.slug, staged_bundle.pdf_hash
        )

        file_path = image_bundle.get_page_image_path(
            test_paper, f"page{page_number}.png", make_dirs
        )

        image = image_bundle.create_image(
            bundle=bundle,
            bundle_order=staged_image.bundle_order,
            original_name=staged_image.file_name,
            file_name=file_path,
            hash=staged_image.image_hash,
            rotation=staged_image.rotation,
        )

        if make_dirs:
            shutil.copy(staged_image.file_path, file_path)
        staged_image.pushed = True
        staged_image.save()

        papers.update_page_image(test_paper, page_number, image)

    def get_page_image_path(self, test_paper, file_name, make_dirs=True):
        """
        Return a save path for a test-paper page image.
        Also, create the necessary folders in the media directory
        if they don't exist.
        """
        page_image_dir = settings.MEDIA_ROOT / "page_images"
        test_papers_dir = page_image_dir / "test_papers"
        paper_dir = test_papers_dir / str(test_paper)

        if make_dirs:
            page_image_dir.mkdir(exist_ok=True)
            test_papers_dir.mkdir(exist_ok=True)
            paper_dir.mkdir(exist_ok=True)

        return str(paper_dir / file_name)

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

    @db_task(queue="tasks")
    def _upload_valid_bundle(staged_bundle):
        """
        Assuming all of the pages in the bundle are valid (i.e. have a valid page number,
        paper number, and don't collide with any currently uploaded pages) upload all the pages
        using bulk ORM calls.

        1. Check that all the staging images have page numbers and test numbers
        2. Check that no staging images collide with each other
        3. Check that no staging images collide with any uploaded images
        4. Bulk-create images
        """

        ibs = ImageBundleService()
        bundle_images = StagingImage.objects.filter(bundle=staged_bundle)

        if not ibs.all_staged_imgs_valid(bundle_images):
            raise RuntimeError("Some pages in this bundle do not have QR data.")

        if len(ibs.find_internal_collisions(bundle_images)) > 0:
            raise RuntimeError("Some pages in the staged bundle collide.")

        if len(ibs.find_external_collisions(bundle_images)) > 0:
            raise RuntimeError(
                "Some pages in the staged bundle collide with uploaded pages."
            )

        uploaded_bundle = Bundle(name=staged_bundle.slug, hash=staged_bundle.pdf_hash)
        uploaded_bundle.save()

        for staged in bundle_images:
            image = Image(
                bundle=uploaded_bundle,
                bundle_order=staged.bundle_order,
                original_name=staged.file_name,
                file_name=staged.file_path,
                hash=staged.image_hash,
                rotation=staged.rotation,
            )
            image.save()

            page = BasePage.objects.get(
                paper__paper_number=staged.paper_id,
                page_number=staged.page_number,
            )
            page.image = image
            page.save(update_fields=["image"])

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
        any_qr = list(staging_image.parsed_qr.values())[0]
        paper_number = any_qr["paper_id"]
        page_number = any_qr["page_num"]

        return paper_number, page_number

    @transaction.atomic
    def all_staged_imgs_valid(self, staged_imgs):
        """
        Check that all staged images in the bundle are ready to be uploaded. Each image
        must have a parsed_qr dict, a page number, and a paper number.

        Args:
            staged_imgs: QuerySet, a list of all staged images for a bundle

        Returns:
            bool: True if all images are valid, false otherwise
        """

        return not staged_imgs.filter(
            parsed_qr=None, paper_id=None, page_number=None
        ).exists()

    @transaction.atomic
    def find_internal_collisions(self, staged_imgs):
        """
        Check for collisions *within* a bundle

        Args:
            staged_imgs: QuerySet, a list of all staged images for a bundle

        Returns:
            list [(StagingImage, StagingImage)]: list of unordered collisions.
        """

        collisions = []
        visited = []
        for image in staged_imgs:
            colls = staged_imgs.filter(
                paper_id=image.paper_id,
                page_number=image.page_number,
            )
            colls = list(filter(lambda i: i.pk != image.pk, colls))
            for colliding_img in colls:
                if colliding_img not in visited:
                    collisions.append((image, colliding_img))
            visited.append(image)
        return collisions

    @transaction.atomic
    def find_external_collisions(self, staged_imgs):
        """
        Check for collisions between images in the input list and all the
        *currently uploaded* images.

        Args:
            staged_imgs: QuerySet, a list of all staged images for a bundle

        Returns:
            list [(StagingImage, StagingImage)]: list of unordered collisions.
        """

        collisions = []
        for image in staged_imgs:
            colls = Image.objects.filter(
                basepage__paper__paper_number=image.paper_id,
                basepage__page_number=image.page_number,
            )
            for colliding_img in colls:
                collisions.append((image, colliding_img))
        return collisions
