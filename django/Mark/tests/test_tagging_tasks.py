# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Colin B. Macdonald

import unittest

from django.test import TestCase
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.exceptions import ValidationError

from Mark.services import MarkingTaskService
from Mark.models import MarkingTask, MarkingTaskTag


class MarkingTaskServiceTaggingTests(TestCase):
    """Unit tests for tagging aspects of Mark.services.MarkingTaskService."""

    def test_tag_create_tag(self):
        s = MarkingTaskService()
        user = baker.make(User)
        tag = s.create_tag(user, "tag")
        assert tag.text == "tag"
        tag2 = s.create_tag(user, "tag2")
        assert tag2.text != tag.text
        # probably exactly 2 but I don't quite understand when things are reset
        assert len(s.get_all_tags()) >= 2

    def test_tag_create_invalid_tag(self):
        # note validity is mostly tested elsewhere
        s = MarkingTaskService()
        user = baker.make(User)
        with self.assertRaisesMessage(ValidationError, "disallowed char"):
            s.create_tag(user, "  spaces and symbols $&<b> ")

    def test_tag_task_invalid_tag(self):
        s = MarkingTaskService()
        user = baker.make(User)
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        with self.assertRaisesMessage(ValidationError, "disallowed char"):
            tag_text = "  spaces and symbols $&<b> "
            s.add_tag_text_from_task_code(tag_text, task.code, user)

    def test_tag_task(self):
        s = MarkingTaskService()
        user = baker.make(User)
        # tag = s.create_tag(user, "hello")
        tag = baker.make(MarkingTaskTag)
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        s.add_tag_text_from_task_code(tag.text, task.code, user)

    def test_tag_task_twice_same(self):
        s = MarkingTaskService()
        user = baker.make(User)
        tag = baker.make(MarkingTaskTag)
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        s.add_tag_text_from_task_code(tag.text, task.code, user)
        s.add_tag_text_from_task_code(tag.text, task.code, user)

    def test_tag_task_twice(self):
        s = MarkingTaskService()
        user = baker.make(User)
        tag1 = baker.make(MarkingTaskTag)
        tag2 = baker.make(MarkingTaskTag)
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        s.add_tag_text_from_task_code(tag1.text, task.code, user)
        s.add_tag_text_from_task_code(tag2.text, task.code, user)

    def test_tag_task_autocreate_none_existing_tag(self):
        s = MarkingTaskService()
        user = baker.make(User)
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        s.add_tag_text_from_task_code("a_new_tag", task.code, user)

    def test_tag_task_invalid_task_code(self):
        s = MarkingTaskService()
        user = baker.make(User)
        with self.assertRaisesMessage(ValueError, "not a valid task code"):
            s.add_tag_text_from_task_code("hello", "paper_0111_invalid", user)

    def test_tag_task_no_such_task_code(self):
        s = MarkingTaskService()
        user = baker.make(User)
        with self.assertRaisesRegexp(RuntimeError, "Task .* does not exist"):
            s.add_tag_text_from_task_code("hello", "q9999g9", user)


class MarkingTaskServiceRemovingTaggingTests(TestCase):
    """Unit tests for removing tags in Mark.services.MarkingTaskService."""

    def test_tag_remove_no_such_global_tag(self):
        s = MarkingTaskService()
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        with self.assertRaisesMessage(ValueError, "No such tag"):
            s.remove_tag_text_from_task_code("no_such_tag_411d1b1443e5", task.code)

    # Issue #2810
    @unittest.expectedFailure
    def test_tag_remove_no_such_local_tag(self):
        s = MarkingTaskService()
        user = baker.make(User)
        s.create_tag(user, "hello")
        task = baker.make(
            MarkingTask, question_number=1, paper__paper_number=2, code="q0002g1"
        )
        with self.assertRaisesMessage(ValueError, "does not have tag"):
            s.remove_tag_text_from_task_code("hello", task.code)

    def test_tag_remove_invalid_code(self):
        s = MarkingTaskService()
        user = baker.make(User)
        s.create_tag(user, "hello")

        with self.assertRaisesMessage(ValueError, "not a valid task code"):
            s.remove_tag_text_from_task_code("hello", "paper_0111_invalid")

    def test_tag_remove_no_such_task(self):
        s = MarkingTaskService()
        user = baker.make(User)
        s.create_tag(user, "hello")
        with self.assertRaisesRegexp(RuntimeError, "Task .*does not exist"):
            s.remove_tag_text_from_task_code("hello", "q9999g9")
