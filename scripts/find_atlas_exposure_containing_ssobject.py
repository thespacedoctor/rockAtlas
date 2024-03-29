#!/usr/local/bin/python
# encoding: utf-8
"""
*Generate a list of all the ATLAS exposures containing a given solar-system object and its position on those exposures*

:Author:
    David Young

:Date Created:
    March 6, 2018

Usage:
    find_atlas_exposure_containing_ssobject <ssobject>

Options:
    ssobject              the name of the solar-system object to find wihtin ATLAS exposures
    -h, --help            show this help message
    -v, --version         show version
    -s, --settings        the settings file
"""
################# GLOBAL IMPORTS ####################
import sys
import os
from fundamentals import tools
from rockfinder import jpl_horizons_ephemeris
from fundamentals.renderer import list_of_dictionaries
from astrocalc.coords import separations
from fundamentals.mysql import database, readquery
import math
import healpy as hp
import numpy as np
import codecs
import time


def main(arguments=None):
    """
    *The main function used when ``find_atlas_exposure_containing_ssobject.py`` is run as a single script from the cl*
    """

    # SETUP VARIABLES
    # MAKE SURE HEALPIX SMALL ENOUGH TO MATCH FOOTPRINTS CORRECTLY
    nside = 1024
    pi = (4 * math.atan(1.0))
    DEG_TO_RAD_FACTOR = pi / 180.0
    RAD_TO_DEG_FACTOR = 180.0 / pi
    tileSide = 5.46

    i = 0
    outputList = []
    rsyncContent = []
    obscodes = {"02": "T05", "01": "T08"}

    # SETUP THE COMMAND-LINE UTIL SETTINGS
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName=False
    )
    arguments, settings, log, dbConn = su.setup()

    # UNPACK REMAINING CL ARGUMENTS USING `EXEC` TO SETUP THE VARIABLE NAMES
    # AUTOMATICALLY
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    dbSettings = {
        'host': '127.0.0.1',
        'user': 'dryx',
        'tunnel': {
            'remote ip': 'starbase.mp.qub.ac.uk',
            'remote datbase host': 'dormammu',
            'remote user': 'dry',
            'port': 5003
        },
        'password': 'dryxPass',
        'db': 'atlas_moving_objects'
    }

    # SETUP DATABASE CONNECTIONS
    dbConn = database(
        log=log,
        dbSettings=dbSettings
    ).connect()

    # GRAB THE EXPOSURE LISTING
    for expPrefix, obscode in obscodes.iteritems():
        exposureList = []
        mjds = []
        sqlQuery = "select * from atlas_exposures where expname like '%(expPrefix)s%%'" % locals(
        )
        connected = 0
        while connected == 0:
            try:
                rows = readquery(
                    log=log,
                    sqlQuery=sqlQuery,
                    dbConn=dbConn,
                    quiet=False
                )
                connected = 1
            except:
                # SETUP DATABASE CONNECTIONS
                dbConn = database(
                    log=log,
                    dbSettings=dbSettings
                ).connect()
                print "Can't connect to DB - try again"
                time.sleep(2)

        t = len(rows)

        print "There are %(t)s '%(expPrefix)s' exposures to check - hang tight" % locals()

        for row in rows:
            row["mjd"] = row["mjd"] + row["exp_time"] / (2. * 60 * 60 * 24)
            exposureList.append(row)
            mjds.append(row["mjd"])

        results = []

        batchSize = 500
        total = len(mjds[1:])
        batches = int(total / batchSize)

        start = 0
        end = 0
        theseBatches = []
        for i in range(batches + 1):
            end = end + batchSize
            start = i * batchSize
            thisBatch = mjds[start:end]
            theseBatches.append(thisBatch)

        i = 0
        totalLen = len(theseBatches)
        index = 0
        for batch in theseBatches:
            i += 1

            if index > 1:
                # Cursor up one line and clear line
                sys.stdout.write("\x1b[1A\x1b[2K")
            print "Requesting batch %(i)04d/%(totalLen)s from JPL" % locals()
            index += 1

            eph = jpl_horizons_ephemeris(
                log=log,
                objectId=[ssobject],
                mjd=batch,
                obscode=obscode,
                verbose=False
            )

            for b in batch:
                match = 0
                # print b
                for row in eph:
                    if math.floor(row["mjd"] * 10000 + 0.01) == math.floor(b * 10000 + 0.01):
                        match = 1
                        results.append(row)
                if match == 0:
                    for row in eph:
                        if math.floor(row["mjd"] * 10000) == math.floor(b * 10000):
                            match = 1
                            results.append(row)
                if match == 0:
                    results.append(None)
                    this = math.floor(b * 10000 + 0.01)
                    print "MJD %(b)s (%(this)s) is missing" % locals()
                    for row in eph:
                        print math.floor(row["mjd"] * 10000 + 0.00001)
                    print ""

        print "Finding the exopsures containing the SS object"

        for e, r in zip(exposureList, results):
            # CALCULATE SEPARATION IN ARCSEC
            if not r:
                continue

            calculator = separations(
                log=log,
                ra1=r["ra_deg"],
                dec1=r["dec_deg"],
                ra2=e["raDeg"],
                dec2=e["decDeg"],
            )
            angularSeparation, north, east = calculator.get()
            sep = float(angularSeparation) / 3600.
            if sep < 5.:

                # THE SKY-LOCATION AS A HEALPIXEL ID
                pinpoint = hp.ang2pix(nside, theta=r["ra_deg"], phi=r[
                                      "dec_deg"], lonlat=True)

                decCorners = (e["decDeg"] - tileSide / 2,
                              e["decDeg"] + tileSide / 2)
                corners = []
                for d in decCorners:
                    if d > 90.:
                        d = 180. - d
                    elif d < -90.:
                        d = -180 - d
                    raCorners = (e["raDeg"] - (tileSide / 2) / np.cos(d * DEG_TO_RAD_FACTOR),
                                 e["raDeg"] + (tileSide / 2) / np.cos(d * DEG_TO_RAD_FACTOR))
                    for rc in raCorners:
                        if rc > 360.:
                            rc = 720. - rc
                        elif rc < 0.:
                            rc = 360. + rc
                        corners.append(hp.ang2vec(rc, d, lonlat=True))

                # NEAR THE POLES RETURN SQUARE INTO TRIANGE - ALMOST DEGENERATE
                pole = False
                for d in decCorners:
                    if d > 87.0 or d < -87.0:
                        pole = True

                if pole == True:
                    corners = corners[1:]
                else:
                    # FLIP CORNERS 3 & 4 SO HEALPY UNDERSTANDS POLYGON SHAPE
                    corners = [corners[0], corners[1],
                               corners[3], corners[2]]

                # RETURN HEALPIXELS IN EXPOSURE AREA
                expPixels = hp.query_polygon(nside, np.array(
                    corners))
                if pinpoint in expPixels:
                    outputList.append(
                        {"obs": e["expname"],
                         "mjd": e["mjd"],
                         "raDeg": r["ra_deg"],
                         "decDeg": r["dec_deg"],
                         "mag": r["apparent_mag"],
                         "sep": sep
                         })
                    thisMjd = int(math.floor(e["mjd"]))
                    expname = e["expname"]
                    ssobject_ = ssobject.replace(" ", "_")
                    raStr = r["ra_deg"]
                    decStr = r["dec_deg"]
                    rsyncContent.append(
                        "rsync -av dyoung@atlas-base-adm01.ifa.hawaii.edu:/atlas/red/%(expPrefix)sa/%(thisMjd)s/%(expname)s.fits.fz %(ssobject_)s_atlas_exposures/" % locals())
                    rsyncContent.append(
                        "touch %(ssobject_)s_atlas_exposures/%(expname)s.location" % locals())
                    rsyncContent.append(
                        'echo "_RAJ2000,_DEJ2000,OBJECT\n%(raStr)s,%(decStr)s,%(ssobject)s" > %(ssobject_)s_atlas_exposures/%(expname)s.location' % locals())

    dataSet = list_of_dictionaries(
        log=log,
        listOfDictionaries=outputList,
        # use re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}T') for mysql
        reDatetime=False
    )

    ssobject = ssobject.replace(" ", "_")
    csvData = dataSet.csv(
        filepath="./%(ssobject)s_atlas_exposure_matches.csv" % locals())

    rsyncContent = ("\n").join(rsyncContent)
    pathToWriteFile = "./%(ssobject)s_atlas_exposure_rsync.sh" % locals()
    try:
        log.debug("attempting to open the file %s" % (pathToWriteFile,))
        writeFile = codecs.open(pathToWriteFile, encoding='utf-8', mode='w')
    except IOError, e:
        message = 'could not open the file %s' % (pathToWriteFile,)
        log.critical(message)
        raise IOError(message)
    writeFile.write(rsyncContent)
    writeFile.close()

    return

if __name__ == '__main__':
    main()
