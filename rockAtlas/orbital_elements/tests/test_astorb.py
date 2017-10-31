import os
import nose2
import shutil
import unittest
import yaml
from rockAtlas.orbital_elements import astorb
from rockAtlas.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="WARNING",
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


class test_astorb(unittest.TestCase):

    def test_astorb_function(self):

        from rockAtlas.orbital_elements import astorb
        oe = astorb(
            log=log,
            settings=settings
        )
        oe.refresh()

    def test_download_astorb_function(self):

        from rockAtlas.orbital_elements import astorb
        oe = astorb(
            log=log,
            settings=settings
        )
        astorbgz = oe._download_astorb()

    def test_parsing_and_ingest_astorb_function(self):

        from rockAtlas.orbital_elements import astorb
        oe = astorb(
            log=log,
            settings=settings
        )
        astorbDictList = oe._parse_astorb_database_file("/tmp/astorb.dat.gz")

        print len(astorbDictList)

        oe._import_astorb_to_database(astorbDictList)

    def test_astorb_function_exception(self):

        from rockAtlas import astorb
        try:
            this = astorb(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.refresh()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
