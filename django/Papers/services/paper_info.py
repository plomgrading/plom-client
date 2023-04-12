# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2023 Andrew Rechnitzer

from django.db import transaction
from Papers.models import Paper, FixedPage, QuestionPage

import logging

log = logging.getLogger("PaperInfoService")


class PaperInfoService:
    @transaction.atomic
    def how_many_papers_in_database(self):
        """How many papers have been created in the database."""
        return Paper.objects.count()

    @transaction.atomic
    def is_paper_database_populated(self):
        """True if any papers have been created in the DB.

        The database is initially created with empty tables.  Users get added.
        This function still returns False.  Eventually Tests (i.e., "papers")
        get created.  Then this function returns True.
        """
        return Paper.objects.filter().exists()

    def is_this_paper_in_database(self, paper_number):
        """Check if the given paper is in the database."""
        return Paper.objects.filter(paper_number=paper_number).exists()

    @transaction.atomic
    def which_papers_in_database(self):
        """List which papers have been created in the database."""
        return list(Paper.objects.values_list("paper_number", flat=True))

    def page_has_image(self, paper_number, page_number):
        """
        Return True if a page has an Image associated with it.
        """
        paper = Paper.objects.get(paper_number=paper_number)
        page = FixedPage.objects.get(paper=paper, page_number=page_number)
        return page.image is not None

    @transaction.atomic
    def get_version_from_paper_page(self, paper_number, page_number):
        """Given a paper_number and page_number, return the version of that page."""
        try:
            paper = Paper.objects.get(paper_number=paper_number)
        except Paper.DoesNotExist:
            raise ValueError(f"Paper {paper_number} does not exist in the database.")
        try:
            page = FixedPage.objects.get(paper=paper, page_number=page_number)
        except FixedPage.DoesNotExist:
            raise ValueError(
                f"Page {page_number} of paper {paper_number} does not exist in the database."
            )
        return page.version

    @transaction.atomic
    def get_version_from_paper_question(self, paper_number, question_number):
        """Given a paper_number and question_number, return the version of that question."""
        try:
            paper = Paper.objects.get(paper_number=paper_number)
        except Paper.DoesNotExist:
            raise ValueError(f"Paper {paper_number} does not exist in the database.")
        try:
            # to find the version, find the first fixed question page of that paper with the question-number
            # and extract the version from that. Note - use "filter" and not "get" here.
            page = QuestionPage.objects.filter(
                paper=paper, question_number=question_number
            )[0]
            # This will either fail with a does-not-exist or index-out-of-range
        except (QuestionPage.DoesNotExist, IndexError):
            raise ValueError(
                f"Question {question_number} of paper {paper_number} does not exist in the database."
            )
        return page.version
