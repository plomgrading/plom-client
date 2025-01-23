# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2025 Colin B. Macdonald

from __future__ import annotations

from typing import Any

from pytest import raises

from .question_labels import (
    check_for_shared_pages,
    get_question_label,
    verbose_question_label,
)


def test_verbose_question_label() -> None:
    s = {
        "question": {
            "1": {},
            "2": {"label": "Q2a"},
            "3": {"label": "Q2bc"},
        }
    }
    assert get_question_label(s, 1) == "Q1"
    assert get_question_label(s, 2) == "Q2a"
    assert get_question_label(s, 3) == "Q2bc"
    assert verbose_question_label(s, 1) == "Q1"
    assert verbose_question_label(s, 2) == "Q2a (question index 2)"
    assert verbose_question_label(s, 3) == "Q2bc (question index 3)"


def test_spec_question_label_printer_errors() -> None:
    N = 2
    s = {"numberOfQuestions": N}
    with raises(ValueError):
        get_question_label(s, N + 1)
    with raises(ValueError):
        get_question_label(s, -1)
    with raises(ValueError):
        get_question_label(s, 0)


def test_spec_question_string() -> None:
    s: dict[str, Any] = {"question": {"1": {}}}
    assert get_question_label(s, "1") == get_question_label(s, 1)
    with raises(ValueError):
        get_question_label(s, "c")


def test_check_shared_pages() -> None:
    partial_spec = {
        "numberOfQuestions": 7,
        "question": {
            "1": {"label": "Q1a", "pages": [3], "mark": 2},
            "2": {"label": "Q1bc", "pages": [3], "mark": 3},
            "3": {"label": "Q2", "pages": [4], "mark": 5},
            "4": {"label": "Q3a", "pages": [4, 5], "mark": 8},
            "5": {"label": "Q3b", "pages": [5, 6], "mark": 1},
            "6": {"label": "Q3c", "pages": [5, 6], "mark": 1},
            "7": {"label": "Q4", "pages": [7], "mark": 1},
        },
    }
    s = check_for_shared_pages(partial_spec, 7)
    assert not s
    assert s == ""
    s = check_for_shared_pages(partial_spec, 1)
    assert "shares page 3" in s
    assert "with Q1bc" in s
    s = check_for_shared_pages(partial_spec, 2)
    assert "shares page 3" in s
    assert "with Q1a" in s
    assert "which is indep" in s
    s = check_for_shared_pages(partial_spec, 4)
    assert "shares pages 4, 5" in s
    assert "with Q2, Q3b, Q3c" in s
    assert "which are indep" in s
