# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates

from django.shortcuts import render
from django.http import Http404, FileResponse
from django.core.files.uploadedfile import SimpleUploadedFile

from Base.base_group_views import ManagerRequiredView

from Progress.services import ManageScanService
from Progress.views import BaseScanProgressPage


class ScanOverview(BaseScanProgressPage):
    """
    View the progress of scanning/validating page-images.
    """

    def get(self, request):
        mss = ManageScanService()

        total_papers = mss.get_total_test_papers()
        completed_papers = mss.get_number_completed_test_papers()
        incomplete_papers = mss.get_number_incomplete_test_papers()
        pushed_bundles = mss.get_number_pushed_bundles()
        unpushed_bundles = mss.get_number_unpushed_bundles()
        
        context = self.build_context("overview")
        context.update(
            {
                "total_papers": total_papers,
                "completed_papers": completed_papers,
                "incomplete_papers": incomplete_papers,
                "pushed_bundles": pushed_bundles,
                "unpushed_bundles": unpushed_bundles,
            }
        )
        return render(request, "Progress/scan_overview.html", context)


class ScanTestPaperProgress(ManagerRequiredView):
    """
    Get the current state of test-paper scanning, filtered by
    'complete', 'incomplete', or 'all'.
    """

    def get(self, request, filter_by):
        mss = ManageScanService()
        context = self.build_context()

        # TODO: test paper list needs updating
        # if filter_by == "all":
        #     test_papers = mss.get_test_paper_list()
        # elif filter_by == "complete":
        #     test_papers = mss.get_test_paper_list(exclude_incomplete=True)
        # elif filter_by == "incomplete":
        #     test_papers = mss.get_test_paper_list(exclude_complete=True)
        # else:
        #     raise Http404("Unrecognized filtering argument.")

        # context.update({"test_papers": test_papers})
        return render(request, "Progress/fragments/scan_overview_table.html", context)


class ScanGetPageImage(ManagerRequiredView):
    """
    Get a page-image from the database.
    """

    def get(self, request, test_paper, index):
        mss = ManageScanService()

        image = mss.get_page_image(test_paper, index)
        with open(str(image.file_name), "rb") as f:
            image_file = SimpleUploadedFile(
                f"{test_paper:04}_page{index}.png",
                f.read(),
                content_type="image/png",
            )
        return FileResponse(image_file)


class ScanTestPageModal(ManagerRequiredView):
    """
    Return a modal that displays a scanned test-paper page.
    """

    def get(self, request, test_paper, index):
        context = self.build_context()
        context.update(
            {
                "test_paper": test_paper,
                "index": index,
            }
        )

        return render(
            request, "Progress/fragments/scan_view_paper_page_modal.html", context
        )


class ScanBundles(BaseScanProgressPage):
    """
    View the bundles uploaded by scanner users.
    """

    def get(self, request):
        context = self.build_context("bundles")
        mss = ManageScanService()

        bundle_list = mss.get_pushed_bundles_list()

        context.update(
            {
                "number_of_pushed_bundles": len(bundle_list),
                "pushed_bundles": bundle_list
            }
        )
        return render(request, "Progress/scan_bundles.html", context)
