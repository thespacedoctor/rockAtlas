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


class test_properElements(unittest.TestCase):

    def test_download_proper_elements_function(self):

        from rockAtlas.orbital_elements import properElements
        this = properElements(
            log=log,
            settings=settings
        )
        this._download_proper_elements()

    def test_parse_proper_elements_database_file_function(self):

        from rockAtlas.orbital_elements import properElements
        this = properElements(
            log=log,
            settings=settings
        )
        this._parse_proper_elements_database_file(
            "/private/tmp/proper_elements.dat")

    def test_refresh_function(self):

        from rockAtlas.orbital_elements import properElements
        this = properElements(
            log=log,
            settings=settings
        )
        this.refresh()

    def test_properElements_function_exception(self):

        from rockAtlas.orbital_elements import properElements
        try:
            this = properElements(
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
