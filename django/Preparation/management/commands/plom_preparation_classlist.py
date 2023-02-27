# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Andrew Rechnitzer
# Copyright (C) 2022 Natalie Balashov
# Copyright (C) 2023 Colin B. Macdonald


from django.core.management.base import BaseCommand

from Preparation.services import (
    StagingClasslistCSVService,
    StagingStudentService,
    PrenameSettingService,
)

from pathlib import Path


class Command(BaseCommand):
    help = "Displays the current status of the classlist, and allows user upload/download/remove it."

    def show_status(self):
        sss = StagingStudentService()
        n = sss.how_many_students()
        if n:
            self.stdout.write(f"A classlist with {n} students is on the server.")
        else:
            self.stdout.write("There is no classlist on the server.")

    def upload_classlist(self, source_csv, ignore_warnings=False):
        sss = StagingStudentService()

        if sss.are_there_students():
            self.stderr.write("There is already a classlist on the server. Stopping.")
            return
        source_path = Path(source_csv)
        if not source_path.exists():
            self.stderr.write(f"Cannot open {source_csv}. Stopping.")

        scsv = StagingClasslistCSVService()
        with open(source_path, "rb") as fh:
            success, warnings = scsv.take_classlist_from_upload(fh)
        if success and not warnings:
            self.stdout.write("Upload has no warnings.")
            sss.use_classlist_csv()
            self.stdout.write("CSV processed.")
            return
        elif success and warnings:
            self.stderr.write("Upload failed - there are warnings:")
            for werr in warnings:
                self.stdout.write(
                    f" * {werr['warn_or_err']} on line {werr['werr_line']} = {werr['werr_text']} "
                )
            if ignore_warnings:
                self.stdout.write(
                    "Ignoring these warnings and using this classlist csv."
                )
                sss.use_classlist_csv()
                self.stdout.write("CSV processed.")
                return
            else:
                self.stdout.write("Stopping.")
                return
        else:
            self.stdout.write("Upload failed - there are warnings and errors")
            for werr in warnings:
                self.stdout.write(
                    f" * {werr['warn_or_err']} on line {werr['werr_line']} = {werr['werr_text']} "
                )
            return

    def download_classlist(self, dest_csv):
        sss = StagingStudentService()
        pss = PrenameSettingService()

        if not sss.are_there_students():
            self.stderr.write("There is no classlist on the server.")
            return
        self.stdout.write(f"Downloading classlist to '{dest_csv}'")
        prename = pss.get_prenaming_setting()
        if prename:
            self.stdout.write("\tPrenaming is enabled, so saving 'paper_number' column")
        else:
            self.stdout.write(
                "\tPrenaming is disabled, so ignoring 'paper_number' column"
            )

        save_path = Path(dest_csv)
        if save_path.exists():
            self.stdout.write(f"A file exists at {save_path} - overwrite it? [y/N]")
            choice = input().lower()
            if choice != "y":
                self.stdout.write("Skipping.")
                return
            else:
                self.stdout.write(f"Overwriting {save_path}.")
        csv_text = sss.get_students_as_csv_string(prename=prename)
        with open(save_path, "w") as fh:
            fh.write(csv_text)

    def remove_classlist(self):
        sss = StagingStudentService()
        if sss.are_there_students():
            self.stdout.write("Removing classlist from the server")
            sss.remove_all_students()
            return
        else:
            self.stderr.write("There is no classlist on the server.")
            return

    def add_arguments(self, parser):
        sub = parser.add_subparsers(
            dest="command",
            description="Perform tasks related to uploading/downloading/deleting of a classlist.",
        )
        sub.add_parser("status", help="Show details of uploaded classlist")
        sp_U = sub.add_parser("upload", help="Upload a classlist csv")
        sp_D = sub.add_parser("download", help="Download the current classlist")

        sub.add_parser("remove", help="Remove the classlist from the server")

        sp_U.add_argument("source_csv", type=str, help="The classlist csv to upload")
        sp_U.add_argument(
            "--ignore-warnings",
            action="store_true",
            help="Use classlist csv even if there are warnings (not recommended).",
        )
        sp_D.add_argument(
            "dest_csv",
            nargs="?",
            type=str,
            help="Where to download to, defaults to 'classlist.csv'",
            default="classlist.csv",
        )

    def handle(self, *args, **options):
        if options["command"] == "status":
            self.show_status()
        elif options["command"] == "upload":
            self.upload_classlist(
                source_csv=options["source_csv"],
                ignore_warnings=options["ignore_warnings"],
            )
        elif options["command"] == "download":
            self.download_classlist(options["dest_csv"])
        elif options["command"] == "remove":
            self.remove_classlist()
        else:
            self.print_help("manage.py", "plom_preparation_classlist")
