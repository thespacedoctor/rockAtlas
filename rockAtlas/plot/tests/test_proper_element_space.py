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
    "/Users/Dave/.config/rockAtlas/rockAtlas.yaml", 'r')
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


class test_proper_element_space(unittest.TestCase):

    def test_get_asteroid_data_function(self):

        from rockAtlas.plot import proper_element_space
        this = proper_element_space(
            log=log,
            settings=settings
        )
        print len(this.get_asteroid_data())

    def test_plot_asteroids_function(self):

        from rockAtlas.plot import proper_element_space
        this = proper_element_space(
            log=log,
            settings=settings
        )
        ssObjectData = this.get_asteroid_data()
        this.plot_asteroids(ssObjectData)

    def test_proper_element_space_function_exception(self):

        from rockAtlas.plot import proper_element_space
        try:
            this = proper_element_space(
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
