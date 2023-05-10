# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Brennen Chiu
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Natalie Balashov

from django.db import models
from Scan.models import StagingBundle


class StagingImage(models.Model):
    """
    An image of a scanned page that isn't validated.

    Note that bundle_order is the 1-indexed position of the image with the pdf. This contrasts with pymupdf (for example) for which pages are 0-indexed.
    """

    ImageTypeChoices = models.TextChoices(
        "ImageType", "UNREAD KNOWN UNKNOWN EXTRA DISCARD ERROR"
    )
    UNREAD = ImageTypeChoices.UNREAD
    KNOWN = ImageTypeChoices.KNOWN
    UNKNOWN = ImageTypeChoices.UNKNOWN
    EXTRA = ImageTypeChoices.EXTRA
    DISCARD = ImageTypeChoices.DISCARD
    ERROR = ImageTypeChoices.ERROR

    def _staging_image_upload_path(self, filename):
        # save bundle as "//media/staging/bundles/username/bundle-timestamp/page_images/filename"
        return "staging/bundles/{}/{}/page_images/{}".format(
            self.bundle.user.username, self.bundle.timestamp, filename
        )

    bundle = models.ForeignKey(StagingBundle, on_delete=models.CASCADE)
    bundle_order = models.PositiveIntegerField(null=True)  # starts from 1 not zero.
    image_file = models.ImageField(upload_to=_staging_image_upload_path)
    image_hash = models.CharField(max_length=64)
    parsed_qr = models.JSONField(default=dict, null=True)
    rotation = models.IntegerField(default=0)
    pushed = models.BooleanField(default=False)
    image_type = models.TextField(choices=ImageTypeChoices.choices, default=UNREAD)


class KnownStagingImage(models.Model):
    staging_image = models.OneToOneField(
        StagingImage, primary_key=True, on_delete=models.CASCADE
    )
    paper_number = models.PositiveIntegerField(null=False)
    page_number = models.PositiveIntegerField(null=False)
    version = models.PositiveIntegerField(null=False)


class ExtraStagingImage(models.Model):
    # NOTE - we must have that paper_number and question_list are **both** null or both filled.

    staging_image = models.OneToOneField(
        StagingImage, primary_key=True, on_delete=models.CASCADE
    )
    paper_number = models.PositiveIntegerField(null=True, default=None)
    # https://docs.djangoproject.com/en/4.1/topics/db/queries/#storing-and-querying-for-none
    question_list = models.JSONField(default=None, null=True)
    # by default we store a null json field - this makes it easier to query
    # whether the extra page has data or not.


class UnknownStagingImage(models.Model):
    staging_image = models.OneToOneField(
        StagingImage, primary_key=True, on_delete=models.CASCADE
    )


class DiscardStagingImage(models.Model):
    staging_image = models.OneToOneField(
        StagingImage, primary_key=True, on_delete=models.CASCADE
    )
    discard_reason = models.TextField()


class ErrorStagingImage(models.Model):
    staging_image = models.OneToOneField(
        StagingImage, primary_key=True, on_delete=models.CASCADE
    )
    error_reason = models.TextField()
