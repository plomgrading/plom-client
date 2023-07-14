# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Andrew Rechnitzer

from django.shortcuts import render
from django.http import Http404, FileResponse
from django.core.files.uploadedfile import SimpleUploadedFile

from Base.base_group_views import ManagerRequiredView

from Progress.services import ManageScanService
from Progress.views import BaseScanProgressPage


class ScanCompleteView(BaseScanProgressPage):
    """View the table of complete pushed papers."""

    def get(self, request):
        mss = ManageScanService()

        # this is a dict - key is paper_number, value = list of pages
        completed_papers_dict = mss.get_all_completed_test_papers()
        # turn into list of tuples (key, value) ordered by key
        completed_papers_list = [
            (pn, pgs) for pn, pgs in sorted(completed_papers_dict.items())
        ]

        context = self.build_context("complete")
        context.update(
            {
                "number_of_completed_papers": len(completed_papers_dict),
                "completed_papers_list": completed_papers_list,
            }
        )
        return render(request, "Progress/scan_complete.html", context)


class PushedImageView(BaseScanProgressPage):
    """Return a pushed image given by its pk."""

    def get(self, request, img_pk):
        img = ManageScanService().get_pushed_image(img_pk)
        return FileResponse(img.image_file)


class PushedImageWrapView(BaseScanProgressPage):
    """Return the simple html wrapper around the pushed image with correct rotation."""

    def get(self, request, img_pk):
        pushed_img = ManageScanService().get_pushed_image(img_pk)
        # pass negative of angle for css rotation since it uses positive=clockwise (sigh)
        context = {"image_pk": img_pk, "angle": -pushed_img.rotation}
        return render(request, "Progress/fragments/pushed_image_wrapper.html", context)
