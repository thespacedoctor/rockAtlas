import os
import nose
import shutil
import yaml
import unittest
from rockAtlas import database, cl_utils
from rockAtlas.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="rockAtlas"
)
arguments, settings, log, dbConn = su.setup()

# # load settings
# stream = file(
#     "/Users/Dave/.config/rockAtlas/rockAtlas.yaml", 'r')
# settings = yaml.load(stream)
# stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

# load settings
stream = file(
    pathToInputDir + "/example_settings.yaml", 'r')
settings = yaml.load(stream)
stream.close()

import shutil
try:
    shutil.rmtree(pathToOutputDir)
except:
    pass
# COPY INPUT TO OUTPUT DIR
shutil.copytree(pathToInputDir, pathToOutputDir)

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)

# xt-setup-unit-testing-files-and-folders


class test_database(unittest.TestCase):

    def test_tunnel(self):

        from rockAtlas import database
        db = database(
            log=log,
            settings=settings
        )
        sshPort = db._setup_tunnel(
            tunnelParameters=settings["database settings"][
                "atlas3"]["tunnel"]
        )

        return

    def test_database_function(self):

        # SETUP ALL DATABASE CONNECTIONS
        from rockAtlas import database
        db = database(
            log=log,
            settings=settings
        )
        dbConns, dbVersions = db.connect()
        self.atlas3DbConn = dbConns["atlas3"]
        self.atlas4DbConn = dbConns["atlas4"]
        self.atlasMoversDbConn = dbConns["atlasMovers"]

        from fundamentals.mysql import readquery
        sqlQuery = u"""
            SELECT VERSION();
        """ % locals()
        rows = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=self.atlas3DbConn,
            quiet=False
        )
        print rows
        rows = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=self.atlas4DbConn,
            quiet=False
        )
        print rows
        rows = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDbConn,
            quiet=False
        )
        print rows

    def test_database_function_exception(self):

        from rockAtlas import database
        try:
            this = database(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
