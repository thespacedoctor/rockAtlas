#!/usr/bin/env python
# encoding: utf-8
"""
Documentation for rockAtlas can be found here: http://rockAtlas.readthedocs.org/en/stable

Usage:
    rockAtlas init
    rockAtlas bookkeeping [-f] [-s <pathToSettingsFile>]
    rockAtlas astorb
    rockAtlas pyephem [-o]
    rockAtlas orbfit [-o]
    rockAtlas cache <days>
    rockAtlas dophot
    rockAtlas cycle <days>

Commands:
    bookkeeping           update and clean database tables, perform essential bookkeeping tasks
    astorb                download astorb.dat orbital elements file and update the orbital elements database table
    pyephem               generate the pyephem positions overlapping the ATLAS exposures in the moving objects database
    orbfit                generate the orbfit positions overlapping the ATLAS exposures in the moving objects database
    cache                 download a cache of ATLAS dophot data to chew on (cache limit set in settings file)
    dophot                match the orbfit generated positions against the dophot recorded postions (for locally cached files)
    cycle                 cycle through the moving objects database, downloading a few nights data, generate pyephem positions, generate orbfit positions, match dophots file ... and repeat


Options:
    init                  setup the rockAtlas settings file for the first time
    days                  number of days to cache
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
import time
from docopt import docopt
from fundamentals import tools, times
from subprocess import Popen, PIPE, STDOUT
# from ..__init__ import *


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings

    dev_flag = False

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
            settings=settings,
            dev_flag=dev_flag
        )
        pyeph.get(singleSnapshot=oneFlag)

    if orbfit:
        from rockAtlas.positions import orbfitPositions
        oe = orbfitPositions(
            log=log,
            settings=settings,
            dev_flag=dev_flag
        )
        oe.get(singleExposure=oneFlag)

    if cache:
        from rockAtlas.phot import download
        data = download(
            log=log,
            settings=settings,
            dev_flag=dev_flag
        )
        data.get(days=days)

    if dophot:
        from rockAtlas.phot import dophotMatch
        dp = dophotMatch(
            log=log,
            settings=settings
        )
        dp.get()

    if cycle:
        from rockAtlas.phot import download
        from rockAtlas.positions import pyephemPositions
        from rockAtlas.positions import orbfitPositions
        from rockAtlas.phot import dophotMatch
        from fundamentals.mysql import readquery

        # INITIAL ACTIONS
        # SETUP ALL DATABASE CONNECTIONS
        from rockAtlas import database
        db = database(
            log=log,
            settings=settings
        )
        dbConns, dbVersions = db.connect()
        atlas3DbConn = dbConns["atlas3"]
        atlas4DbConn = dbConns["atlas4"]
        atlasMoversDBConn = dbConns["atlasMovers"]

        while True:

            if dev_flag:
                o = " and dev_flag = 1"
            else:
                o = " "

            sqlQuery = u"""
                select distinct floor(mjd) from (
select mjd from atlas_exposures where dophot_match = 0 %(o)s
union all
select mjd from day_tracker where processed = 0 %(o)s) as a;
            """ % locals()
            rows = readquery(
                log=log,
                sqlQuery=sqlQuery,
                dbConn=atlasMoversDBConn,
                quiet=False
            )

            if len(rows) == 0:
                if dev_flag:
                    print "Processing of the ATLAS development dataset is now complete and up to date"
                else:
                    print "Processing of ATLAS data is now complete and up to date"
                break

            start_time = time.time()

            data = download(
                log=log,
                settings=settings,
                dev_flag=dev_flag
            )
            data.get(days=days)

            print "%d seconds to download ATLAS cache of %d days" % (time.time() - start_time, days)
            start_time = time.time()

            pyeph = pyephemPositions(
                log=log,
                settings=settings,
                dev_flag=dev_flag
            )
            pyeph.get()

            print "%d seconds to generate pyephem snapshots" % (time.time() - start_time,)
            start_time = time.time()

            oe = orbfitPositions(
                log=log,
                settings=settings,
                dev_flag=dev_flag
            )
            oe.get()

            print "%d seconds to generate orbfit positions" % (time.time() - start_time,)
            start_time = time.time()

            dp = dophotMatch(
                log=log,
                settings=settings
            )
            dp.get()

            print "%d seconds to extract dophot measurements" % (time.time() - start_time,)
            start_time = time.time()

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
