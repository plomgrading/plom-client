# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022 Brennen Chiu
# Copyright (C) 2022-2023 Colin B. Macdonald

from django.urls import path, re_path

from API.views import (
    MgetDoneTasks,
    MgetNextTask,
    MarkingProgressCount,
    MclaimThisTask,
    MgetOneImage,
    MgetRubricsByQuestion,
    MgetRubricPanes,
    McreateRubric,
    MmodifyRubric,
    MlatexFragment,
)


class MarkURLPatterns:
    """
    URLs that handle marking and interacting with plom-client.

    All of these patterns are under the route "MK,"
    e.g. "progress" will become "MK/progress"
    """

    prefix = "MK/"

    @staticmethod
    def get_patterns():
        mark_patterns = []

        # Overall marking progress
        progress = [
            path(
                "progress",
                MarkingProgressCount.as_view(),
                name="api_marking_progress_count",
            ),
        ]
        mark_patterns += progress

        # Task management
        tasks = [
            path(
                "tasks/complete", MgetDoneTasks.as_view(), name="api_MK_get_done_tasks"
            ),
            path(
                "tasks/available", MgetNextTask.as_view(), name="api_MK_get_next_tasks"
            ),
            path("tasks/<code>", MclaimThisTask.as_view(), name="api_MK_claim_task"),
        ]
        mark_patterns += tasks

        # Getting page-images from the server
        images = [
            path(
                "images/<int:pk>/<hash>/",
                MgetOneImage.as_view(),
                name="api_MK_one_image",
            ),
        ]
        mark_patterns += images

        # Rubric management
        rubrics = [
            re_path(
                r"rubric/(?P<question>[0-9]{,5})$",
                MgetRubricsByQuestion.as_view(),
                name="api_MK_get_rubric",
            ),
            path(
                "user/<username>/<int:question>",
                MgetRubricPanes.as_view(),
                name="api_MK_get_rubric_panes",
            ),
            path("rubric", McreateRubric.as_view(), name="api_MK_create_rubric"),
            re_path(
                r"rubric/(?P<key>[0-9]{12})$",
                MmodifyRubric.as_view(),
                name="api_MK_modify_rubric",
            ),
        ]
        mark_patterns += rubrics

        # Get LaTeX fragments
        latex = [
            path(
                "latex",
                MlatexFragment.as_view(),
                name="api_MK_latex_fragment",
            ),
        ]
        mark_patterns += latex

        return mark_patterns

    patterns = get_patterns()
