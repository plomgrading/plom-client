# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Edith Coates

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Mark.models import MarkingTask


class AnnotationImage(models.Model):
    """A raster representation of an annotated question."""

    path = models.TextField(null=False, default="")
    hash = models.TextField(null=False, default="")


class Annotation(models.Model):
    """Represents a marker's annotation of a particular test paper's question.

    Attributes:
        edition: The edition of the annotation for the specified task.
        score: The score given to the student's work.
        image: The image of the annotated question.
        annotation_data: A Json blob of annotation data containing image path info,
            rubric info, svg annotation info.
        marking_time: The time spent by the TA marking the question in seconds.
        task: The marking task.
        user: The user who made the annotation.
        time_of_last_update: The time of the last update.
    """

    edition = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    image = models.OneToOneField(AnnotationImage, on_delete=models.CASCADE)
    annotation_data = models.JSONField(null=True)
    marking_time = models.PositiveIntegerField(null=True)
    task = models.ForeignKey(MarkingTask, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    time_of_last_update = models.DateTimeField(auto_now=True)
