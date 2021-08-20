# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020 Andrew Rechnitzer
# Copyright (C) 2020-2021 Colin B. Macdonald
# Copyright (C) 2021 Peter Lee

from stdiomask import getpass

from plom.messenger import ScanMessenger


def clearLogin(server=None, password=None):
    if server and ":" in server:
        s, p = server.split(":")
        scanMessenger = ScanMessenger(s, port=p)
    else:
        scanMessenger = ScanMessenger(server)
    scanMessenger.start()

    if not password:
        password = getpass("Please enter the 'scanner' password: ")

    try:
        scanMessenger.clearAuthorisation("scanner", password)
        print("Scanner login cleared.")
    finally:
        scanMessenger.stop()
