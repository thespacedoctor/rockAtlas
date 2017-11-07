import os
import nose2
import shutil
import unittest
import yaml
from rockAtlas.positions import orbfitPositions
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


class test_orbfitPositions(unittest.TestCase):

    def test_orbfit_select_function(self):

        from rockAtlas.positions import orbfitPositions
        this = orbfitPositions(
            log=log,
            settings=settings,
            dev_flag=True
        )
        expsoureObjects, astorbString = this._get_exposures_requiring_orbfit_positions()

        orbfitPositions = this._get_orbfit_positions(
            expsoureObjects, astorbString)

        this._add_orbfit_eph_to_database(orbfitPositions, expsoureObjects)

    def test_orbfit_get_function(self):

        from rockAtlas.positions import orbfitPositions
        oe = orbfitPositions(
            log=log,
            settings=settings,
            dev_flag=True
        )
        oe.get(singleExposure=True)

    def test_orbfitPositions_function(self):

        from rockAtlas.positions import orbfitPositions
        this = orbfitPositions(
            log=log,
            settings=settings
        )
        this.get()

    def test_orbfitPositions_function_exception(self):

        from rockAtlas.positions import orbfitPositions
        try:
            this = orbfitPositions(
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
