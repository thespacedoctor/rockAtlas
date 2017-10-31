#!/usr/bin/env python
# encoding: utf-8
"""
Documentation for rockAtlas can be found here: http://rockAtlas.readthedocs.org/en/stable

Usage:
    rockAtlas init
    rockAtlas bookkeeping [-f] [-s <pathToSettingsFile>]
    rockAtlas astorb
    rockAtlas pyephem [-o]

Commands:
    bookkeeping           update and clean database tables, perform essential bookkeeping tasks
    astorb                download astorb.dat orbital elements file and update the orbital elements database table
    pyephem               generate the pyephem positions overlapping the ATLAS exposures in the moving objects database

Options:
    init                  setup the rockAtlas settings file for the first time
    -h, --help            show this help message
    -v, --version         show version
    -s, --settings        the settings file
    -f, --full            a full update (not just recently changed exposures and sources)
    -o, --one             only generate positions for a single pyephem snapshot (few 10s of exposures - useful for testing)
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from subprocess import Popen, PIPE, STDOUT
# from ..__init__ import *


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="DEBUG",
        options_first=False,
        projectName="rockAtlas"
    )
    arguments, settings, log, dbConn = su.setup()

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if varname == "import":
            varname = "iimport"
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    if init:
        from os.path import expanduser
        home = expanduser("~")
        filepath = home + "/.config/rockAtlas/rockAtlas.yaml"
        try:
            cmd = """open %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        try:
            cmd = """start %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass

    # CALL FUNCTIONS/OBJECTS
    if bookkeeping:
        from rockAtlas.bookkeeping import bookkeeper
        bk = bookkeeper(
            log=log,
            settings=settings,
            fullUpdate=fullFlag
        )
        bk.clean_all()

    if astorb:
        from rockAtlas.orbital_elements import astorb
        oe = astorb(
            log=log,
            settings=settings
        )
        oe.refresh()

    if pyephem:

        from rockAtlas.positions import pyephemPositions
        pyeph = pyephemPositions(
            log=log,
            settings=settings
        )
        pyeph.get(singleSnapshot=oneFlag)

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
