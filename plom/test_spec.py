# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2021 Colin B. Macdonald

from pytest import raises
from plom import SpecVerifier, get_question_label

raw = SpecVerifier.demo().spec


def test_spec_demo():
    s = SpecVerifier.demo()
    assert s.number_to_name
    assert s.number_to_produce


def test_spec_verify():
    s = SpecVerifier.demo()
    s.verifySpec(verbose=False)


def test_spec_too_many_named():
    r = raw.copy()
    r["numberToProduce"] = 50
    r["numberToName"] = 60
    s = SpecVerifier(r)
    raises(ValueError, lambda: s.verifySpec(verbose=False))


def test_spec_negatives_still_pass():
    r = raw.copy()
    r["numberToName"] = -1
    r["numberToProduce"] = -1
    SpecVerifier(r).verifySpec(verbose=False)


def test_spec_setting_adds_spares():
    r = raw.copy()
    r["numberToName"] = -1
    r["numberToProduce"] = -1
    s = SpecVerifier(r)
    s.set_number_papers_to_name(16)
    s.set_number_papers_add_spares(16)
    assert s.numberToName == 16
    # creates some spares
    assert s.numberToProduce > 16
    s.verifySpec(verbose=False)


def test_spec_invalid_shortname():
    r = raw.copy()
    r["name"] = "no spaces"
    raises(ValueError, lambda: SpecVerifier(r).verifySpec(verbose=False))


def test_spec_too_many_named():
    r = raw.copy()
    r["numberToProduce"] = 50
    r["numberToName"] = 60
    raises(ValueError, lambda: SpecVerifier(r).verifySpec(verbose=False))


def test_spec_longname_slash_issue1364():
    r = raw.copy()
    r["longName"] = 'Math123 / Bio321 Midterm ∫∇·Fdv — "have fun!"😀'
    SpecVerifier(r).verifySpec(verbose=False)


def test_spec_question_label_printer():
    sd = SpecVerifier.demo()
    r = raw.copy()
    r["question"]["1"]["label"] = "Track 1"
    r["question"]["2"]["label"] = ""
    s = SpecVerifier(r)
    assert get_question_label(s, 0) == "Track 1"
    assert get_question_label(s, 1) == "Q2"
    assert get_question_label(s, 2) == get_question_label(sd, 2)


def test_spec_question_label_printer_errors():
    s = SpecVerifier.demo()
    N = s["numberOfQuestions"]
    raises(ValueError, lambda: get_question_label(s, N))
    raises(ValueError, lambda: get_question_label(s, -1))
