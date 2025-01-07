# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2025 Colin B. Macdonald

"""Utilities for dealing with question labels, question indices, etc.."""

from __future__ import annotations

from typing import Any


def get_question_label(spec: dict[str, Any], n: int | str) -> str:
    """Print question label for the nth question from spec dict.

    Args:
        spec: a dict with the assessment specification.
        n: which question, current indexed from 1.  For historical
            reasons it can be a str.

    Returns:
        The custom label of a question or "Qn" if one is not set.

    Raises:
        ValueError: `n` is out of range.

    TODO: change spec question keys to int.
    """
    n = int(n)
    try:
        N = spec["numberOfQuestions"]
    except KeyError:
        N = None
    if N:
        if n < 1 or n > N:
            raise ValueError(f"question={n} out of range [1, {N}]")
    else:
        if n < 1:
            raise ValueError(f"question={n} out of range [1, ...]")
    label = spec["question"][str(n)].get("label", None)
    if label:
        return label
    return "Q{}".format(n)


def verbose_question_label(spec: dict[str, Any], qidx: int) -> str:
    """Get the question label with a possible parenthetical for the index."""
    qlabel = get_question_label(spec, qidx)
    if qlabel == f"Q{qidx}":
        return qlabel
    return f"{qlabel} (question index {qidx})"


def check_for_shared_pages(spec: dict[str, Any], question_idx: int) -> str:
    """Check if our question shares pages, and return user-facing info message."""
    verbose_qlabel = verbose_question_label(spec, question_idx)
    my_pages = spec["question"][str(question_idx)]["pages"]
    shared_pages = []
    shared_with = []
    for pg in my_pages:
        for qidx_str, v in spec["question"].items():
            if qidx_str == str(question_idx):
                continue
            if pg in v["pages"]:
                shared_pages.append(pg)
                shared_with.append(get_question_label(spec, qidx_str))
    if not shared_pages:
        return ""
    shared_pages = sorted(list(set(shared_pages)))
    page_slash_pages = "page" if len(shared_pages) == 1 else "pages"
    rendered_shared_pages = ", ".join(str(x) for x in shared_pages)
    is_slash_are = "is" if len(shared_with) == 1 else "are"
    rendered_shared_with = ", ".join(shared_with)
    return f"""
        <p>
          {verbose_qlabel} shares {page_slash_pages} {rendered_shared_pages}
          of the assessment with {rendered_shared_with}
          which {is_slash_are} independently markable.
        </p>
        <ul>
          <li><em>Do not</em> mark any parts of {rendered_shared_with}
            at this time.</li>
          <li>You may want to use the
            &ldquo;crop to region&rdquo; feature.</li>
          <li>You will not see any annotations to {rendered_shared_with};
            see
            <a href="https://plom.readthedocs.io/en/latest/preparing_an_exam.html#what-should-each-question-be">docs about Plom questions</a>.
          </li>
        </ul>
        <p>
          Shared pages are a <em>new feature in Plom;</em>
          please <strong>discuss your marking assignment with
          your instructor</strong>.
        </p>
    """
