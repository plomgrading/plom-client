# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Edith Coates

import os
import subprocess
from time import sleep
from shlex import split

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from Demo.services import (
    DemoProcessesService,
    DemoCreationService,
    DemoBundleService,
    DemoHWBundleService,
    ServerConfigService,
)


class Command(BaseCommand):
    help = "WebPlom demo. For testing, debugging and development."

    def papers_and_db(self, dcs: DemoCreationService):
        print("*" * 40)
        dcs.build_db_and_papers()
        dcs.wait_for_papers_to_be_ready()

        print("*" * 40)
        dcs.download_zip()

    def create_bundles(
        self,
        dbs: DemoBundleService,
        dhs: DemoHWBundleService,
        config: dict,
        homework_bundles,
    ):
        if ServerConfigService().contains_key(config, "bundles"):
            dbs.scribble_on_exams(config)

        for bundle in homework_bundles:
            dhs.make_hw_bundle(bundle)

    def upload_bundles(
        self, dcs: DemoCreationService, number_of_bundles, homework_bundles
    ):
        print("*" * 40)
        dcs.upload_bundles(
            number_of_bundles=number_of_bundles, homework_bundles=homework_bundles
        )

        dcs.wait_for_upload(
            number_of_bundles=number_of_bundles,
        )

    def read_bundles(
        self,
        dcs: DemoCreationService,
        dhs: DemoHWBundleService,
        config: dict,
        number_of_bundles,
        homework_bundles,
    ):
        print("*" * 40)
        dcs.read_qr_codes(
            number_of_bundles=number_of_bundles,
        )
        dhs.map_homework_pages(homework_bundles=homework_bundles)

        print("*" * 40)
        dcs.wait_for_qr_read(
            number_of_bundles=number_of_bundles,
        )

        dcs.map_extra_pages(config)

    def push_bundles(
        self, dcs: DemoCreationService, number_of_bundles, homework_bundles
    ):
        print("*" * 40)
        dcs.push_if_ready(
            number_of_bundles=number_of_bundles, homework_bundles=homework_bundles
        )

    def post_server_init(self, dcs: DemoCreationService, config: dict, stop_at: str):
        self.papers_and_db(dcs)

        print("*" * 40)
        scs = ServerConfigService()
        if scs.contains_key(config, "bundles"):
            number_of_bundles = len(config["bundles"])
            bundle_service = DemoBundleService()
        else:
            bundle_service = None
            number_of_bundles = 0

        if scs.contains_key(config, "hw_bundles"):
            homework_bundles = config["hw_bundles"]
            homework_service = DemoHWBundleService()
        else:
            homework_bundles = []
            homework_service = None

        if bundle_service is None and homework_service is None:
            print("No bundles detected - stopping.")
            return

        self.create_bundles(bundle_service, homework_service, config, homework_bundles)

        self.upload_bundles(dcs, number_of_bundles, homework_bundles)
        if stop_at == "bundles_uploaded":
            return

        self.read_bundles(
            dcs, homework_service, config, number_of_bundles, homework_bundles
        )
        if stop_at == "bundles_read":
            return

        self.push_bundles(dcs, number_of_bundles, homework_bundles)
        if stop_at == "bundles_pushed":
            return

        print("*" * 40)
        dcs.create_rubrics()

    def run_randomarker(self):
        # TODO: hardcoded port numbers!
        cmd = "python3 -m plom.client.randoMarker -s localhost:8000 -u demoMarker1 -w demoMarker1"
        print(f"RandoMarking!  calling: {cmd}")
        subprocess.check_call(split(cmd), env=dict(os.environ, WEBPLOM="1"))
        cmd = "python3 -m plom.client.randoIDer -s localhost:8000 -u demoMarker1 -w demoMarker1"
        print(f"RandoIDing!  calling: {cmd}")
        subprocess.check_call(split(cmd), env=dict(os.environ, WEBPLOM="1"))

    def wait_for_exit(self):
        while True:
            x = input("Type 'quit' and press Enter to exit the demo: ")
            if x.casefold() == "quit":
                break

    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            action="store",
            nargs=1,
            help="Use a TOML config file for creating the demo exam structure.",
        )
        parser.add_argument(
            "--no-waiting",
            action="store_true",
            help="Do not wait for user input at the end of the demo sequence before stopping the demo.",
        )
        parser.add_argument(
            "--stop-at",
            action="store",
            choices=[
                "migrations",
                "users",
                "preparation",
                "bundles-uploaded",
                "bundles-read",
                "bundles-pushed",
            ],
            nargs=1,
            help="Stop the demo sequence at a certain breakpoint.",
        )
        parser.add_argument(
            "--randomarker",
            action="store_true",
            help="Run the plom-client randomarker.",
        )

    def handle(self, *args, **options):
        stop_at = options["stop_at"]
        if stop_at is not None:
            stop_at = stop_at[0]
            if options["randomarker"]:
                raise CommandError(
                    "Cannot run plom-client randomarker with a demo breakpoint."
                )

        config_path = options["config"]
        config_service = ServerConfigService()
        if config_path is None:
            config = config_service.read_server_config(
                settings.BASE_DIR / "Demo/config_files/full_demo_config.toml"
            )
        else:
            try:
                config = config_service.read_server_config(config_path[0])
            except Exception as e:
                raise CommandError(e)
        print(config)

        proc_service = DemoProcessesService()
        proc_service.initialize_server_and_db()

        if stop_at == "migrate":
            return

        print("*" * 40)
        huey_worker_proc = proc_service.launch_huey_workers()

        creation_service = DemoCreationService()
        print("*" * 40)
        creation_service.make_groups_and_users()

        if stop_at == "users":
            huey_worker_proc.terminate()
            return

        # TODO: I get errors if I move this after launching the server...
        print("*" * 40)
        creation_service.prepare_assessment(config)

        if stop_at == "preparation" or not config_service.contains_key(config, "num_to_produce"):
            huey_worker_proc.terminate()
            return

        print("*" * 40)
        server_proc = proc_service.launch_server()

        try:  # We're guaranteed to hit the cleanup code in the "finally" block
            self.post_server_init(creation_service, config, stop_at)

            if options["randomarker"]:
                self.run_randomarker()

            if not options["no_waiting"]:
                sleep(2)
                print("*" * 72)
                self.wait_for_exit()
            sleep(0.1)
            print("v" * 40)
        finally:
            huey_worker_proc.terminate()
            server_proc.terminate()
