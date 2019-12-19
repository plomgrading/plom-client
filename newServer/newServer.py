__author__ = "Andrew Rechnitzer"
__copyright__ = "Copyright (C) 2019 Andrew Rechnitzer"
__credits__ = ["Andrew Rechnitzer", "Colin Macdonald"]
__license__ = "AGPLv3"

# TODO - directory structure!

# ----------------------

from aiohttp import web
import hashlib
import json
import os
import ssl
import sys
import uuid

# ----------------------

from authenticate import Authority

# this allows us to import from ../resources
sys.path.append("..")
from resources.specParser import SpecParser
from resources.examDB import *

# ----------------------

serverInfo = {"server": "127.0.0.1", "mport": 41984}
# ----------------------
sslContext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
sslContext.check_hostname = False
sslContext.load_cert_chain("../resources/mlp-selfsigned.crt", "../resources/mlp.key")


from plomServer.routesUpload import UploadHandler

# ----------------------
def buildDirectories(spec):
    """Build the directories that this script needs"""
    # the list of directories. Might need updating.
    lst = [
        "pages",
        "pages/discardedPages",
        "pages/duplicatePages",
        "pages/collidingPages",
        "pages/originalPages",
    ]
    for dir in lst:
        try:
            os.mkdir(dir)
        except FileExistsError:
            pass


# ----------------------


class Server(object):
    def __init__(self, spec, db):
        self.testSpec = spec
        self.DB = db
        self.loadUsers()

    def loadUsers(self):
        """Load the users from json file, add them to the authority which
        handles authentication for us.
        """
        if os.path.exists("../resources/userList.json"):
            with open("../resources/userList.json") as data_file:
                # Load the users and pass them to the authority.
                self.userList = json.load(data_file)
                self.authority = Authority(self.userList)
        else:
            # Cannot find users - give error and quit out.
            print("Where is user/password file?")
            quit()

    from plomServer.serverUpload import addKnownPage, addUnknownPage, addCollidingPage


examDB = PlomDB()
spec = SpecParser().spec
buildDirectories(spec)
peon = Server(spec, examDB)
uploader = UploadHandler(peon)

try:
    # Run the server
    app = web.Application()
    uploader.setUpRoutes(app.router)
    web.run_app(app, ssl_context=sslContext, port=serverInfo["mport"])
except KeyboardInterrupt:
    pass
