import os
import nose2
import shutil
import unittest
import yaml
from rockAtlas.enhance import phase_curve
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
stream = file("/Users/Dave/.config/rockAtlas/rockAtlas.yaml", 'r')
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


class test_phase_curve(unittest.TestCase):

    def test_update_atlas_objects_table(self):

        from rockAtlas.enhance import phase_curve
        pc = phase_curve(
            log=log,
            settings=settings
        )
        pc.update_atlas_object_table()

    def test_phase_curve_grab_objects_up_update(self):

        from rockAtlas.enhance import phase_curve
        pc = phase_curve(
            log=log,
            settings=settings
        )
        objects = pc.get_objects(filter='c')
        print objects

    def test_phase_curve_grab_mags(self):

        from rockAtlas.enhance import phase_curve
        pc = phase_curve(
            log=log,
            settings=settings
        )
        objects = pc.get_objects(filter='c')

        from rockAtlas.enhance import phase_curve
        pc = phase_curve(
            log=log,
            settings=settings
        )

        for o in objects[0:10]:
            results = pc.calculate_phase_curve_parameters(o, filter='c')
            print results

    def test_calculate(self):

        from rockAtlas.enhance import phase_curve
        pc = phase_curve(
            log=log,
            settings=settings
        )
        pc.calculate()

    def test_phase_curve_function_exception(self):

        from rockAtlas.enhance import phase_curve
        try:
            this = phase_curve(
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
