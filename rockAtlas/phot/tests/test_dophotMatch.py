import os
import nose2
import shutil
import unittest
import yaml
from rockAtlas.utKit import utKit
import time
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

# # load settings
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


class test_dophotMatch(unittest.TestCase):

    def test_dophotMatch_function(self):

        t1 = time.time()

        from rockAtlas.phot import dophotMatch
        this = dophotMatch(
            log=log,
            settings=settings
        )
        exposureIds, remaining = this._select_exposures_requiring_dophot_extraction()

        cachePath = settings["atlas archive path"]

        print exposureIds
        dophotMatches = this._extract_phot_from_exposure(
            expId=exposureIds[0], cachePath=cachePath)

        this._add_dophot_matches_to_database(
            dophotMatches=[dophotMatches], exposureIds=[exposureIds[0]])

        print time.time() - t1

    def test_dophotMatch_get_function(self):

        t1 = time.time()

        from rockAtlas.phot import dophotMatch
        this = dophotMatch(
            log=log,
            settings=settings
        )
        this.get()

        print time.time() - t1

    def test_dophotMatch_function_exception(self):

        from rockAtlas.phot import dophotMatch
        try:
            this = dophotMatch(
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
