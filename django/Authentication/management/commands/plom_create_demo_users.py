# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Brennen Chiu
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2022-2023 Colin B. Macdonald

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from tabulate import tabulate


# -m to get number of scanners and markers
class Command(BaseCommand):
    """
    This is the command for "python manage.py plom_create_demo_users"
    It creates demo users such as 1 manager, 5 scanners and 5 markers.
    Then, add the users to their respective group.
    This command also prints a table with a list of the demo users and
    passwords.
    """

    def handle(self, *args, **options):
        # Check to see if there are any groups created
        exist_groups = [str(group) for group in Group.objects.all()]
        if not exist_groups:
            self.stderr.write(
                "\nNo groups created! Please run python manage.py plom_create_groups "
                "to create groups first before running this command!\n"
            )
        else:
            range_of_scanners_markers = 5
            admin_group = Group.objects.get(name="admin")
            manager_group = Group.objects.get(name="manager")
            marker_group = Group.objects.get(name="marker")
            scanner_group = Group.objects.get(name="scanner")
            demo_group = Group.objects.get(name="demo")
            exist_usernames = [str(username) for username in User.objects.all()]
            admin_info = {"Username": [], "Password": []}
            manager_info = {"Username": [], "Password": []}
            scanner_info = {"Username": [], "Password": []}
            marker_info = {"Username": [], "Password": []}
            email = "@example.com"

            admin = "demoAdmin"
            manager = "demoManager1"
            scanner = "demoScanner"
            marker = "demoMarker"

            # Here is to create a single demo admin user
            try:
                User.objects.create_superuser(
                    username=admin,
                    email=admin + email,
                    password="password",
                    is_staff=True,
                    is_superuser=True,
                ).groups.add(admin_group, demo_group)
                self.stdout.write(f"{admin} created and added to {admin_group} group!")

            except IntegrityError as err:
                self.stderr.write(f"{admin} already exists!")
                raise CommandError(err)
            except Group.DoesNotExist as err:
                self.stderr.write("Admin group {admin_group} does not exist.")
                raise CommandError(err)

            admin_info["Username"].append(admin)
            admin_info["Password"].append("password")

            # Here is to create a single demo manager user
            try:
                User.objects.create_user(
                    username=manager, email=manager + email, password=manager
                ).groups.add(manager_group, demo_group)
                self.stdout.write(
                    f"{manager} created and added to {manager_group} group!"
                )
                User.objects.create_user(
                    username="manager", email="manager" + email, password="1234"
                ).groups.add(manager_group, demo_group)
                self.stdout.write(
                    f"{manager} created and added to {manager_group} group!"
                )
            except IntegrityError as err:
                self.stderr.write(f"{manager} already exists!")
                raise CommandError(err)

            manager_info["Username"].append(manager)
            manager_info["Password"].append(manager)
            manager_info["Username"].append("manager")
            manager_info["Password"].append("1234")

            # Here is to create 5 scanners and markers
            for number_of_scanner_marker in range(1, range_of_scanners_markers + 1):
                scanner_username = scanner + str(number_of_scanner_marker)
                scanner_password = scanner_username
                scanner_info["Username"].append(scanner_username)
                scanner_info["Password"].append(scanner_password)

                marker_username = marker + str(number_of_scanner_marker)
                marker_password = marker_username
                marker_info["Username"].append(marker_username)
                marker_info["Password"].append(marker_password)

                if scanner_username in exist_usernames:
                    self.stderr.write(f"{scanner_username} already exists!")
                else:
                    User.objects.create_user(
                        username=scanner_username,
                        email=scanner_username + email,
                        password=scanner_password,
                    ).groups.add(scanner_group, demo_group)
                    user = User.objects.get(username=scanner_username)
                    user.is_active = True
                    user.save()

                    self.stdout.write(
                        f"{scanner_username} created and added to {scanner_group} group!"
                    )

                if marker_username in exist_usernames:
                    self.stderr.write(f"{marker_username} already exists!")
                else:
                    User.objects.create_user(
                        username=marker_username,
                        email=marker_username + email,
                        password=marker_password,
                    ).groups.add(marker_group, demo_group)
                    user = User.objects.get(username=marker_username)
                    user.is_active = True
                    user.save()

                    self.stdout.write(
                        f"{marker_username} created and added to {marker_group} group!"
                    )

            # Here is print the table of demo users
            self.stdout.write("\nAdmin table: demo admin usernames and passwords")
            self.stdout.write(
                str(tabulate(admin_info, headers="keys", tablefmt="fancy_grid"))
            )

            self.stdout.write("\nManager table: demo manager usernames and passwords")
            self.stdout.write(
                str(tabulate(manager_info, headers="keys", tablefmt="fancy_grid"))
            )

            self.stdout.write("\nScanner table: demo scanner usernames and passwords")
            self.stdout.write(
                str(tabulate(scanner_info, headers="keys", tablefmt="fancy_grid"))
            )

            self.stdout.write("\nMarker table: demo marker usernames and passwords")
            self.stdout.write(
                str(tabulate(marker_info, headers="keys", tablefmt="fancy_grid"))
            )
