# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020-2022 Colin B. Macdonald

import importlib.resources as resources
import tempfile

import plom
from .textools import buildLaTeX


def test_latex_exam_template():
    content = resources.read_text(plom, "latexTemplate.tex")
    with tempfile.NamedTemporaryFile() as f:
        r, out = buildLaTeX(content, f)
        assert r == 0


def test_latex_exam_templatev2():
    content = resources.read_text(plom, "latexTemplatev2.tex")
    with tempfile.NamedTemporaryFile() as f:
        r, out = buildLaTeX(content, f)
        assert r == 0


def test_latex_fails_and_makes_useful_output():
    content = r"""\documentclass{article}
        \begin{document}
        \InvalidCommand
        \end{document}
    """
    with tempfile.NamedTemporaryFile() as f:
        r, out = buildLaTeX(content, f)
        assert r != 0
        assert r"\InvalidCommand" in out
        assert "Undefined" in out
