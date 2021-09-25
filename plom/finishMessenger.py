# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2020-2021 Andrew Rechnitzer
# Copyright (C) 2020-2021 Colin B. Macdonald

from io import BytesIO
import urllib3

import requests

from plom.plom_exceptions import PlomSeriousException, PlomAuthenticationException
from plom.baseMessenger import BaseMessenger

# TODO: how to do this in subclass?
# TODO: set username method?
# _userName = "manager"

# ----------------------


class FinishMessenger(BaseMessenger):
    """Finishing-related communications."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def RgetCompletionStatus(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/REP/completionStatus",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return response.json()

    def RgetOutToDo(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/REP/outToDo",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return response.json()

    def RgetSpreadsheet(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/REP/spreadSheet",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return response.json()

    def RgetIdentified(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/REP/identified",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
            rval = response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return rval

    def RgetCompletions(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/REP/completions",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
            rval = response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return rval

    def RgetCoverPageInfo(self, test):
        self.SRmutex.acquire()
        try:
            response = self.get(
                f"/REP/coverPageInfo/{test}",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
            rval = response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return rval

    def RgetOriginalFiles(self, testNumber):
        self.SRmutex.acquire()
        try:
            response = self.get(
                f"/REP/originalFiles/{testNumber}",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return response.json()

    def MgetAllMax(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/MK/allMax",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return response.json()

    def getSolutionStatus(self):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/REP/solutions",
                json={"user": self.user, "token": self.token},
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return response.json()

    def getSolutionImage(self, question, version):
        self.SRmutex.acquire()
        try:
            response = self.get(
                "/MK/solution",
                json={
                    "user": self.user,
                    "token": self.token,
                    "question": question,
                    "version": version,
                },
            )
            response.raise_for_status()
            if response.status_code == 204:
                raise PlomNoSolutionException(
                    "No solution for {}.{} uploaded".format(question, version)
                ) from None

            img = BytesIO(response.content).getvalue()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()
        return img
