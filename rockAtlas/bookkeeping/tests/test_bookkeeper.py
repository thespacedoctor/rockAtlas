import os
import nose2
import shutil
import unittest
import yaml
from rockAtlas.bookkeeping import bookkeeper
from rockAtlas.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="rockAtlas",
    defaultSettingsFile=False
)
arguments, settings, log, dbConn = su.setup()

# # load settings
stream = file(
    "/Users/Dave/.config/rockAtlas/rockAtlas.yaml", 'r')
settings = yaml.load(stream)
stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

# load settings
# stream = file(
#     pathToInputDir + "/example_settings.yaml", 'r')
# settings = yaml.load(stream)
# stream.close()

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


class test_bookkeeper(unittest.TestCase):

    def test_bookkeeper_function(self):

        from rockAtlas.bookkeeping import bookkeeper
        this = bookkeeper(
            log=log,
            settings=settings
        )
        this.get()

    def test_atlas_metadata_table_import(self):

        from rockAtlas.bookkeeping import bookkeeper
        bk = bookkeeper(
            log=log,
            settings=settings
        )
        bk.import_new_atlas_pointings()

    def test_clean_all(self):

        from rockAtlas.bookkeeping import bookkeeper
        bk = bookkeeper(
            log=log,
            settings=settings
        )
        bk.clean_all()

    def test_bookkeeper_function_exception(self):

        from rockAtlas.bookkeeping import bookkeeper
        try:
            this = bookkeeper(
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
