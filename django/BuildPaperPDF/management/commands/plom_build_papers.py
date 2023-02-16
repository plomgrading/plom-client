# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Andrew Rechnitzer

from django.core.management.base import BaseCommand

from BuildPaperPDF.services import BuildPapersService
from Preparation.services import PQVMappingService, StagingStudentService
from Papers.services import SpecificationService

from plom.misc_utils import format_int_list_with_runs


class Command(BaseCommand):
    help = (
        "Allows user to enqueue building of test papers, download them and delete them."
    )

    def add_arguments(self, parser):
        grp = parser.add_mutually_exclusive_group()
        grp.add_argument(
            "--enqueue",
            action="store_true",
            help="Enqueue the building of the test papers",
        )
        grp.add_argument(
            "--start",
            nargs=1,
            type=int,
            action="store",
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
            help="Delete all paper build tasks (incomplete and complete) in the queue",
        )
        grp.add_argument(
            "--cancel-all",
            action="store_true",
            help="Cancel any incomplete but queued build tasks",
        )

    def enqueue_tasks(self):
        bp_service = BuildPapersService()
        n_tasks = bp_service.get_n_tasks()
        if n_tasks > 0:
            self.stdout.write(f"Already enqueued {n_tasks} papers.")
            return

        pqv_service = PQVMappingService()
        num_pdfs = len(pqv_service.get_pqv_map_dict())

        sstu_service = StagingStudentService()
        classdict = sstu_service.get_classdict()

        bp_service.clear_tasks()
        bp_service.stage_pdf_jobs(num_pdfs, classdict=classdict)
        self.stdout.write(f"Enqueued the building of {num_pdfs} papers.")

    def start_all_tasks(self):
        bp_service = BuildPapersService()
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
            self.stdout.write(f"{len(stats)} tasks.")
            rev_stat = {}
            for (n, state) in stats.items():
                rev_stat.setdefault(state, []).append(n)
            for (state, papers) in rev_stat.items():
                self.stdout.write(f"{state} = {format_int_list_with_runs(papers)}")
        else:
            self.stdout.write("No queued tasks.")
            
    def delete_all_tasks(self):
        bp_service = BuildPapersService()
        bp_service.delete_all_task()

    def cancel_all_tasks(self):
        bp_service = BuildPapersService()
        bp_service.cancel_all_task()
        
    def handle(self, *args, **options):

        if options["enqueue"]:
            self.enqueue_tasks()
        elif options["start"]:
            self.start_specific_task(options["start"][0])
        elif options["start_all"]:
            self.start_all_tasks()
        elif options["delete_all"]:
            self.delete_all_tasks()
        elif options["cancel_all"]:
            self.cancel_all_tasks()
        elif options["status"]:
            self.show_task_status()
        else:
            self.stdout.write("pass")
