# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2022 Brennen Chiu
# Copyright (C) 2023 Natalie Balashov
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Julian Lapenna

import arrow
from django.db import transaction
from django.db.models import Exists, OuterRef, Prefetch

from Papers.models import (
    FixedPage,
    MobilePage,
    Paper,
    Image,
    Bundle,
)
from Scan.models import StagingBundle


class ManageScanService:
    """Functions for overseeing pushed papers."""

    def get_total_fixed_pages(self):
        """Return the total number of fixed pages."""
        return FixedPage.objects.all().count()

    def get_total_mobile_pages(self):
        """Return the total number of mobile pages.

        Note that an image used for multiple questions will be counted
        with multiplicity.
        """
        return MobilePage.objects.all().count()

    @transaction.atomic
    def get_number_of_scanned_pages(self):
        """Return the number of pages scanned and validated.

        Note that any mobile page used in multiple questions is
        counted with multiplicity.
        """
        scanned_fixed = FixedPage.objects.exclude(image=None)
        mobile = MobilePage.objects.all()
        return scanned_fixed.count() + mobile.count()

    def get_total_test_papers(self):
        """Return the total number of test-papers in the exam."""
        return Paper.objects.all().count()

    @transaction.atomic
    def get_number_completed_test_papers(self):
        """Return a dict of completed papers and their fixed/mobile pages.

        A paper is complete when it either has **all** its fixed
        pages, or it has no fixed pages but has some extra-pages.
        """
        # Get fixed pages with no image
        fixed_with_no_scan = FixedPage.objects.filter(paper=OuterRef("pk"), image=None)
        # Get papers without fixed-page-with-no-scan
        all_fixed_present = Paper.objects.filter(~Exists(fixed_with_no_scan))
        # now get papers with **no** fixed page scans
        fixed_with_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=False
        )
        # build a subquery to help us find papers which have some
        # mobile_pages the outer-ref in the subquery allows us to
        # match for papers that have mobile pages. This also allows us
        # to avoid duplications since "exists" stops the query as soon
        # as one item is found - see below
        mobile_pages = MobilePage.objects.filter(paper=OuterRef("pk"))
        no_fixed_but_some_mobile = Paper.objects.filter(
            ~Exists(fixed_with_scan), Exists(mobile_pages)
        )
        # We can also do the above query as:
        #
        # no_fixed_but_some_mobile = Paper.objects.filter(
        # ~Exists(fixed_with_scan), mobilepages_set__isnull=False
        # ).distinct()
        #
        # however this returns one result for **each** mobile-page, so
        # one needs to append the 'distinct'. This is a common problem
        # when querying backwards across foreign key fields

        return all_fixed_present.count() + no_fixed_but_some_mobile.count()

    @transaction.atomic
    def get_all_completed_test_papers(self):
        """Return dict of test-papers that have been completely scanned.

        A paper is complete when it either has **all** its fixed
        pages, or it has no fixed pages but has some extra-pages.
        """
        # Subquery of fixed pages with no image
        fixed_with_no_scan = FixedPage.objects.filter(paper=OuterRef("pk"), image=None)
        # Get all papers without fixed-page-with-no-scan
        all_fixed_present = Paper.objects.filter(
            ~Exists(fixed_with_no_scan)
        ).prefetch_related(
            Prefetch(
                "fixedpage_set", queryset=FixedPage.objects.order_by("page_number")
            ),
            Prefetch(
                "mobilepage_set",
                queryset=MobilePage.objects.order_by("question_number"),
            ),
            "fixedpage_set__image",
            "mobilepage_set__image",
        )
        # Notice all the prefetching here - this is to avoid N+1
        # problems.  Below we loop over these papers and their pages /
        # images we tell django to prefetch the fixed and mobile
        # pages, and the images in the fixed and mobile pages.  Since
        # there are many fixed/mobile pages for a given paper, these
        # are fixedpage_set and mobilepage_set. Now because we want to
        # loop over the fixed/mobile pages in specific orders we use
        # the Prefetch object to specify that order at the time of
        # prefetching.

        # now subquery papers with **no** fixed page scans
        fixed_with_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=False
        )
        # again - we use a subquery to get mobile pages to avoid
        # duplications when executing the main query (see the
        # get_number_completed_test_papers function above.
        mobile_pages = MobilePage.objects.filter(paper=OuterRef("pk"))
        no_fixed_but_some_mobile = Paper.objects.filter(
            ~Exists(fixed_with_scan), Exists(mobile_pages)
        ).prefetch_related(
            Prefetch(
                "mobilepage_set",
                queryset=MobilePage.objects.order_by("question_number"),
            ),
            "mobilepage_set__image",
        )
        # again since we loop over the mobile pages within the paper
        # in a specified order, and ref the image in those mobile-pages
        # we do all this prefetching.

        complete = {}
        for paper in all_fixed_present:
            complete[paper.paper_number] = []
            # notice we don't specify order or prefetch in the loops
            # below here because we did the hard work above
            for fp in paper.fixedpage_set.all():
                complete[paper.paper_number].append(
                    {
                        "type": "fixed",
                        "page_number": fp.page_number,
                        "img_pk": fp.image.pk,
                    }
                )
            for mp in paper.mobilepage_set.all():
                complete[paper.paper_number].append(
                    {
                        "type": "mobile",
                        "question_number": mp.question_number,
                        "img_pk": mp.image.pk,
                    }
                )
        for paper in no_fixed_but_some_mobile:
            complete[paper.paper_number] = []
            # again we don't specify order or prefetch here because of the work above
            for mp in paper.mobilepage_set.all():
                complete[paper.paper_number].append(
                    {
                        "type": "mobile",
                        "question_number": mp.question_number,
                        "img_pk": mp.image.pk,
                    }
                )
        return complete

    @transaction.atomic
    def get_all_incomplete_test_papers(self):
        """Return a dict of test-papers that are partially but not completely scanned.

        A paper is not completely scanned when it has *some* but not all its fixed pages.
        """
        # Get fixed pages with no image - ie not scanned.
        fixed_with_no_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=True
        )
        # Get fixed pages with image - ie scanned.
        fixed_with_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=False
        )

        # Get papers with some but not all scanned fixed pages
        some_but_not_all_fixed_present = Paper.objects.filter(
            Exists(fixed_with_no_scan), Exists(fixed_with_scan)
        ).prefetch_related(
            Prefetch(
                "fixedpage_set", queryset=FixedPage.objects.order_by("page_number")
            ),
            Prefetch(
                "mobilepage_set",
                queryset=MobilePage.objects.order_by("question_number"),
            ),
            "fixedpage_set__image",
            "mobilepage_set__image",
        )

        incomplete = {}
        for paper in some_but_not_all_fixed_present:
            incomplete[paper.paper_number] = []
            for fp in paper.fixedpage_set.all():
                if fp.image:
                    incomplete[paper.paper_number].append(
                        {
                            "type": "fixed",
                            "page_number": fp.page_number,
                            "img_pk": fp.image.pk,
                        }
                    )
                else:
                    incomplete[paper.paper_number].append(
                        {
                            "type": "missing",
                            "page_number": fp.page_number,
                        }
                    )
            for mp in paper.mobilepage_set.all():
                incomplete[paper.paper_number].append(
                    {
                        "type": "mobile",
                        "question_number": mp.question_number,
                        "img_pk": mp.image.pk,
                    }
                )

        return incomplete

    @transaction.atomic
    def get_number_incomplete_test_papers(self):
        """Return the number of test-papers that are partially but not completely scanned.

        A paper is not completely scanned when it has *some* but not all its fixed pages.
        """
        # Get fixed pages with no image - ie not scanned.
        fixed_with_no_scan = FixedPage.objects.filter(paper=OuterRef("pk"), image=None)
        # Get fixed pages with image - ie scanned.
        fixed_with_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=False
        )
        # Get papers with some but not all scanned fixed pages
        some_but_not_all_fixed_present = Paper.objects.filter(
            Exists(fixed_with_no_scan), Exists(fixed_with_scan)
        )

        return some_but_not_all_fixed_present.count()

    @transaction.atomic
    def get_number_unused_test_papers(self):
        """Return the number of test-papers that are usused.

        A paper is unused when it has no fixed page images nor any mobile pages.
        """
        # Get fixed pages with image - ie scanned.
        fixed_with_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=False
        )
        # Get papers with neither fixed-with-scan nor mobile-pages
        no_images_at_all = Paper.objects.filter(
            ~Exists(fixed_with_scan), mobilepage__isnull=True
        )

        return no_images_at_all.count()

    @transaction.atomic
    def get_all_unused_test_papers(self):
        """Return a list of paper-numbers of all unused test-papers. Is sorted into paper-number order.

        A paper is unused when it has no fixed page images nor any mobile pages.
        """
        # Get fixed pages with image - ie scanned.
        fixed_with_scan = FixedPage.objects.filter(
            paper=OuterRef("pk"), image__isnull=False
        )
        # Get papers with neither fixed-with-scan nor mobile-pages
        no_images_at_all = Paper.objects.filter(
            ~Exists(fixed_with_scan), mobilepage__isnull=True
        )
        return sorted([paper.paper_number for paper in no_images_at_all])

    @transaction.atomic
    def get_page_image(self, test_paper, index):
        """Return a page-image.

        Args:
            test_paper (int): paper ID
            index (int): page number
        """
        paper = Paper.objects.get(paper_number=test_paper)
        page = FixedPage.objects.get(paper=paper, page_number=index)
        return page.image

    def get_number_pushed_bundles(self):
        """Return the number of pushed bundles."""
        return Bundle.objects.all().count()

    def get_number_unpushed_bundles(self):
        """Return the number of uploaded, but not yet pushed, bundles."""
        return StagingBundle.objects.filter(pushed=False).count()

    @transaction.atomic
    def get_pushed_bundles_list(self):
        """Return a list of all pushed bundles."""
        bundle_list = []
        for bundle in Bundle.objects.all().prefetch_related("staging_bundle", "user"):
            bundle_list.append(
                {
                    "name": bundle.staging_bundle.slug,
                    "pages": Image.objects.filter(bundle=bundle).count(),
                    "when_pushed": arrow.get(bundle.time_of_last_update).humanize(),
                    "when_uploaded": arrow.get(
                        bundle.staging_bundle.time_of_last_update
                    ).humanize(),
                    "who_pushed": bundle.user.username,
                    "who_uploaded": bundle.staging_bundle.user.username,
                }
            )
        return bundle_list

    def get_pushed_image(self, img_pk):
        try:
            img = Image.objects.get(pk=img_pk)
            return img
        except Image.DoesNotExist:
            return None
