import os
import nose2
import shutil
import unittest
import yaml
from rockAtlas.positions import pyephemPositions
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


class test_pyephemPositions(unittest.TestCase):

    def test_pyephemPositions_function(self):

        from rockAtlas.positions import pyephemPositions
        this = pyephemPositions(
            log=log,
            settings=settings
        )
        this.get(singleSnapshot=True)

    def test_get_atlas_exposures_requiring_pyephem_function(self):

        from rockAtlas.positions import pyephemPositions
        this = pyephemPositions(
            log=log,
            settings=settings
        )
        nextMjd, exposures, snapshotsRequired = this._get_exposures_requiring_pyephem_positions()

        print nextMjd
        print exposures

    def test_generate_pyephem_snapshot_function(self):

        from rockAtlas.positions import pyephemPositions
        this = pyephemPositions(
            log=log,
            settings=settings
        )
        pyephemDB = this._generate_pyephem_snapshot(57916.1)

        print len(pyephemDB)

    def test_pyephemPositions_function_exception(self):

        from rockAtlas.positions import pyephemPositions
        try:
            this = pyephemPositions(
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
