# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020 Andrew Rechnitzer
# Copyright (C) 2020-2021 Colin B. Macdonald

import logging
from math import ceil
import random
from pathlib import Path
import pkg_resources

import toml

specdir = "specAndDatabase"
log = logging.getLogger("spec")


class SpecVerifier:
    """Verify Plom exam specifications.

    Example specification:
    >>> raw = {
    ... 'name': 'plomdemo',
    ... 'longName': 'Midterm Demo using Plom',
    ... 'numberOfVersions': 2,
    ... 'numberOfPages': 6,
    ... 'numberToProduce': 20,
    ... 'numberToName': 10,
    ... 'numberOfQuestions': 3,
    ... 'privateSeed': '1001378822317872',
    ... 'publicCode': '270385',
    ... 'idPages': {'pages': [1]},
    ... 'doNotMark': {'pages': [2]},
    ... 'question': {
    ...     '1': {'pages': [3], 'mark': 5, 'select': 'shuffle'},
    ...     '2': {'pages': [4], 'mark': 10, 'select': 'fix'},
    ...     '3': {'pages': [5, 6], 'mark': 10, 'select': 'shuffle'}
    ...    }
    ... }
    >>> spec = SpecVerifier(raw)

    Here `spec` is an object representing a Plom exam specification:
    >>> print(spec)
    Plom exam specification:
      Name of test = plomdemo
      Long name of test = Midterm Demo using Plom
      Number of source versions = 2
      Number of tests to produce = 20
      Number of those to be printed with names = 10
      Number of pages = 6
      IDpages = [1]
      Do not mark pages = [2]
      Number of questions to mark = 3
        Question.1: pages [3], selected as shuffle, worth 5 marks
        Question.2: pages [4], selected as fix, worth 10 marks
        Question.3: pages [5, 6], selected as shuffle, worth 10 marks
      Test total = 25 marks


    We can verify that this input is valid:
    >>> spec.verifySpec()     # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Check specification keys
        contains "name" - check
        contains "longName" - check
        ...
        Page 5 used once - check
        Page 6 used once - check

    The spec above already has private and public random numbers, but
    these would typically be autogenerated:
    >>> spec.checkCodes()
    WARNING - privateSeed is already set. Not replacing this.
    WARNING - publicCode is already set. Not replacing this.

    Write the result for the server to find on disk:
    >>> spec.saveVerifiedSpec()     # doctest: +SKIP
    """

    def __init__(self, d):
        """Initialize a SpecVerifier from a dict.

        Args:
            d (dict): an exam specification.
        """
        self.spec = d

    @classmethod
    def _template_as_bytes(cls):
        return pkg_resources.resource_string("plom", "templateTestSpec.toml")

    @classmethod
    def _template_as_string(cls):
        # TODO: or just use a triple-quoted inline string
        return cls._template_as_bytes().decode()

    @classmethod
    def create_template(cls, fname="testSpec.toml"):
        """Create a documented example exam specification."""
        template = cls._template_as_bytes()
        with open(fname, "wb") as fh:
            fh.write(template)

    @classmethod
    def create_demo_template(cls, fname="demoSpec.toml", *, num_to_produce=None):
        """Create a documented demo exam specification.

        This does not create a Spec object, but rather saves the
        template to disc.
        """
        s = cls._template_as_string()
        if num_to_produce:
            from plom.produce.demotools import getDemoClassListLength

            # TODO: 20 and 10 in source file hardcoded here, use regex instead
            s = s.replace(
                "numberToProduce = 20",
                "numberToProduce = {}".format(num_to_produce),
            )
            classlist_len = getDemoClassListLength()
            if num_to_produce > classlist_len:
                raise ValueError(
                    "Demo size capped at classlist length of {}".format(classlist_len)
                )
            s = s.replace(
                "numberToName = 10",
                "numberToName = {}".format(min(num_to_produce // 2, classlist_len)),
            )
        with open(fname, "w") as fh:
            fh.write(s)

    @classmethod
    def demo(cls):
        return cls(toml.loads(cls._template_as_string()))

    @classmethod
    def from_toml_file(cls, fname="testSpec.toml"):
        """Initialize a SpecVerifier from a toml file."""
        return cls(toml.load(fname))

    @classmethod
    def load_verified(cls, fname=Path(specdir) / "verifiedSpec.toml"):
        """Initialize a SpecVerifier from the default verified toml file."""
        # TODO: maybe we should do some testing here?
        return cls(toml.load(fname))

    # this allows spec["numberToProduce"] for all
    def __getitem__(self, what):
        return self.spec[what]

    # this allows spec.number_to_produce
    @property
    def number_to_produce(self):
        return self.spec["numberToProduce"]

    @property
    def number_to_name(self):
        return self.spec["numberToName"]

    def set_number_to_name(self, n):
        """Set previously-deferred number of named papers.

        exceptions:
            ValueError: number of named papers already set.
        """
        if self.spec["numberToName"] >= 0:
            raise ValueError("Number of named papers already set: read-only")
        self.spec["numberToName"] = n
        log.info('deferred number of named papers now set to "{}"'.format(n))

    def set_number_to_produce(self, n, spare_percent=10, min_extra=5, max_extra=100):
        """Set previously-deferred number of named papers.

        exceptions:
            ValueError: number of named papers already set.
        """
        extra = ceil(spare_percent * n / 100)
        extra = min(max(extra, min_extra), max_extra)  # threshold
        self.spec["numberToProduce"] = n + extra
        log.info(
            'deferred number of papers to produce now set to "{}"'.format(
                self.spec["numberToProduce"]
            )
        )

    def __str__(self):
        s = "Plom exam specification:\n  "
        s += "\n  ".join(
            (
                "Name of test = {}".format(self.spec["name"]),
                "Long name of test = {}".format(self.spec["longName"]),
                "Number of source versions = {}".format(self.spec["numberOfVersions"]),
                # "Public code (to prevent project collisions) = {}".format(self.spec["publicCode"]),
                # "Private random seed (for randomisation) = {}".format(self.spec["privateSeed"]),
                "Number of tests to produce = {}".format(self.spec["numberToProduce"]),
                "Number of those to be printed with names = {}".format(
                    self.spec["numberToName"]
                ),
                "Number of pages = {}".format(self.spec["numberOfPages"]),
                "IDpages = {}".format(self.spec["idPages"]["pages"]),
                "Do not mark pages = {}".format(self.spec["doNotMark"]["pages"]),
                "Number of questions to mark = {}".format(
                    self.spec["numberOfQuestions"]
                ),
            )
        )
        s += "\n"
        tot = 0
        for g in range(self.spec["numberOfQuestions"]):
            gs = str(g + 1)
            tot += self.spec["question"][gs]["mark"]
            s += "    Question.{}: pages {}, selected as {}, worth {} marks\n".format(
                gs,
                self.spec["question"][gs]["pages"],
                self.spec["question"][gs]["select"],
                self.spec["question"][gs]["mark"],
            )
        s += "  Test total = {} marks".format(tot)
        return s

    def get_public_spec_dict(self):
        """Return a copy of the spec dict with private info removed."""
        d = self.spec.copy()
        d.pop("privateSeed")
        return d

    def verifySpec(self):
        """Check that spec contains required attributes.

        TODO: need a less verbose version that raises exceptions
        and doesn't print, more appropriate for library calls.
        """
        self.check_keys()
        self.check_name_and_production_numbers()
        lastPage = self.spec["numberOfPages"]
        self.check_IDPages(lastPage)
        self.check_doNotMark(lastPage)

        print("Checking question groups")
        for g in range(self.spec["numberOfQuestions"]):
            self.check_group(str(g + 1), lastPage)

        self.check_pages()

    def checkCodes(self):
        """Add public and private codes if the spec doesn't already have them."""
        if "privateSeed" in self.spec:
            print("WARNING - privateSeed is already set. Not replacing this.")
        else:
            print("Assigning a privateSeed to the spec - check")
            self.spec["privateSeed"] = str(random.randrange(0, 10 ** 16)).zfill(16)

        if "publicCode" in self.spec:
            print("WARNING - publicCode is already set. Not replacing this.")
        else:
            print("Assigning a publicCode to the spec - check")
            self.spec["publicCode"] = str(random.randrange(0, 10 ** 6)).zfill(6)

    def saveVerifiedSpec(self, verbose=False):
        """Saves the verified spec to a particular name."""
        if verbose:
            print('Saving the verified spec to "verifiedSpec.toml"')
        with open(Path(specdir) / "verifiedSpec.toml", "w+") as fh:
            fh.write("# This file is produced by the plom-build script.\n")
            fh.write(
                "# Do not edit this file. Instead edit testSpec.toml and rerun plom-build.\n"
            )
            toml.dump(self.spec, fh)

    # a couple of useful functions
    def isPositiveInt(self, s):
        try:
            n = int(s)
            if n > 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def isNonNegInt(self, s):
        try:
            n = int(s)
            if n >= 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def isContiguousListPosInt(self, l, lastPage):
        # check it is a list
        if type(l) is not list:
            return False
        # check each entry is 0<n<=lastPage
        for n in l:
            if not self.isPositiveInt(n):
                return False
            if n > lastPage:
                return False
        # check it is contiguous
        sl = set(l)
        for n in range(min(sl), max(sl) + 1):
            if n not in sl:
                return False
        # all tests passed
        return True

    # define all the specification checks
    def check_keys(self):
        print("Check specification keys")
        # check it contains required keys
        for x in [
            "name",
            "longName",
            "numberOfVersions",
            "numberOfPages",
            "numberToProduce",
            "numberToName",
            "numberOfQuestions",
            "idPages",
            "doNotMark",
        ]:
            if x not in self.spec:
                print('Specification error - must contain "{}" but does not.'.format(x))
                exit(1)
            else:
                print('\tcontains "{}" - check'.format(x))
        # check it contains at least one question to mark
        if "1" in self.spec["question"]:
            print('\tcontains at least one question (ie "question.1") - check')
        else:
            print(
                "Specification error - must contain at least one question to mark but does not."
            )
            exit(1)

    def check_name_and_production_numbers(self):
        print("Check specification name and numbers")
        # check name is alphanumeric and non-zero length
        print("\tChecking names")
        if self.spec["name"].isalnum() and len(self.spec["name"]) > 0:
            print('\t\tname "{}" has non-zero length - check'.format(self.spec["name"]))
            print(
                '\t\tname "{}" is alphanumeric string - check'.format(self.spec["name"])
            )
        else:
            print(
                "Specification error - Test name must be an alphanumeric string of non-zero length."
            )
            exit(1)

        if (
            all(x.isalnum() or x.isspace() for x in self.spec["longName"])
            and len(self.spec["longName"]) > 0
        ):
            print(
                '\t\tName "{}" has non-zero length - check'.format(
                    self.spec["longName"]
                )
            )
            print(
                '\t\tName "{}" is alphanumeric string - check'.format(
                    self.spec["longName"]
                )
            )
        else:
            print(
                "Specification error - Test longName must be an alphanumeric string of non-zero length."
            )
            exit(1)

        print("\tChecking production numbers")
        # all should be positive integers
        for x in [
            "numberOfVersions",
            "numberOfPages",
            "numberOfQuestions",
        ]:
            if self.isPositiveInt(self.spec[x]):
                print(
                    '\t\t"{}" = {} is positive integer - check'.format(x, self.spec[x])
                )
            else:
                print(
                    'Specification error - "{}" must be a positive integer.'.format(x)
                )
                exit(1)
        for x in ("numberToName", "numberToProduce"):
            try:
                self.spec[x] = int(self.spec[x])
                print('\t\t"{}" = {} is integer - check'.format(x, self.spec[x]))
            except ValueError:
                raise ValueError(
                    'Specification error - "{}" must be an integer.'.format(x)
                )
            if self.spec[x] < 0:
                print('\t\t"{}" is negative: will determine from classlist!'.format(x))

        if self.spec["numberToProduce"] == 0:
            raise ValueError('Specification error - "numberToProduce" cannot be zero.')

        if self.spec["numberToProduce"] > 0:
            if self.spec["numberToProduce"] < self.spec["numberToName"]:
                raise ValueError(
                    "Specification error - insufficient papers: producing fewer papers {} than you wish to name {}. Produce more papers.".format(
                        self.spec["numberToProduce"], self.spec["numberToName"]
                    )
                )
            else:
                print(
                    "\t\tSufficiently many papers: papers to prduce larger than number of named papers - check"
                )
            if self.spec["numberToProduce"] < 1.05 * self.spec["numberToName"]:
                print(
                    "WARNING = you are not producing less than 5% un-named papers. We recommend that you produce more un-named papers"
                )
            else:
                print("\t\tProducing sufficient spare papers - check")

        for k in range(self.spec["numberOfQuestions"]):
            if str(k + 1) in self.spec["question"]:
                print(
                    "\t\tFound question {} of {} - check".format(
                        k + 1, self.spec["numberOfQuestions"]
                    )
                )
            else:
                print("Specification error - could not find question {} ".format(k + 1))
                exit(1)

    def check_IDPages(self, lastPage):
        print("Checking IDpages")
        if "pages" not in self.spec["idPages"]:
            print('IDpages error - could not find "pages" key')
            exit(1)
        if not self.isContiguousListPosInt(self.spec["idPages"]["pages"], lastPage):
            print(
                'IDpages error - "pages" = {} should be a list of positive integers in range'.format(
                    self.spec["idPages"]["pages"]
                )
            )
            exit(1)
        else:
            print("\t\tIDpages is contiguous list of positive integers - check")
        # check that page 1 is in there.
        if self.spec["idPages"]["pages"][0] != 1:
            print(
                "Warning - page 1 is not part if your ID pages - are you sure you want to do this?"
            )

    def check_doNotMark(self, lastPage):
        print("Checking DoNotMark-pages")
        if "pages" not in self.spec["doNotMark"]:
            print('DoNotMark pages error - could not find "pages" key')
            exit(1)
        if type(self.spec["doNotMark"]["pages"]) is not list:
            print(
                'DoNotMark pages error - "pages" = {} should be a list of positive integers'.format(
                    self.spec["doNotMark"]["pages"]
                )
            )
            exit(1)
        # should be a list of positive integers
        for n in self.spec["doNotMark"]["pages"]:
            if self.isPositiveInt(n) and n <= lastPage:
                pass
            else:
                print(
                    'DoNotMark pages error - "pages" = {} should be a list of positive integers in range'.format(
                        self.spec["doNotMark"]["pages"]
                    )
                )
                exit(1)
        print("\t\tDoNotMark pages is list of positive integers - check")

    def check_group(self, g, lastPage):
        print("\tChecking question group #{}".format(g))
        # each group has keys
        for x in ["pages", "select", "mark"]:
            if x not in self.spec["question"][g]:
                print("Question error - could not find {} key".format(x))
                exit(1)
        # check pages is contiguous list of positive integers
        if self.isContiguousListPosInt(self.spec["question"][g]["pages"], lastPage):
            print(
                "\t\tpages {} is list of contiguous positive integers - check".format(
                    self.spec["question"][g]["pages"]
                )
            )
        else:
            print(
                "Question error - pages {} is not list of contiguous positive integers".format(
                    self.spec["question"][g]["pages"]
                )
            )
            exit(1)
        # check mark is positive integer
        if self.isPositiveInt(self.spec["question"][g]["mark"]):
            print(
                "\t\tmark {} is positive integer - check".format(
                    self.spec["question"][g]["mark"]
                )
            )
        else:
            print(
                "Question error - mark {} is not a positive integer".format(
                    self.spec["question"][g]["mark"]
                )
            )
            exit(1)
        # check select is "fix" or "shuffle"
        if self.spec["question"][g]["select"] in ["fix", "shuffle"]:
            print('\t\tselect is "fix" or "shuffle" - check')
        else:
            print(
                'Question error - select {} is not "fix" or "shuffle"'.format(
                    self.spec["question"][g]["select"]
                )
            )
            exit(1)

    def check_pages(self):
        print("Checking all pages used exactly once:")
        pageUse = {k + 1: 0 for k in range(self.spec["numberOfPages"])}
        for p in self.spec["idPages"]["pages"]:
            pageUse[p] += 1
        for p in self.spec["doNotMark"]["pages"]:
            pageUse[p] += 1
        for g in range(self.spec["numberOfQuestions"]):
            for p in self.spec["question"][str(g + 1)]["pages"]:
                pageUse[p] += 1
        for p in range(1, self.spec["numberOfPages"] + 1):
            if pageUse[p] != 1:
                print("Page Use error - page {} used {} times".format(p, pageUse[p]))
                exit(1)
            else:
                print("\tPage {} used once - check".format(p))
