# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Edith Coates
# Copyright (C) 2023 Natalie Balashov

import csv
import fitz
import tempfile
from pathlib import Path
from collections import defaultdict

from django.core.management import call_command

from plom.create.scribble_utils import (
    scribble_name_and_id,
    scribble_pages,
    splitFakeFile,
)

from Papers.services import SpecificationService


class DemoBundleService:
    """Handle generating demo bundles."""

    def get_classlist_as_dict(self):
        with tempfile.TemporaryDirectory() as td:
            classlist_file = Path(td) / "classlist.csv"
            classlist = []
            call_command("plom_preparation_classlist", "download", f"{classlist_file}")
            with open(classlist_file) as fh:
                red = csv.DictReader(fh, skipinitialspace=True)
                for row in red:
                    classlist.append(
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "paper_number": row["paper_number"],
                        }
                    )
        return classlist

    def get_default_paper_length(self):
        """Get the default number of pages in a paper from the specification."""
        return SpecificationService().get_n_pages()

    def split_into_bundle_files(self, out_file, config):
        """Split the single scribble PDF file into the designated number of bundles.

        Args:
            out_file (path.Path): path to the monolithic scribble PDF
            config (dict): server config
        """
        bundles = config["bundles"]
        n_bundles = len(bundles)
        default_n_pages = self.get_default_paper_length()

        with fitz.open(out_file) as scribble_pdf:
            from_page_idx = 0
            to_page_idx = default_n_pages
            curr_bundle_idx = 0
            bundle_doc = None

            for paper in range(1, config["num_to_produce"] + 1):
                print("PAPER", paper)

                curr_bundle = bundles[curr_bundle_idx]
                for key in curr_bundle.keys():
                    if key in [
                        "garbage_page_papers",
                        "duplicate_page_papers",
                    ]:
                        if paper in curr_bundle[key]:
                            print(
                                f"to index incremented because paper {paper} is in {key}"
                            )
                            to_page_idx += 1
                    elif key == "duplicates":
                        for inst in curr_bundle["duplicates"]:
                            if inst["paper"] == paper:
                                to_page_idx += 1

                print("From", from_page_idx)
                print("to", to_page_idx)

                if paper == curr_bundle["first_paper"]:
                    bundle_doc = fitz.open()
                bundle_doc.insert_pdf(
                    scribble_pdf, from_page=from_page_idx, to_page=to_page_idx
                )
                if paper == curr_bundle["last_paper"]:
                    bundle_filename = out_file.stem + f"{curr_bundle_idx + 1}.pdf"
                    bundle_doc.save(out_file.with_name(bundle_filename))
                    bundle_doc.close()
                    curr_bundle_idx += 1

                from_page_idx = to_page_idx + 1
                to_page_idx = from_page_idx + default_n_pages - 1

    def get_extra_page(self):
        # Assumes that the extra page has been generated
        call_command(
            "plom_preparation_extrapage",
            "download",
            "media/papersToPrint/extra_page.pdf",
        )

    def assign_students_to_papers(self, paper_list, classlist):
        # prenamed papers are "exam_XXXX_YYYYYYY" and normal are "exam_XXXX"
        all_sid = [row["id"] for row in classlist]
        id_to_name = {X["id"]: X["name"] for X in classlist}

        assignment = []

        for path in paper_list:
            paper_number = path.stem.split("_")[1]
            if len(path.stem.split("_")) == 3:  # paper is prenamed
                sid = path.stem.split("_")[2]
                all_sid.remove(sid)
                assignment.append(
                    {
                        "path": path,
                        "id": sid,
                        "name": id_to_name[sid],
                        "prenamed": True,
                        "paper_number": paper_number,
                    }
                )
            else:
                sid = all_sid.pop(0)

                assignment.append(
                    {
                        "path": path,
                        "id": sid,
                        "name": id_to_name[sid],
                        "prenamed": False,
                        "paper_number": paper_number,
                    }
                )

        return assignment

    def make_last_page_with_wrong_version(self, pdf_doc, paper_number):
        """Muck around with the last page for testing purposes.

        Removes the last page of the doc and replaces it with a nearly
        blank page that contains a qr-code that is nearly valid except
        that the version is wrong.

        Args:
            pdf_doc (fitz.Document): a pdf document of a test-paper.
            paper_number (int): the paper_number of that test-paper.

        Returns:
            pdf_doc (fitz.Document): the updated pdf-document with replaced last page.
        """
        from plom import SpecVerifier
        from plom.create.mergeAndCodePages import create_QR_codes

        # a rather cludge way to get at the spec via commandline tools
        # really we just need the public code.
        with tempfile.TemporaryDirectory() as td:
            spec_file = Path(td) / "the_spec.toml"
            call_command("plom_preparation_test_spec", "download", f"{spec_file}")
            spec = SpecVerifier.from_toml_file(spec_file).spec
            code = spec["publicCode"]
            max_ver = spec["numberOfVersions"]

            # take last page of paper and insert a qr-code from the page before that.
            page_number = pdf_doc.page_count
            # make a qr-code for this paper/page but with version max+1
            qr_pngs = create_QR_codes(
                paper_number, page_number, max_ver + 1, code, Path(td)
            )
            pdf_doc.delete_page()  # this defaults to the last page.

            pdf_doc.new_page(-1)

            pdf_doc[-1].insert_text(
                (120, 50),
                text="This is a page has a qr-code with the wrong version",
                fontsize=18,
                color=[0, 0.75, 0.75],
            )
            # hard-code one qr-code in top-left
            rect = fitz.Rect(50, 50, 50 + 70, 50 + 70)
            pdf_doc[-1].insert_image(rect, pixmap=fitz.Pixmap(qr_pngs[1]), overlay=True)

    def append_extra_page(self, pdf_doc, paper_number, student_id, extra_page_path):
        with fitz.open(extra_page_path) as extra_pages_pdf:
            pdf_doc.insert_pdf(
                extra_pages_pdf,
                from_page=0,
                to_page=1,
                start_at=-1,
            )
            page_rect = pdf_doc[-1].rect
            # stamp some info on it - TODO - make this look better.
            tw = fitz.TextWriter(page_rect, color=(0, 0, 1))
            # TODO - make these numbers less magical
            maxbox = fitz.Rect(25, 400, 500, 600)
            # page.draw_rect(maxbox, color=(1, 0, 0))
            excess = tw.fill_textbox(
                maxbox,
                f"EXTRA PAGE - t{paper_number} Q1 - {student_id}",
                align=fitz.TEXT_ALIGN_LEFT,
                fontsize=18,
                font=fitz.Font("helv"),
            )
            assert not excess, "Text didn't fit: is extra-page text too long?"
            tw.write_text(pdf_doc[-1])
            tw.write_text(pdf_doc[-2])

    def append_duplicate_page(self, pdf_doc, page_number):
        last_page = len(pdf_doc) - 1
        pdf_doc.fullcopy_page(last_page)

    def insert_qr_from_previous_page(self, pdf_doc, paper_number):
        """Muck around with the penultimate page for testing purposes.

        Stamps a qr-code for the second-last page onto the last page,
        in order to create a page with inconsistent qr-codes. This can
        happen when, for example, a folded page is fed into the scanner.

        Args:
            pdf_doc (fitz.Document): a pdf document of a test-paper.
            paper_number (int): the paper_number of that test-paper.

        Returns:
            pdf_doc (fitz.Document): the updated pdf-document with the
            inconsistent qr-codes on its last page.
        """
        from plom import SpecVerifier
        from plom.create.mergeAndCodePages import create_QR_codes

        # a rather cludge way to get at the spec via commandline tools
        # really we just need the public code.
        with tempfile.TemporaryDirectory() as td:
            spec_file = Path(td) / "the_spec.toml"
            call_command("plom_preparation_test_spec", "download", f"{spec_file}")
            code = SpecVerifier.from_toml_file(spec_file).spec["publicCode"]

            # take last page of paper and insert a qr-code from the page before that.
            page_number = pdf_doc.page_count
            # make a qr-code for this paper, but for second-last page.
            qr_pngs = create_QR_codes(paper_number, page_number - 1, 1, code, Path(td))
            pdf_doc[-1].insert_text(
                (120, 200),
                text="This is a page has a qr-code from the previous page",
                fontsize=18,
                color=[0, 0.75, 0.75],
            )
            # hard-code one qr-code in top-left
            rect = fitz.Rect(50, 50 + 70, 50 + 70, 50 + 70 * 2)
            pdf_doc[-1].insert_image(rect, pixmap=fitz.Pixmap(qr_pngs[1]), overlay=True)

    def append_garbage_page(self, pdf_doc):
        pdf_doc.insert_page(
            -1, text="This is a garbage page", fontsize=18, color=[0, 0.75, 0]
        )

    def insert_page_from_another_assessment(self, pdf_doc):
        from plom import SpecVerifier
        from plom.create.mergeAndCodePages import create_QR_codes

        # a rather cludge way to get at the spec via commandline tools
        # really we just need the public code.
        with tempfile.TemporaryDirectory() as td:
            spec_file = Path(td) / "the_spec.toml"
            call_command("plom_preparation_test_spec", "download", f"{spec_file}")
            spec = SpecVerifier.from_toml_file(spec_file).spec
            # now make a new magic code that is not the same as the spec
            if spec["publicCode"] == "00000":
                code = "99999"
            else:
                code = "00000"
            qr_pngs = create_QR_codes(1, 1, 1, code, Path(td))
            # now we have qr-code pngs that we can use to make a bogus page from a different assessment.
            # these are called "qr_0001_pg1_4.png" etc.
            pdf_doc.new_page(-1)
            pdf_doc[-1].insert_text(
                (120, 200),
                text="This is a page from a different assessment",
                fontsize=18,
                color=[0, 0.75, 0.75],
            )
            # hard-code one qr-code in top-left
            rect = fitz.Rect(50, 50, 50 + 70, 50 + 70)
            # the 2nd qr-code goes in NW corner.
            pdf_doc[-1].insert_image(rect, pixmap=fitz.Pixmap(qr_pngs[1]), overlay=True)
            # (note don't care if even/odd page: is a new page, no staple indicator)

    def append_out_of_range_paper_and_page(self, pdf_doc):
        """Append two new pages to the pdf - one as test-1 page-999 and one as test-99999 page-1."""
        from plom import SpecVerifier
        from plom.create.mergeAndCodePages import create_QR_codes

        # a rather cludge way to get at the spec via commandline tools
        # really we just need the public code.
        with tempfile.TemporaryDirectory() as td:
            spec_file = Path(td) / "the_spec.toml"
            call_command("plom_preparation_test_spec", "download", f"{spec_file}")
            code = SpecVerifier.from_toml_file(spec_file).spec["publicCode"]

            qr_pngs = create_QR_codes(99999, 1, 1, code, Path(td))
            pdf_doc.new_page(-1)
            pdf_doc[-1].insert_text(
                (120, 200),
                text="This is a page from a non-existent paper",
                fontsize=18,
                color=[0, 0.75, 0.75],
            )
            # hard-code one qr-code in top-left
            rect = fitz.Rect(50, 50, 50 + 70, 50 + 70)
            # the 2nd qr-code goes in NW corner.
            pdf_doc[-1].insert_image(rect, pixmap=fitz.Pixmap(qr_pngs[1]), overlay=True)

            qr_pngs = create_QR_codes(1, 999, 1, code, Path(td))
            pdf_doc.new_page(-1)
            pdf_doc[-1].insert_text(
                (120, 200),
                text="This is a non-existent page from an existing test",
                fontsize=18,
                color=[0, 0.75, 0.75],
            )
            # hard-code one qr-code in top-left
            rect = fitz.Rect(50, 50, 50 + 70, 50 + 70)
            # the 2nd qr-code goes in NW corner.
            pdf_doc[-1].insert_image(rect, pixmap=fitz.Pixmap(qr_pngs[1]), overlay=True)

    def _convert_duplicates_dict(self, duplicates):
        """If duplicates is a list of dicts, convert into a dict."""
        duplicates_dict = {}
        for paper_dict in duplicates:
            duplicates_dict[paper_dict["paper"]] = paper_dict["page"]
        return duplicates_dict

    def _convert_duplicates_list(self, duplicates):
        """If duplicates is a list, convert into a dict."""
        duplicates_dict = {}
        for paper in duplicates:
            duplicates_dict[paper] = -1
        return duplicates_dict

    def scribble_bundle(
        self,
        assigned_papers_ids,
        extra_page_path,
        out_file,
        *,
        extra_page_papers=[],
        garbage_page_papers=[],
        duplicate_pages=[],
        duplicate_qr=[],
        wrong_version=[],
    ):
        # extra_page_papers = list of paper_numbers to which we append a couple of extra_pages
        # garbage_page_papers = list of paper_numbers to which we append a garbage page
        # duplicate_pages = a list of papers to have their final page duplicated.
        # wrong_version = list of paper_numbers to which we replace last page with a blank but wrong version number.

        # A complete collection of the pdfs created
        with fitz.open() as all_pdf_documents:
            for paper in assigned_papers_ids:
                with fitz.open(paper["path"]) as pdf_document:
                    # first put an ID on paper if it is not prenamed.
                    if not paper["prenamed"]:
                        scribble_name_and_id(pdf_document, paper["id"], paper["name"])
                    paper_number = int(paper["paper_number"])

                    if paper_number in wrong_version:
                        self.make_last_page_with_wrong_version(
                            pdf_document, paper_number
                        )

                    if paper_number in extra_page_papers:
                        self.append_extra_page(
                            pdf_document,
                            paper["paper_number"],
                            paper["id"],
                            extra_page_path,
                        )
                    if paper_number in duplicate_pages:
                        self.append_duplicate_page(pdf_document, duplicate_pages)

                    # scribble on the pages
                    scribble_pages(pdf_document)

                    # insert a qr-code from a previous page after scribbling
                    if paper_number in duplicate_qr:
                        self.insert_qr_from_previous_page(pdf_document, paper_number)

                    # append a garbage page after the scribbling
                    if paper_number in garbage_page_papers:
                        self.append_garbage_page(pdf_document)

                    # TODO: Append out-of-range papers and wrong public codes to some bundles

                    # finally, append this to the bundle
                    all_pdf_documents.insert_pdf(pdf_document)

            all_pdf_documents.save(out_file)

    def _flatten(self, list_to_flatten):
        flat_list = []
        for sublist in list_to_flatten:
            flat_list += sublist
        return flat_list

    def _get_combined_list(self, bundles: dict, key: str):
        filtered = filter(lambda bundle: key in bundle.keys(), bundles)
        return self._flatten([bundle[key] for bundle in filtered])

    def scribble_on_exams(self, config):
        bundles = config["bundles"]
        n_bundles = len(bundles)

        classlist = self.get_classlist_as_dict()
        classlist_length = len(classlist)
        papers_to_print = Path("media/papersToPrint")
        paper_list = [paper for paper in papers_to_print.glob("exam*.pdf")]
        self.get_extra_page()  # download copy of the extra-page pdf to papersToPrint subdirectory
        extra_page_path = papers_to_print / "extra_page.pdf"

        number_papers_to_use = classlist_length
        papers_to_use = sorted(paper_list)[:number_papers_to_use]

        assigned_papers_ids = self.assign_students_to_papers(papers_to_use, classlist)
        number_prenamed = sum(1 for X in assigned_papers_ids if X["prenamed"])

        print("v" * 40)
        print(
            f"Making a bundle of {len(papers_to_use)} papers, of which {number_prenamed} are prenamed"
        )
        print("^" * 40)

        for i in range(n_bundles):
            bundle = defaultdict(list, bundles[i])
            bundle_path = Path(f"fake_bundle{i + 1}.pdf")

            first_idx = bundle["first_paper"] - 1
            last_idx = bundle["last_paper"]
            papers_in_bundle = assigned_papers_ids[first_idx:last_idx]

            self.scribble_bundle(
                papers_in_bundle,
                extra_page_path,
                bundle_path,
                extra_page_papers=bundle["extra_page_papers"],
                garbage_page_papers=bundle["garbage_page_papers"],
                duplicate_pages=bundle["duplicate_pages"],
                duplicate_qr=bundle["duplicate_qr"],
                wrong_version=bundle["wrong_version"],
            )
