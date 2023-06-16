# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Edith Coates

import subprocess
from time import sleep
from shlex import split

from django.core.management import call_command
from django.conf import settings

from Scan.services import ScanCastService
from Scan.models import ExtraStagingImage, StagingImage
from Papers.services import SpecificationService


class DemoCreationService:
    """Handle creating the demo exam and populating the database."""

    def make_groups_and_users(self):
        print("Create groups and users")
        call_command("plom_create_groups")
        call_command("plom_create_demo_users")

    def prepare_assessment(self, config):
        print("Prepare assessment: ")
        print(
            "\tUpload demo spec, upload source pdfs and classlist, enable prenaming, and generate qv-map"
        )
        call_command("plom_demo_spec")

        (settings.BASE_DIR / "fixtures").mkdir(exist_ok=True)
        call_command(
            "dumpdata",
            "--natural-foreign",
            "Papers.Specification",
            f"-o{settings.BASE_DIR}/fixtures/test_spec.json",
        )

        call_command(
            "plom_preparation_test_source",
            "upload",
            "-v 1",
            "useful_files_for_testing/test_version1.pdf",
        )
        call_command(
            "plom_preparation_test_source",
            "upload",
            "-v 2",
            "useful_files_for_testing/test_version2.pdf",
        )
        call_command("plom_preparation_prenaming", enable=True)
        call_command(
            "plom_preparation_classlist",
            "upload",
            "useful_files_for_testing/cl_for_demo.csv",
        )

        n_to_produce = config["num_to_produce"]
        call_command("plom_preparation_qvmap", "generate", f"-n {n_to_produce}")

        call_command(
            "dumpdata",
            "--natural-foreign",
            "Preparation",
            f"-o{settings.BASE_DIR}/fixtures/preparation.json",
        )

    def build_db_and_papers(self):
        print("Populating database in background")
        call_command("plom_papers", "build_db")

        call_command(
            "dumpdata",
            "--natural-foreign",
            "Papers.Paper",
            "--exclude=Papers.FixedPage",
            "--exclude=Papers.IDPage",
            f"-o{settings.BASE_DIR}/fixtures/papers.json",
        )

        call_command("plom_preparation_extrapage", "build")
        call_command("plom_build_papers", "--start-all")

    def wait_for_papers_to_be_ready(self):
        py_man_ep = "python3 manage.py plom_preparation_extrapage"
        py_man_papers = "python3 manage.py plom_build_papers --status"
        ep_todo = True
        papers_todo = True

        sleep(1)
        while True:
            if ep_todo:
                out_ep = subprocess.check_output(split(py_man_ep)).decode("utf-8")
                if "complete" in out_ep:
                    print("Extra page is built")

                    ep_todo = False
            if papers_todo:
                out_papers = subprocess.check_output(split(py_man_papers)).decode(
                    "utf-8"
                )
                if "All papers are now built" in out_papers:
                    print("Papers are now built.")
                    papers_todo = False
            if papers_todo or ep_todo:
                print("Still waiting for pdf production tasks. Sleeping.")
                sleep(1)
            else:
                print(
                    "Extra page and papers all built - continuing to next step of demo."
                )
                break

    def download_zip(self):
        print("Download a zip of all the papers")
        cmd = "plom_build_papers --download-all"
        py_man_cmd = f"python3 manage.py {cmd}"
        subprocess.check_call(split(py_man_cmd))

    def upload_bundles(self, number_of_bundles=3, homework_bundles={}):
        bundle_names = [f"fake_bundle{n+1}.pdf" for n in range(number_of_bundles)]
        # these will be messed with before upload via the --demo toggle
        for bname in bundle_names:
            cmd = f"plom_staging_bundles upload demoScanner{1} {bname} --demo"
            py_man_cmd = f"python3 manage.py {cmd}"
            subprocess.check_call(split(py_man_cmd))
            sleep(0.2)
        # we don't want to mess with these - just upload them
        for bundle in homework_bundles:
            paper_number = bundle["paper_number"]
            bundle_name = f"fake_hw_bundle_{paper_number}.pdf"
            cmd = f"plom_staging_bundles upload demoScanner{1} {bundle_name}"
            py_man_cmd = f"python3 manage.py {cmd}"
            subprocess.check_call(split(py_man_cmd))
            sleep(0.2)

    def wait_for_upload(self, number_of_bundles=3, homework_bundles={}):
        bundle_names = [f"fake_bundle{n+1}" for n in range(number_of_bundles)]
        for paper_number in homework_bundles:
            bundle_names.append(f"fake_hw_bundle_{paper_number}")

        for bname in bundle_names:
            cmd = f"plom_staging_bundles status {bname}"
            py_man_cmd = f"python3 manage.py {cmd}"
            while True:
                out = subprocess.check_output(split(py_man_cmd)).decode("utf-8")
                if "qr-codes not yet read" in out:
                    print(f"{bname} ready for qr-reading")
                    break
                else:
                    print(out)
                sleep(0.5)

    def read_qr_codes(self, number_of_bundles=3):
        for n in range(1, number_of_bundles + 1):
            cmd = f"plom_staging_bundles read_qr fake_bundle{n}"
            py_man_cmd = f"python3 manage.py {cmd}"
            subprocess.check_call(split(py_man_cmd))
            sleep(0.5)

    def wait_for_qr_read(self, number_of_bundles=3):
        for n in range(1, number_of_bundles + 1):
            cmd = f"plom_staging_bundles status fake_bundle{n}"
            py_man_cmd = f"python3 manage.py {cmd}"
            while True:
                out = subprocess.check_output(split(py_man_cmd)).decode("utf-8")
                if "qr-codes not yet read" in out:
                    print(f"fake_bundle{n}.pdf still being read")
                    print(out)
                    sleep(0.5)
                else:
                    print(f"fake_bundle{n}.pdf has been read")
                    return

    def push_if_ready(self, number_of_bundles=3, homework_bundles=[], attempts=15):
        print(
            "Try to push all bundles - some will fail since they are not yet ready, or contain unknowns/errors etc"
        )
        todo = [f"fake_bundle{k+1}" for k in range(number_of_bundles)]
        for bundles in homework_bundles:
            paper_number = bundles["paper_number"]
            todo.append(f"fake_hw_bundle_{paper_number}")

        while True:
            done = []
            for bundle in todo:
                cmd = f"plom_staging_bundles status {bundle}"
                py_man_cmd = f"python3 manage.py {cmd}"
                out_stat = subprocess.check_output(
                    split(py_man_cmd), stderr=subprocess.STDOUT
                ).decode("utf-8")
                if "perfect" in out_stat:
                    push_cmd = f"python3 manage.py plom_staging_bundles push {bundle}"
                    subprocess.check_call(split(push_cmd))
                    done.append(bundle)
                    sleep(1)
                elif "cannot push" in out_stat:
                    print(
                        f"Cannot push {bundle} because it contains unknowns or errors"
                    )
                    done.append(bundle)

            for bundle in done:
                todo.remove(bundle)
            if len(todo) > 0 and attempts > 0:
                print(
                    f"Still waiting for bundles {todo} to process - sleep between attempts"
                )
                attempts -= 1
                sleep(1)
            else:
                print("All bundles pushed.")
                break

    def create_rubrics(self):
        call_command("plom_rubrics", "init")
        call_command("plom_rubrics", "push", "--demo")

    def map_extra_pages(self, config):
        """Map extra pages that are in otherwise fully fixed-page bundles."""
        caster = ScanCastService()
        if "bundles" not in config.keys():
            return

        bundles = config["bundles"]
        n_bundles = len(bundles)

        for i in range(n_bundles):
            bundle = bundles[i]
            bundle_slug = f"fake_bundle{i+1}"
            if "extra_page_papers" in bundle.keys():
                extra_page_papers = bundle["extra_page_papers"]
                extra_pages = ExtraStagingImage.objects.filter(
                    staging_image__bundle__slug=bundle_slug,
                ).order_by("staging_image__bundle_order")

                n_questions = SpecificationService().get_n_questions()

                for i in range(len(extra_page_papers)):
                    paper_extra_pages = extra_pages[i * 2 : i * 2 + 2]

                    # command must be called twice, since the demo generates double extra pages
                    for page in paper_extra_pages:
                        call_command(
                            "plom_staging_assign_extra",
                            "assign",
                            "demoScanner1",
                            bundle_slug,
                            "-i",
                            page.staging_image.bundle_order,
                            "-t",
                            extra_page_papers[i],
                            "-q",
                            n_questions,  # default to last question
                        )
