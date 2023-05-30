# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Edith Coates

import os
import shutil
import subprocess
from shlex import split
from pathlib import Path

from django.core.management import call_command
from django.conf import settings


class DemoProcessesService:
    """Handle starting and stopping the server and the Huey background process."""

    def setup_django(self):
        from django import setup

        """Setup the django server and apply settings.py."""
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Web_Plom.settings")
        setup()

    def get_database_engine(self):
        """Which database engine are we using?"""
        from Web_Plom import settings

        engine = settings.DATABASES["default"]["ENGINE"]
        if "postgres" in engine:
            return "postgres"
        elif "sqlite" in engine:
            return "sqlite"
        else:
            return "unknown"
        # TODO = get this working with mysql too

    def recreate_postgres_db(self):
        import psycopg2

        # use local "socket" thing
        # conn = psycopg2.connect(user="postgres", password="postgres")
        # use TCP/IP
        host = settings.DATABASES["postgres"]["HOST"]
        conn = psycopg2.connect(user="postgres", password="postgres", host=host)

        conn.autocommit = True
        print("Removing old database.")
        try:
            with conn.cursor() as curs:
                curs.execute("DROP DATABASE plom_db;")
        except psycopg2.errors.InvalidCatalogName:
            print("No database 'plom_db' - continuing")

        print("Creating database 'plom_db'")
        try:
            with conn.cursor() as curs:
                curs.execute("CREATE DATABASE plom_db;")
        except psycopg2.errors.DuplicateDatabase:
            with conn.cursor() as curs:
                print("We should not reach here.")
                quit()
        conn.close()

    def remove_old_db_and_misc_user_files(self, engine):
        print("Removing old DB and any misc user-generated files")

        if engine == "sqlite":
            Path("db.sqlite3").unlink(missing_ok=True)
        elif engine == "postgres":
            self.recreate_postgres_db()
        else:
            raise RuntimeError('Unexpected engine "{engine}"')

        for fname in [
            "fake_bundle1.pdf",
            "fake_bundle2.pdf",
            "fake_bundle3.pdf",
        ]:
            Path(fname).unlink(missing_ok=True)

        for path in Path("huey").glob("huey_db.*"):
            path.unlink(missing_ok=True)

        for rmdir in ["sourceVersions", "papersToPrint", "media", "fixtures"]:
            shutil.rmtree(rmdir, ignore_errors=True)

        Path("media").mkdir()

    def sqlite_set_wal(self):
        import sqlite3

        print("Setting journal mode WAL for sqlite database")
        conn = sqlite3.connect("db.sqlite3")
        conn.execute("pragma journal_mode=wal")
        conn.close()

    def rebuild_migrations_and_migrate(self, engine):
        # print("Rebuild the database migrations and migrate")
        # for cmd in ["makemigrations", "migrate"]:
        # py_man_cmd = f"python3 manage.py {cmd}"
        # subprocess.check_call(split(py_man_cmd))

        call_command("makemigrations")
        call_command("migrate")

        if engine == "sqlite":
            sqlite_set_wal()

    def launch_huey_workers(self):
        # I don't understand why, but this seems to need to be run as a sub-proc
        # and not via call_command... maybe because it launches a bunch of background
        # stuff?

        print("Launching huey workers for background tasks")
        for cmd in ["djangohuey --quiet"]:  # quiet huey tasks.
            py_man_cmd = f"python3 manage.py {cmd}"
            return subprocess.Popen(split(py_man_cmd))

    def launch_server(self):
        print("Launching django server")
        # this needs to be run in the background
        cmd = "python3 manage.py runserver 8000"
        return subprocess.Popen(split(cmd))

    def remove_old_migration_files(self):
        print("Avoid perplexing errors by removing autogen migration droppings")

        for path in Path(".").glob("*/migrations/*.py"):
            if path.name == "__init__.py":
                continue
            else:
                print(f"Removing {path}")
                path.unlink(missing_ok=True)

    def initialize_server_and_db(self):
        """Configure Django settings and flush the previous database and media files."""
        self.setup_django()

        engine = self.get_database_engine()
        print(f"You appear to be running with a {engine} database.")

        print("*" * 40)
        if engine == "postgres":
            self.recreate_postgres_db()

        print("*" * 40)
        self.remove_old_migration_files()

        print("*" * 40)
        self.remove_old_db_and_misc_user_files(engine)

        print("*" * 40)
        self.rebuild_migrations_and_migrate(engine)
