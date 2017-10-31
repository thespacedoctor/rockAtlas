#!/usr/local/bin/python
# encoding: utf-8
"""
*Estimate the positions of moving objects in the neighbourhood of the ATLAS exposures using pyephemPositions and add results to the database*

:Author:
    David Young

:Date Created:
    October 30, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import readquery
import math
import ephem
import codecs
import healpy as hp
import numpy as np
from collections import defaultdict
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
import copy
from fundamentals.mysql import writequery


class pyephemPositions():
    """
    *The worker class for the pyephemPositions module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``dev_flag`` -- use the dev_flag column in the database to select out specific ATLAS exposures to work with. Default *False*

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a pyephemPositions object, use the following:

        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this class
            - add a tutorial about ``pyephemPositions`` to documentation
            - create a blog post about what ``pyephemPositions`` does

        .. code-block:: python 

            usage code   
    """
    # Initialisation
    # 1. @flagged: what are the unique attrributes for each object? Add them
    # to __init__

    def __init__(
            self,
            log,
            settings=False,
            dev_flag=True
    ):
        self.log = log
        log.debug("instansiating a new 'pyephemPositions' object")
        self.settings = settings
        self.dev_flag = dev_flag

        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions
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

        return None

    def get(self):
        """
        *get the pyephemPositions object*

        **Return:**
            - ``pyephemPositions``

        **Usage:**
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this method
            - update the package tutorial if needed

        .. code-block:: python 

            usage code 
        """
        self.log.info('starting the ``get`` method')

        nextMjd, exposures = self._get_exposures_requiring_pyephem_positions()
        pyephemDB = self._generate_pyephem_snapshot(mjd=nextMjd)
        matchedObjects = self._match_pyephem_snapshot_to_atlas_exposures(
            pyephemDB, exposures)
        self._add_matched_objects_to_database(matchedObjects)
        self._update_database_flag(exposures)

        self.log.info('completed the ``get`` method')
        return None

    def _get_exposures_requiring_pyephem_positions(
            self):
        """*get next batch of exposures requiring pyephem positions*
        """
        self.log.info(
            'starting the ``_get_exposures_requiring_pyephem_positions`` method')

        if self.dev_flag == True:
            dev_flag = " and dev_flag = 1"
        else:
            dev_flag = ""

        sqlQuery = u"""
            select distinct pyephem_mjd from atlas_exposures where pyephem_positions = 0  %(dev_flag)s order by pyephem_mjd asc
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        snapshotsRequired = len(rows)

        print "There are currently %(snapshotsRequired)s more pyephem snapshots required " % locals()

        nextMjd = rows[0]["pyephem_mjd"]

        sqlQuery = u"""
            select * from atlas_exposures where pyephem_positions = 0 %(dev_flag)s and pyephem_mjd = %(nextMjd)s 
        """ % locals()
        exposures = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        exposures = list(exposures)

        self.log.info(
            'completed the ``_get_exposures_requiring_pyephem_positions`` method')
        return nextMjd, exposures

    def _generate_pyephem_snapshot(
            self,
            mjd):
        """* generate pyephem snapshot*

        **Key Arguments:**
            - ``mjd`` -- the mjd to generate the pyephem snapshot database for.

        **Return:**
            - ``pyephemDB`` -- the pyephem solar-system snapshot database 
        """
        self.log.info('starting the ``_generate_pyephem_snapshot`` method')

        # CONSTANTS
        nside = 1024
        pi = (4 * math.atan(1.0))
        DEG_TO_RAD_FACTOR = pi / 180.0
        RAD_TO_DEG_FACTOR = 180.0 / pi

        # GRAB PARAMETERS FROM THE SETTINGS FILE
        magLimit = self.settings["pyephem"]["magnitude limit"]
        astorbDatabase = self.settings["astorb filepath"]

        try:
            self.log.debug("attempting to open the file %s" %
                           (astorbDatabase,))
            readFile = codecs.open(astorbDatabase, encoding='utf-8', mode='r')
            thisData = readFile.read()
            readFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (astorbDatabase,)
            self.log.critical(message)
            raise IOError(message)
        readFile.close()

        # THE PYEPHEM OBSERVER
        obs = ephem.Observer()
        # PYEPHEM WORKS IN DUBLIN JD, TO CONVERT FROM MJD SUBTRACT 15019.5
        obs.date = float(mjd) - 15019.5
        pyephemDB = {
            "ra_deg": [],
            "dec_deg": [],
            "mpc_number": [],
            "object_name": [],
            "healpix": []
        }

        # CONVERT ASTORB DATABASE TO XEPHEM DATABASE FORMAT
        lines = thisData.split("\n")
        for l in lines:

            if len(l) < 50:
                continue
            d = {}

            # PARSE THE LINE FROM astorb.dat (UNNEEDED VALUES COMMENTED OUT)
            d["mpc_number"] = l[0:7].strip()
            d["name"] = l[7:26].strip()
            d["discoverer"] = l[26:41].strip()
            d["H_abs_mag"] = l[41:48].strip()
            d["G_slope"] = l[48:54].strip()
            d["color_b_v"] = l[54:59].strip()
            d["diameter_km"] = l[59:65].strip()
            d["class"] = l[65:71].strip()
            # d["int1"] = l[71:75].strip()
            # d["int2"] = l[75:79].strip()
            # d["int3"] = l[79:83].strip()
            # d["int4"] = l[83:87].strip()
            # d["int5"] = l[87:91].strip()
            # d["int6"] = l[91:95].strip()
            d["orbital_arc_days"] = l[95:101].strip()
            d["number_obs"] = l[101:106].strip()
            d["epoch"] = l[106:115].strip()
            d["M_mean_anomaly_deg"] = l[115:126].strip()
            d["o_arg_peri_deg"] = l[126:137].strip()
            d["O_long_asc_node_deg"] = l[137:148].strip()
            d["i_inclination_deg"] = l[148:158].strip()
            d["e_eccentricity"] = l[158:169].strip()
            d["a_semimajor_axis"] = l[169:182].strip()
            d["orbit_comp_date"] = l[182:191].strip()
            d["ephem_uncertainty_arcsec"] = l[191:199].strip()
            d["ephem_uncertainty_change_arcsec_day"] = l[199:208].strip()
            d["ephem_uncertainty_date"] = l[208:217].strip()
            # d["peak_ephem_uncertainty_next_arcsec"] = l[217:225].strip()
            # d["peak_ephem_uncertainty_next_date"] = l[225:234].strip()
            # d["peak_ephem_uncertainty_10_yrs_from_ceu_arcsec"] = l[
            #     217:225].strip()
            # d["peak_ephem_uncertainty_10_yrs_from_ceu_date"] = l[
            #     242:251].strip()
            # d["peak_ephem_uncertainty_10_yrs_from_peu_arcsec"] = l[
            #     251:259].strip()
            # d["peak_ephem_uncertainty_10_yrs_from_peu_date"] = l[
            #     259:].strip()

            yyyy = int(d["epoch"][:4])
            mm = int(d["epoch"][4:6])
            dd = int(d["epoch"][6:])
            d["epoch_xeph"] = "%(mm)s/%(dd)s/%(yyyy)s" % locals()
            xephemStr = "%(mpc_number)s %(name)s,e,%(i_inclination_deg)s,%(O_long_asc_node_deg)s,%(o_arg_peri_deg)s,%(a_semimajor_axis)s,0,%(e_eccentricity)s,%(M_mean_anomaly_deg)s,%(epoch_xeph)s,2000.0,%(H_abs_mag)s,%(G_slope)s" % d
            xephemStr = xephemStr.strip()

            # TIDYUP
            if len(d["mpc_number"]) == 0:
                d["mpc_number"] = None

            # GENERATE EPHEMERIS FOR THIS OBJECT
            minorPlanet = ephem.readdb(xephemStr)
            minorPlanet.compute(obs)

            if minorPlanet.mag > magLimit:
                continue

            thisRa = minorPlanet.a_ra * RAD_TO_DEG_FACTOR
            thisDec = minorPlanet.a_dec * RAD_TO_DEG_FACTOR
            pyephemDB["ra_deg"].append(thisRa)
            pyephemDB["dec_deg"].append(thisDec)
            pyephemDB["mpc_number"].append(d["mpc_number"])
            pyephemDB["object_name"].append(d["name"])
            pyephemDB["healpix"].append(hp.ang2pix(
                nside, theta=thisRa, phi=thisDec, lonlat=True))

        self.log.info('completed the ``_generate_pyephem_snapshot`` method')
        return pyephemDB

    def _match_pyephem_snapshot_to_atlas_exposures(
            self,
            pyephemDB,
            exposures):
        """*match pyephem snapshot to atlas exposures*

        **Key Arguments:**
            - ``pyephemDB`` -- the pyephem solar-system snapshot database
            - ``exposures`` -- the atlas exposures to match against the snapshot

        **Return:**
            - ``matchedObjects`` -- these objects matched in the neighbourhood of the ATLAS exposures (list of dictionaries)
        """
        self.log.info(
            'starting the ``_match_pyephem_snapshot_to_atlas_exposures`` method')

        # MAKE SURE HEALPIX SMALL ENOUGH TO MATCH FOOTPRINTS CORRECTLY
        nside = 1024
        pi = (4 * math.atan(1.0))
        DEG_TO_RAD_FACTOR = pi / 180.0
        RAD_TO_DEG_FACTOR = 180.0 / pi

        # GRAB PARAMETERS FROM SETTINGS FILE
        tileSide = float(self.settings["pyephem"]["atlas exposure match side"])
        magLimit = float(self.settings["pyephem"]["magnitude limit"])

        # EXPLODE OUT THE PYEPHEM DATABASE
        ra = pyephemDB["ra_deg"]
        dec = pyephemDB["dec_deg"]
        healpix = pyephemDB["healpix"]
        objects = pyephemDB["object_name"]
        mpc_numbers = pyephemDB["mpc_number"]

        # INDEX PYEPHEM MOVERS IN DICTIONARY BY HEALPIX ID
        moversDict = defaultdict(list)
        for ind, (p, r, d, o, m) in enumerate(zip(healpix, ra, dec, objects, mpc_numbers)):
            moversDict[p].append(
                {"object_name": o,
                 "ra_deg": r,
                 "dec_deg": d,
                 "mpc_number": m
                 }
            )

        # MATCH THE PYEPHEM MOVERS AGAINST THE ATLAS EXPOSURES
        matchedObjects = []
        for e in exposures:

            expId = e["expname"]
            raFc = float(e["raDeg"])
            decFc = float(e["decDeg"])

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

            # MATCH HEALPIX ON EXPOSURE AGAINST PYEPHEM DATABASE
            for ele in expPixels:
                if ele in moversDict:
                    for o in moversDict[ele]:
                        d2 = copy.deepcopy(o)
                        d2["expname"] = expId
                        matchedObjects.append(d2)

        self.log.info(
            'completed the ``_match_pyephem_snapshot_to_atlas_exposures`` method')
        return matchedObjects

    def _add_matched_objects_to_database(
            self,
            matchedObjects):
        """*add mathced objects to database*

        **Key Arguments:**
            - ``matchedObjects`` -- these objects matched in the neighbourhood of the ATLAS exposures (list of dictionaries)
        """
        self.log.info(
            'starting the ``_add_matched_objects_to_database`` method')

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            dictList=matchedObjects,
            dbTableName="pyephem_positions",
            uniqueKeyList=["expname", "object_name"],
            dateModified=True,
            batchSize=2500,
            replace=True
        )

        self.log.info(
            'completed the ``_add_matched_objects_to_database`` method')
        return None

    def _update_database_flag(
            self,
            exposures):
        """* update database flag*

        **Key Arguments:**
            - ``exposures`` -- the atlas exposure to update the database flags for
        """
        self.log.info('starting the ``_update_database_flag`` method')

        expIds = []
        expIds[:] = [e["expname"] for e in exposures]

        expIds = ('","').join(expIds)

        sqlQuery = """update atlas_exposures set pyephem_positions = 1 where expname in ("%(expIds)s") """ % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )

        self.log.info('completed the ``_update_database_flag`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
