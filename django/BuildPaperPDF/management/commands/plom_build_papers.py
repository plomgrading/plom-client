# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Colin B. Macdonald

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from BuildPaperPDF.services import BuildPapersService
from Preparation.services import PQVMappingService
from Papers.services import SpecificationService
from SpecCreator.services import StagingSpecificationService

from plom.misc_utils import format_int_list_with_runs


class Command(BaseCommand):
    help = "Allows user to build papers, download them and delete them."

    def add_arguments(self, parser):
        grp = parser.add_mutually_exclusive_group()
        grp.add_argument(
            "--start",
            type=int,
            metavar="N",
            help="Start building a specific test paper in the queue",
        )
        grp.add_argument(
            "--start-all",
            action="store_true",
            help="Start building all papers in the queue",
        )
        grp.add_argument(
            "--status",
            action="store_true",
            help="Show status of all test paper build tasks",
        )
        grp.add_argument(
            "--delete-all",
            action="store_true",
            help="Delete all PDFs that have been built",
        )
        grp.add_argument(
            "--cancel-all",
            action="store_true",
            help="Cancel any incomplete but queued build tasks",
        )
        grp.add_argument(
            "--download",
            type=int,
            metavar="N",
            help="Download a specific test paper as a PDF file",
        )
        grp.add_argument(
            "--download-all",
            action="store_true",
            help="Download all papers in a ZIP file",
        )

    def start_all_tasks(self):
        bp_service = BuildPapersService()
        if bp_service.get_n_tasks() == 0:
            self.stdout.write(
                "There are no tasks to start. Check that DB is populated."
            )
            return

        spec = SpecificationService().get_the_spec()
        pqv_service = PQVMappingService()
        qvmap = pqv_service.get_pqv_map_dict()

        bp_service.send_all_tasks(spec, qvmap)
        self.stdout.write(f"Started building {len(qvmap)} papers.")

    def start_specific_task(self, paper_number):
        bp_service = BuildPapersService()
        spec = SpecificationService().get_the_spec()
        pqv_service = PQVMappingService()
        qvmap = pqv_service.get_pqv_map_dict()

        if paper_number in qvmap:
            bp_service.send_single_task(paper_number, spec, qvmap[paper_number])
            self.stdout.write(f"Started building paper number {paper_number}.")
        else:
            self.stderr.write(
                f"Paper number {paper_number} is not in the question-version map."
            )

    def show_task_status(self):
        bp_service = BuildPapersService()
        # is a list of (paper_number, status)
        stats = bp_service.get_all_task_status()
        if len(stats):
            self.stdout.write(f"{len(stats)} tasks total:")
            rev_stat = {}
            for n, state in stats.items():
                rev_stat.setdefault(state, []).append(n)
            for state, papers in rev_stat.items():
                self.stdout.write(f' * "{state}": {format_int_list_with_runs(papers)}')
            if len(rev_stat.get("complete", [])) == len(stats):
                self.stdout.write("All papers are now built")
        else:
            self.stdout.write("No queued tasks.")

    def delete_all_tasks(self):
        bp_service = BuildPapersService()
        bp_service.reset_all_tasks()

    def cancel_all_tasks(self):
        bp_service = BuildPapersService()
        bp_service.cancel_all_task()

    def download_specific_paper(self, paper_number):
        bp_service = BuildPapersService()
        try:
            (name, b) = bp_service.get_paper_path_and_bytes(paper_number)
        except ValueError as err:
            self.stderr.write(f"Error - {err}")
            raise CommandError(err)

        with open(Path(name), "wb") as fh:
            fh.write(b)
        self.stdout.write(f'Saved paper {paper_number} as "{name}"')

    def download_all_papers(self):
        bps = BuildPapersService()
        short_name = StagingSpecificationService().get_short_name_slug()
        zgen = bps.get_zipfly_generator(short_name)
        with open(f"{short_name}.zip", "wb") as fh:
            self.stdout.write(f"Opening {short_name}.zip to write the zip-file")
            tot_size = 0
            for index, chunk in enumerate(zgen):
                tot_size += len(chunk)
                fh.write(chunk)
                self.stdout.write(
                    f"# chunk {index} = {tot_size//(1024*1024)}mb", ending="\r"
                )
        self.stdout.write(f'\nAll built papers saved in zip = "{short_name}.zip"')

    def handle(self, *args, **options):
        if options["start"]:
            self.start_specific_task(options["start"])
        elif options["download"]:
            self.download_specific_paper(options["download"])
        elif options["download_all"]:
            self.download_all_papers()
        elif options["start_all"]:
            self.start_all_tasks()
        elif options["delete_all"]:
            self.delete_all_tasks()
        elif options["cancel_all"]:
            self.cancel_all_tasks()
        elif options["status"]:
            self.show_task_status()
        else:
            self.print_help("manage.py", "plom_build_papers")
