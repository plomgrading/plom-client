# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Brennen Chiu
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Natalie Balashov

from datetime import datetime
import hashlib
import pathlib

import fitz
from tabulate import tabulate
from django.utils import timezone
from django.utils.text import slugify
from django.core.management.base import BaseCommand, CommandError

from Scan.services import ScanService


class Command(BaseCommand):
    """Management command that contains several subcommands.

    python3 manage.py plom_staging_bundles upload (username) (file) <- drag and drop or copy path
    python3 manage.py plom_staging_bundles status
    python3 manage.py plom_staging_bundles read_qr (bundle name) <- can get it from status
    python3 manage.py plom_staging_bundles push (bundle name) (username) <- can get it from status
    python3 manage.py plom_staging_bundles pages bundle name
    """

    help = "Upload bundle pdf files to staging area"

    def upload_pdf(self, username=None, source_pdf=None, *, debug_jpeg=False):
        scanner = ScanService()

        if source_pdf is None:
            raise CommandError("No bundle supplied.")

        try:
            with open(source_pdf, "rb") as f:
                file_bytes = f.read()
        except OSError as err:
            raise CommandError(err)

        try:
            pdf_doc = fitz.open(stream=file_bytes)
        except fitz.FileDataError as err:
            raise CommandError(err)

        filename_stem = pathlib.Path(source_pdf).stem
        slug = slugify(filename_stem)
        timestamp = datetime.timestamp(timezone.now())
        hashed = hashlib.sha256(file_bytes).hexdigest()
        number_of_pages = pdf_doc.page_count

        if scanner.check_for_duplicate_hash(hashed):
            raise CommandError("Upload failed - Bundle was already uploaded.")

        try:
            scanner.upload_bundle_cmd(
                source_pdf,
                slug,
                username,
                timestamp,
                hashed,
                number_of_pages,
                debug_jpeg=debug_jpeg,
            )
            self.stdout.write(
                f"Uploaded {source_pdf} as user {username} - processing it in the background now."
            )
        except ValueError as err:
            raise CommandError(err)

    def staging_bundle_status(self, bundle_name=None):
        scanner = ScanService()
        bundle_status = scanner.staging_bundle_status_cmd()
        if bundle_name is None:
            self.stdout.write(
                tabulate(bundle_status, headers="firstrow", tablefmt="simple_outline")
            )
            if len(bundle_status) == 1:
                self.stdout.write("No bundles uploaded.")
            return

        the_bundle = [X for X in bundle_status if X[0] == bundle_name]
        if len(the_bundle) == 0:
            raise CommandError(f"Bundle '{bundle_name}' not present.")
        if len(the_bundle) > 1:
            raise CommandError(f"Multiple bundles called '{bundle_name}' are present.")

        (
            pk,
            num_pages,
            unknown_pages,
            known_pages,
            extra_pages,
            discard_pages,
            error_pages,
            qr_processed,
            pushed,
            username,
        ) = the_bundle[0][1:]
        self.stdout.write(
            f"Found bundle '{bundle_name}' (id {pk}) with {num_pages} pages uploaded by {username}"
        )

        valid_pages = known_pages + extra_pages + discard_pages

        if isinstance(num_pages, str) and "progress" in num_pages:
            self.stdout.write(f"  * bundle still being split: {num_pages}")
            return
        if pushed is True:
            self.stdout.write("  * bundle has been pushed")
            return
        if qr_processed is not True:
            self.stdout.write("  * qr-codes not yet read")
            return
        if unknown_pages > 0:
            self.stdout.write("  * unknown pages present, cannot push.")
            return
        if error_pages > 0:
            self.stdout.write("  * error pages present, cannot push.")
            return
        if valid_pages != num_pages:
            self.stdout.write("  * invalid pages present, cannot push.")
            return
        if (
            (qr_processed is True)
            and (valid_pages == num_pages)
            and (error_pages == 0)
            and (pushed is not True)
        ):
            self.stdout.write("  *  bundle perfect, ready to push")

    def delete_staged_bundle(self, bundle_name):
        scanner = ScanService()
        try:
            scanner.remove_bundle(bundle_name)
        except ValueError as err:
            raise CommandError(err)
        self.stdout.write(f"Deleted {bundle_name}")

    def push_staged_bundle(self, bundle_name, username):
        scanner = ScanService()
        try:
            scanner.push_bundle_cmd(bundle_name, username)
            self.stdout.write(f"Bundle {bundle_name} - pushed from staging.")
        except ValueError as err:
            raise CommandError(err)

    def read_bundle_qr(self, bundle_name):
        scanner = ScanService()
        try:
            scanner.read_bundle_qr_cmd(bundle_name)
            self.stdout.write(
                f"Reading {bundle_name} QR codes - processing it in the background now."
            )
        except ValueError as err:
            raise CommandError(err)

    def show_bundle_pages(self, bundle_name, *, show="all"):
        # For the table construct a list of lists
        bundle_page_list = [["order", "status", "info", "rotation"]]

        scanner = ScanService()
        try:
            bundle_page_info_list = scanner.get_bundle_pages_info_cmd(bundle_name)
        except ValueError as err:
            raise CommandError(err)

        # Now for each entry in this data from the server, parse out the fields we want for the table.
        for page in bundle_page_info_list:
            dat = [page["order"], page["status"]]
            if page["status"] == "unknown":
                dat.append(" - ")
            elif page["status"] == "known":
                dat.append(
                    f"paper {page['info']['paper_number']}: p.{page['info']['page_number']} v.{page['info']['version']}"
                )
            elif page["status"] == "extra":
                if page["info"]["paper_number"] and page["info"]["question_list"]:
                    dat.append(
                        f"paper {page['info']['paper_number']}: q{page['info']['question_list']}"
                    )
                else:
                    dat.append("extra page without data")
            elif page["status"] in ["error", "discard"]:
                dat.append(page["info"]["reason"])
            else:
                raise CommandError(
                    "Expected page with status: known, unknown, extra, discard, error, but got {page['status']}"
                )

            dat.append(page["rotation"])

            # filter out required pages
            if show == "all" or page["status"] == show:
                bundle_page_list.append(dat)

        self.stdout.write(
            tabulate(bundle_page_list, headers="firstrow", tablefmt="simple_outline")
        )

    def add_arguments(self, parser):
        sp = parser.add_subparsers(
            dest="command",
            description="Upload PDF files.",
        )

        # Upload
        sp_upload = sp.add_parser("upload", help="Upload a test pdf.")
        sp_upload.add_argument(
            "username", type=str, help="Which username to upload as."
        )
        sp_upload.add_argument("source_pdf", type=str, help="The test pdf to upload.")
        sp_upload.add_argument(
            "--demo",
            action="store_true",
            help="""
                Make a mess of the input, using low-quality JPEGs, rotations, etc.
                Not for production.
            """,
        )

        # Status
        sp_stat = sp.add_parser(
            "status", help="Show the status of the staging bundles."
        )
        sp_stat.add_argument(
            "bundle_name",
            type=str,
            nargs="?",
            help="(optional) get status of specific bundle",
        )

        sp_del = sp.add_parser("delete", help="delete a bundle.")
        sp_del.add_argument("bundle_name", type=str, help="Which bundle to delete")

        # Push
        sp_push = sp.add_parser("push", help="Push the staged bundles.")
        sp_push.add_argument("bundle_name", type=str, help="Which bundle to push.")
        sp_push.add_argument(
            "username", type=str, help="Name of user who is pushing the bundle.",
        )

        # Read QR codes
        sp_read_qr = sp.add_parser("read_qr", help="Read the selected bundle QR codes.")
        sp_read_qr.add_argument(
            "bundle_name", type=str, help="Which bundle to read the QR codes."
        )
        # pages
        sp_page = sp.add_parser("pages", help="Show the pages within the given bundle.")
        sp_page.add_argument(
            "bundle_name",
            type=str,
            help="get status of pages within this bundle",
        )
        sp_page.add_argument(
            "--show",
            type=str,
            help="Show only pages with indicated status",
            choices=["all", "unknown", "known", "extra", "discard", "error"],
            default="all",
        )

    def handle(self, *args, **options):
        if options["command"] == "upload":
            self.upload_pdf(
                username=options["username"],
                source_pdf=options["source_pdf"],
                debug_jpeg=options["demo"],
            )
        elif options["command"] == "status":
            self.staging_bundle_status(bundle_name=options["bundle_name"])
        elif options["command"] == "delete":
            self.delete_staged_bundle(bundle_name=options["bundle_name"])
        elif options["command"] == "push":
            self.push_staged_bundle(
                bundle_name=options["bundle_name"],
                username=options["username"],
            )
        elif options["command"] == "read_qr":
            self.read_bundle_qr(bundle_name=options["bundle_name"])
        elif options["command"] == "pages":
            self.show_bundle_pages(
                bundle_name=options["bundle_name"], show=options["show"]
            )
        else:
            self.print_help("manage.py", "plom_staging_bundles")
