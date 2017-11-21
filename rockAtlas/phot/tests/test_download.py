import os
import nose2
import shutil
import unittest
import yaml
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


class test_download(unittest.TestCase):

    def test_mjds_to_download(self):

        from rockAtlas.phot import download
        this = download(
            log=log,
            settings=settings
        )
        mjds = this._determine_mjds_to_download()

        print mjds

    def test_download_function(self):

        from rockAtlas.phot import download
        this = download(
            log=log,
            settings=settings
        )
        results = this.get(days=1)

    def test_remove_processed_data_function(self):

        from rockAtlas.phot import download
        this = download(
            log=log,
            settings=settings
        )
        results = this._remove_processed_data()

    def test_download_function_exception(self):

        from rockAtlas import download
        try:
            this = download(
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
