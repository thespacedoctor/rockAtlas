#!/usr/local/bin/python
# encoding: utf-8
"""
*Tighten up pyephem positions with orbfit*

:Author:
    David Young

:Date Created:
    November  1, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
import math
import codecs
import healpy as hp
import numpy as np
from collections import defaultdict
from fundamentals.mysql import readquery
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
import copy
from fundamentals.mysql import writequery
from datetime import datetime, date, time
from rockfinder import orbfit_ephemeris
from collections import defaultdict


class orbfitPositions():
    """
    *The worker class for the orbfitPositions module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``dev_flag`` -- use the dev_flag column in the database to select out specific ATLAS exposures to work with. Default *False*

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

        To initiate an orbfitPositions object, generate the positions for moving objects that already have PyEphem positions and finally add the results to the `orbfit_positions` database table, use the following:

        .. code-block:: python

            from rockAtlas.positions import orbfitPositions
            oe = orbfitPositions(
                log=log,
                settings=settings
            )
            oe.get()
    """
    # INITIALISATION

    def __init__(
            self,
            log,
            settings=False,
            dev_flag=False

    ):
        self.log = log
        log.debug("instansiating a new 'orbfitPositions' object")
        self.settings = settings
        self.dev_flag = dev_flag
        # xt-self-arg-tmpx

        # INITIAL ACTIONS
        # SETUP ALL DATABASE CONNECTIONS
        from rockAtlas import database
        db = database(
            log=log,
            settings=settings
        )
        dbConns, dbVersions = db.connect()
        self.atlas3DbConn = dbConns["atlas3"]
        self.atlas4DbConn = dbConns["atlas4"]
        self.atlasMoversDBConn = dbConns["atlasMovers"]

        sqlQuery = """update
            atlas_exposures
        set orbfit_positions = 1, dophot_match = 1
        WHERE
            pyephem_positions = 1
                AND (orbfit_positions = 0 or dophot_match = 0) and local_data = 1 and expname not in (select distinct expname from pyephem_positions);""" % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )

        return None

    def get(self,
            singleExposure):
        """
        *get the orbfitPositions object*

        **Key Arguments:**
            - ``singleExposure`` -- only execute fot a single exposure (useful for debugging)

        **Return:**
            - None

        **Usage:**

            See class docstring
        """
        self.log.info('starting the ``get`` method')

        if singleExposure:
            batchSize = 1
        else:
            batchSize = 10

        expsoureCount = 1
        while expsoureCount > 0:
            expsoureObjects, astorbString, expsoureCount = self._get_exposures_requiring_orbfit_positions(
                batchSize=batchSize)
            if expsoureCount:
                orbfitPositions = self._get_orbfit_positions(
                    expsoureObjects, astorbString)
                self._add_orbfit_eph_to_database(
                    orbfitPositions, expsoureObjects)
            if singleExposure:
                expsoureCount = 0

        self.log.info('completed the ``get`` method')
        return None

    def _get_exposures_requiring_orbfit_positions(
            self,
            batchSize=25):
        """*get next batch of exposures requiring orbfit positions*

        **Key Arguments:**
            - ``batchSize`` -- number of exposures to process per batch

        **Return:**
            - ``expsoureObjects`` -- a dictionary with exposure names as keys and a dictionary of exposure ra, dec and moving object names/mpc number as values
            - ``astorbString`` -- as string of the object orbital elements to be used later for orbfit ephemerides
        """
        self.log.info(
            'starting the ``_get_exposures_requiring_orbfit_positions`` method')

        if self.dev_flag == True:
            dev_flag = " and dev_flag = 1"
        else:
            dev_flag = ""

        sqlQuery = u"""
            select count(*) as count from atlas_exposures where pyephem_positions = 1 and orbfit_positions = 0 and local_data = 1  %(dev_flag)s order by pyephem_mjd asc
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        expsoureCount = rows[0]["count"]

        if batchSize > 1:
            text = "%(batchSize)s exposures" % locals()
        else:
            text = "%(batchSize)s exposure" % locals()

        if expsoureCount:
            print "There are currently %(expsoureCount)s ATLAS exposures with pyephem positions needing tightened - processing the next %(text)s with orbfit" % locals()
        else:
            print "There are no more ATLAS exposures requiring to be processed with orbfit"
            return {}, '', expsoureCount

        sqlQuery = u"""
            SELECT
                a.expname, a.mjd, o.primaryId, a.raDeg, a.decDeg, p.object_name, p.mpc_number, o.astorb_string, a.mjd+a.exp_time/(2*3600*24) as `mjd_mid`
            FROM
                atlas_exposures a,
                pyephem_positions p,
                orbital_elements o
            WHERE
                a.expname=p.expname
                 %(dev_flag)s
                and
                p.object_name=o.name
                and
                a.expname IN (SELECT
                        *
                    FROM
                        (SELECT
                            expname
                        FROM
                            atlas_exposures
                        WHERE
                            pyephem_positions = 1
                                AND orbfit_positions = 0 and local_data = 1 order by mjd
                        LIMIT %(batchSize)s) AS a);
                    """ % locals()
        objects = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        expsoureObjects = {}
        astorbDict = {}

        for o in objects:
            if o["expname"] not in expsoureObjects:
                expsoureObjects[o["expname"]] = {
                    "ra": o["raDeg"],
                    "dec": o["decDeg"],
                    "mjd": o["mjd_mid"],
                    "objects": [[o["mpc_number"], o["object_name"], o["primaryId"]]]
                }
            else:
                expsoureObjects[o["expname"]]["objects"].append(
                    [o["mpc_number"], o["object_name"], o["primaryId"]])

            if o["object_name"] not in astorbDict:
                astorbDict[o["object_name"]] = o["astorb_string"]

        astorbString = ("\n").join(astorbDict.values())

        self.log.info(
            'completed the ``_get_exposures_requiring_orbfit_positions`` method')
        return expsoureObjects, astorbString, expsoureCount

    def _get_orbfit_positions(
            self,
            expsoureObjects,
            astorbString):
        """* get orbfit positions*

        **Key Arguments:**
            - ``expsoureObjects`` -- a dictionary with exposure names as keys and a dictionary of exposure ra, dec and moving object names/mpc number as values
            - ``astorbString`` -- as string of the object orbital elements to be used with orbfit

        **Return:**
            - ``orbfitMatches`` -- all of the ephemerides generated by Orbfit that match against the exact ATLAS exposure footprint
        """
        self.log.info('starting the ``_get_orbfit_positions`` method')

        # WRITE THE CUSTOM ORBFIT DATABASE TO FILE
        now = datetime.now()
        astorbFilepath = now.strftime("/tmp/astorb-%Y%m%dt%H%M%S%f.dat")

        try:
            self.log.debug("attempting to open the file %s" %
                           (astorbFilepath,))
            writeFile = codecs.open(astorbFilepath, encoding='utf-8', mode='w')
        except IOError, e:
            message = 'could not open the file %s' % (astorbFilepath,)
            self.log.critical(message)
            raise IOError(message)
        writeFile.write(astorbString)
        writeFile.close()

        orbfitMatches = []
        for expname, v in expsoureObjects.iteritems():
            raDeg = v["ra"]
            decDeg = v["dec"]
            mjd = v["mjd"]
            objects = {}

            for o in v["objects"]:

                if o[0]:
                    objects[o[0]] = [o[0], o[1], o[2]]
                else:
                    objects[o[1].replace(" ", "")] = [o[0], o[1], o[2]]

            if expname[:2] == "02":
                obscode = "T05"
            elif expname[:2] == "01":
                obscode = "T08"

            orbfitEph = orbfit_ephemeris(
                log=self.log,
                obscode=obscode,
                objectId=objects.keys(),
                mjd=mjd,
                settings=self.settings,
                verbose=True,
                astorbPath=astorbFilepath
            )

            for o in orbfitEph:
                o["expname"] = expname
                o["mpc_number"] = objects[o["object_name"]][0]
                o["orbital_elements_id"] = objects[o["object_name"]][
                    2]
                o["object_name"] = objects[o["object_name"]][
                    1]

            matchedEph = self._match_objects_against_atlas_footprint(
                orbfitEph=orbfitEph, ra=raDeg, dec=decDeg)

            orbfitMatches += matchedEph

        try:
            os.remove(astorbFilepath)
        except:
            pass

        self.log.info('completed the ``_get_orbfit_positions`` method')
        return orbfitMatches

    def _match_objects_against_atlas_footprint(
            self,
            orbfitEph,
            ra,
            dec):
        """*match the orbfit generated object positions against atlas exposure footprint*

        **Key Arguments:**
            - ``orbfitEph`` -- the orbfit ephemerides
            - ``ra`` -- the ATLAS exposure RA (degrees)
            - ``dec`` -- the ATLAS exposure DEC (degrees)

        **Return:**
            - ``matchedEph`` -- the ephemerides of objects falling within the ATLAS exposure footprint
        """
        self.log.info(
            'starting the ``_match_objects_against_atlas_footprint`` method')

        # GET THE ORBFIT MAG LIMIT
        magLimit = float(self.settings["orbfit"]["magnitude limit"])
        tileSide = float(self.settings["orbfit"]["atlas exposure match side"])

        pi = (4 * math.atan(1.0))
        DEG_TO_RAD_FACTOR = pi / 180.0
        RAD_TO_DEG_FACTOR = 180.0 / pi
        nside = 1024

        raFc = ra
        decFc = dec

        eph = []
        raArray = []
        decArray = []
        for o in orbfitEph:
            if float(o["apparent_mag"]) < magLimit:
                eph.append(o)
                raArray.append(float(o["ra_deg"]))
                decArray.append(float(o["dec_deg"]))

        raArray = np.array(raArray)
        decArray = np.array(decArray)
        healpix = hp.ang2pix(nside, theta=raArray, phi=decArray, lonlat=True)

        # GENERATE THE EXPOSURE HEALPIX ID MAP
        decCorners = (decFc - tileSide / 2,
                      decFc + tileSide / 2)
        corners = []
        for d in decCorners:
            if d > 90.:
                d = 180. - d
            elif d < -90.:
                d = -180 - d
            raCorners = (raFc - (tileSide / 2) / np.cos(d * DEG_TO_RAD_FACTOR),
                         raFc + (tileSide / 2) / np.cos(d * DEG_TO_RAD_FACTOR))
            for r in raCorners:
                if r > 360.:
                    r = 720. - r
                elif r < 0.:
                    r = 360. + r
                corners.append(hp.ang2vec(r, d, lonlat=True))

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

        # DICTIONARY STORES ALL THE RELEVANT COORDINATES
        dicto = defaultdict(list)
        for ind, (p, r, d, o) in enumerate(zip(healpix, raArray, decArray, eph)):
            dicto[p].append(o)

        matchedEph = []
        for ele in expPixels:
            if ele in dicto:
                matchedEph.append(dicto[ele][0])

        self.log.info(
            'completed the ``_match_objects_against_atlas_footprint`` method')
        return matchedEph

    def _add_orbfit_eph_to_database(
            self,
            orbfitMatches,
            expsoureObjects):
        """* add orbfit eph to database*

        **Key Arguments:**
            - ``orbfitMatches`` -- all of the ephemerides generated by Orbfit that match against the exact ATLAS exposure footprint
            - ``expsoureObjects`` -- the dictionary of original exposure objects

        **Return:**
            - None
        """
        self.log.info('starting the ``_add_orbfit_eph_to_database`` method')

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            dictList=orbfitMatches,
            dbTableName="orbfit_positions",
            uniqueKeyList=["expname", "object_name"],
            dateModified=True,
            batchSize=10000,
            replace=True
        )

        exposures = expsoureObjects.keys()
        exposures = '","'.join(exposures)

        sqlQuery = """update atlas_exposures set  orbfit_positions = 1 where expname in ("%(exposures)s")""" % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )

        self.log.info('completed the ``_add_orbfit_eph_to_database`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
