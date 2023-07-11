# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2023 Natalie Balashov

from datetime import timedelta

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from model_bakery import baker

from Papers.models import Paper

from Identify.services import IdentifyTaskService, IDService
from Identify.models import (
    PaperIDTask,
    PaperIDAction,
)


class IdentifyTaskTests(TestCase):
    """Tests for ``Identify.services.IdentifyTaskService`` functions
    and ``Identify.services.IDService`` functions. """

    def setUp(self):
        self.marker0 = baker.make(User, username="marker0")
        self.marker1 = baker.make(User, username="marker1")
        return super().setUp()

    def test_are_there_id_tasks(self):
        """Test ``IdentifyTaskService.are_there_id_tasks()``."""
        its = IdentifyTaskService()
        self.assertFalse(its.are_there_id_tasks())

        baker.make(PaperIDTask)
        self.assertTrue(its.are_there_id_tasks())

    def test_get_done_tasks(self):
        """Test ``IdentifyTaskService.get_done_tasks()``."""
        its = IdentifyTaskService()
        self.assertEqual(its.get_done_tasks(user=self.marker0), [])

        paper = baker.make(Paper, paper_number=1)
        task = baker.make(PaperIDTask, paper=paper, status=PaperIDTask.COMPLETE)
        baker.make(
            PaperIDAction,
            user=self.marker0,
            task=task,
            student_name="A",
            student_id="1",
        )

        result = its.get_done_tasks(user=self.marker0)
        self.assertEqual(result, [[1, "1", "A"]])

    def test_get_latest_id_task(self):
        """Test ``IdentifyTaskService.get_latest_id_results()``."""
        its = IdentifyTaskService()
        paper = baker.make(Paper, paper_number=1)
        task1 = baker.make(PaperIDTask, paper=paper)
        self.assertIsNone(its.get_latest_id_results(task=task1))

        start_time = timezone.now()
        first = baker.make(
            PaperIDAction,
            time=start_time,
            task=task1,
        )

        self.assertEqual(its.get_latest_id_results(task1), first)

        second = baker.make(
            PaperIDAction, time=start_time + timedelta(seconds=1), task=task1
        )

        self.assertEqual(its.get_latest_id_results(task1), second)

    def test_get_id_progress(self):
        """Test ``IdentifyTaskService.get_id_progress()``."""
        its = IdentifyTaskService()
        self.assertEqual(its.get_id_progress(), [0, 0])

        baker.make(PaperIDTask, status=PaperIDTask.COMPLETE)
        baker.make(PaperIDTask, status=PaperIDTask.TO_DO)
        baker.make(PaperIDTask, status=PaperIDTask.OUT)
        self.assertEqual(its.get_id_progress(), [1, 3])

    def test_get_next_task(self):
        """Test ``IdentifyTaskService.get_next_task()``."""
        its = IdentifyTaskService()
        self.assertIsNone(its.get_next_task())

        p1 = baker.make(Paper, paper_number=1)
        p2 = baker.make(Paper, paper_number=2)
        p3 = baker.make(Paper, paper_number=3)
        p4 = baker.make(Paper, paper_number=4)

        baker.make(PaperIDTask, status=PaperIDTask.OUT, paper=p1)
        t2 = baker.make(PaperIDTask, status=PaperIDTask.TO_DO, paper=p2)
        baker.make(PaperIDTask, status=PaperIDTask.OUT, paper=p3)
        baker.make(PaperIDTask, status=PaperIDTask.TO_DO, paper=p4)

        claimed = its.get_next_task()
        self.assertEqual(claimed, t2)

    def test_claim_task(self):
        """Test a simple case of ``IdentifyTaskService.claim_task()``."""
        its = IdentifyTaskService()
        with self.assertRaises(RuntimeError):
            its.claim_task(self.marker0, 1)

        p1 = baker.make(Paper, paper_number=1)
        task = baker.make(PaperIDTask, paper=p1)

        its.claim_task(self.marker0, 1)
        task.refresh_from_db()

        self.assertEqual(task.status, PaperIDTask.OUT)
        self.assertEqual(task.assigned_user, self.marker0)

    def test_out_claim_task(self):
        """Test that claiming a task throws an error if the task is currently out."""
        its = IdentifyTaskService()
        p1 = baker.make(Paper, paper_number=1)
        baker.make(PaperIDTask, paper=p1, status=PaperIDTask.OUT)

        with self.assertRaises(RuntimeError):
            its.claim_task(self.marker0, 1)

    def test_identify_paper(self):
        """Test a simple case for ``IdentifyTaskService.identify_paper()``."""
        its = IdentifyTaskService()
        with self.assertRaises(RuntimeError):
            its.identify_paper(self.marker1, 1, "1", "A")

        p1 = baker.make(Paper, paper_number=1)
        task = baker.make(
            PaperIDTask, paper=p1, status=PaperIDTask.OUT, assigned_user=self.marker0
        )

        its.identify_paper(self.marker0, 1, "1", "A")
        task.refresh_from_db()

        self.assertEqual(task.status, PaperIDTask.COMPLETE)
        self.assertEqual(
            task.assigned_user, self.marker0
        )  # Assumption: user keeps task after ID'ing

        action = PaperIDAction.objects.get(user=self.marker0, task=task)
        self.assertEqual(action.student_name, "A")
        self.assertEqual(action.student_id, "1")

    def test_set_id_task_todo_and_clear_specific_id(self):
        """Test ``IDService().set_id_task_todo_and_clear_specific_id()``."""
        ids = IDService()
        paper = baker.make(Paper)
        task = baker.make(PaperIDTask, paper=paper, status=PaperIDTask.COMPLETE)
        action = baker.make(PaperIDAction, task=task)

        with self.assertRaises(ObjectDoesNotExist):
            ids.set_id_task_todo_and_clear_specific_id(paper.pk)
            task.refresh_from_db()
            action.refresh_from_db()

        self.assertEqual(task.status, PaperIDTask.TO_DO)
        self.assertQuerysetEqual(PaperIDAction.objects.filter(task=task), [])

    def set_id_task_todo_and_clear_specific_id_cmd(self):
        """Test ``IDService().id_task_todo_and_clear_specific_id_cmd()``."""
        ids = IDService()
        paper = baker.make(Paper)
        task = baker.make(PaperIDTask, paper=paper, status=PaperIDTask.COMPLETE)
        action = baker.make(PaperIDAction, task=task)

        with self.assertRaises(ObjectDoesNotExist):
            ids.set_id_task_todo_and_clear_specific_id_cmd(paper.paper_number)
            task.refresh_from_db()
            action.refresh_from_db()

        self.assertEqual(task.status, PaperIDTask.TO_DO)
        self.assertQuerysetEqual(PaperIDAction.objects.filter(task=task), [])

    def test_set_all_id_task_todo_and_clear_all_id_cmd(self):
        """Test ``IDService().set_all_id_task_todo_and_clear_all_id_cmd()``."""
        ids = IDService()
        for paper_number in range(1, 11):
            paper = baker.make(Paper, paper_number=paper_number)
            task = baker.make(PaperIDTask, paper=paper, status=PaperIDTask.COMPLETE)
            action = baker.make(PaperIDAction, task=task)
        
        with self.assertRaises(ObjectDoesNotExist):
            ids.set_all_id_task_todo_and_clear_all_id_cmd()
            task.refresh_from_db()
            action.refresh_from_db()

        for id_task in PaperIDTask.objects.all():
            self.assertEqual(id_task.status, PaperIDTask.TO_DO)
        
        self.assertQuerysetEqual(PaperIDAction.objects.all(), [])
