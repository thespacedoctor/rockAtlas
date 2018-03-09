#!/usr/local/bin/python
# encoding: utf-8
"""
*Crossmatch the orbfit determined postions of known asteroids in the ATLAS exposure FOVs with the photometry extracted by dophot*

:Author:
    David Young

:Date Created:
    November 15, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import writequery, readquery
from fundamentals import fmultiprocess
import numpy as np
import codecs
from HMpTy import HTM
import pymysql as ms
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
from rockAtlas.bookkeeping import bookkeeper

exposureIds = []


class dophotMatch():
    """
    *The worker class for the dophotMatch module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

        To initiate a dophotMatch object, and then match the orbfit predicted positions of known asteroids against the positions recored in the local cache of dophot files. use the following:

        .. code-block:: python

            from rockAtlas.phot import dophotMatch
            dp = dophotMatch(
                log=log,
                settings=settings
            )
            dp.get()
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'dophotMatch' object")
        self.settings = settings
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

        return None

    def get(self):
        """
        *match the orbfit predicted positions of known asteroids against the positions recored in the local cache of dophot files*

        **Return:**
            - None

        **Usage:**

            See class docstring
        """
        self.log.info('starting the ``get`` method')

        cachePath = self.settings["atlas archive path"]

        global exposureIds
        exposureIds, remaining = self._select_exposures_requiring_dophot_extraction(
            batch=int(self.settings["dophot"]["batch size"]))
        if remaining == 0:
            print "%(remaining)s locally cached dophot files remain needing to be parsed for orbfit predicted known asteroid positions" % locals()
            return None

        # SELECT 100 EXPOSURES REQUIRING DOPHOT EXTRACTION
        while remaining > 0:
            exposureIds, remaining = self._select_exposures_requiring_dophot_extraction(
                batch=int(self.settings["dophot"]["batch size"]))
            print "%(remaining)s locally cached dophot files remain needing to be parsed for orbfit predicted known asteroid positions" % locals()
            if remaining == 0:
                continue
            dophotMatches = fmultiprocess(log=self.log, function=_extract_phot_from_exposure,
                                          inputArray=range(len(exposureIds)), poolSize=5, timeout=300, cachePath=cachePath, settings=self.settings)
            self._add_dophot_matches_to_database(
                dophotMatches=dophotMatches, exposureIds=exposureIds)
            dophotMatches = None

        self._add_value_to_dophot_table()

        self.log.info('completed the ``get`` method')
        return None

    def _select_exposures_requiring_dophot_extraction(
            self,
            batch=10):
        """* select exposures requiring dophot extraction*

        **Key Arguments:**
            - ``batch`` -- the batch size of dophot file to process

        **Return:**
            - ``expnames`` -- the names of the expsoures in the batch
            - ``remaining`` -- the number of exposured remainging that require orbfit/dophot crossmatching
        """
        self.log.info(
            'starting the ``_select_exposures_requiring_dophot_extraction`` method')

        sqlQuery = u"""
            select expname, floor(mjd) as mjd from atlas_exposures where local_data = 1 and dophot_match = 0 and orbfit_positions = 1;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        remaining = len(rows)

        expnames = []
        expnames[:] = [(r["expname"], int(r["mjd"])) for r in rows[:batch]]

        self.log.info(
            'completed the ``_select_exposures_requiring_dophot_extraction`` method')
        return expnames, remaining

    def _add_dophot_matches_to_database(
            self,
            dophotMatches,
            exposureIds):
        """*add dophot matches to database*

        **Key Arguments:**
            - ``dophotMatches`` -- a list of lists of dophot matches
            - ``exposureIds`` -- the ATLAS exposure IDs these matches were found in

        **Return:**
            - None
        """
        self.log.info(
            'starting the ``_add_dophot_matches_to_database`` method')

        insertList = []
        for d in dophotMatches:
            insertList += d

        dbSettings = self.settings["database settings"]["atlasMovers"]

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            dictList=insertList,
            dbTableName="dophot_photometry",
            uniqueKeyList=["expname", "idx"],
            dateModified=True,
            batchSize=10000,
            replace=True,
            dbSettings=dbSettings
        )

        exps = []
        exps[:] = [e[0] for e in exposureIds]

        exps = ('","').join(exps)

        sqlQuery = """
update atlas_exposures set dophot_match = 1 where dophot_match = 0 and expname in ("%(exps)s");
update atlas_exposures set dophot_match = 2 where dophot_match = 1 and expname not in (select distinct expname from dophot_photometry);""" % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        self.log.info(
            'completed the ``_add_dophot_matches_to_database`` method')
        return None

    def _add_value_to_dophot_table(
            self):
        """*add value to dophot table*
        """
        self.log.info('starting the ``_add_value_to_dophot_table`` method')

        # ADD SEPARATION RANK TO DOPHOT TABLE
        sqlQuery = """
UPDATE dophot_photometry a,
    (SELECT
        t.primaryId,
            (SELECT
                    COUNT(*) + 1
                FROM
                    dophot_photometry t2
                WHERE
                    t2.expname = t.expname
                        AND t2.orbfit_postions_id = t.orbfit_postions_id
                        AND t2.orbfit_separation_arcsec < t.orbfit_separation_arcsec) AS match_rank
    FROM
        dophot_photometry t where t.sep_rank is null) b
SET
    a.sep_rank = b.match_rank
WHERE
    a.primaryId = b.primaryId
        AND a.sep_rank IS NULL;
""" % locals()
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        sqlQuery = """UPDATE dophot_photometry d,
    orbfit_positions o
SET
    d.object_name = o.object_name,
    d.orbital_elements_id = o.orbital_elements_id
WHERE
    d.orbfit_postions_id = o.primaryId;""" % locals()
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        self.log.info('completed the ``_add_value_to_dophot_table`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method


def _extract_phot_from_exposure(
        expIdIndex,
        log,
        cachePath,
        settings):
    """* extract phot from exposure*

    **Key Arguments:**
        - ``expIdIndex`` -- index of the exposure to extract the dophot photometry from. A tuple of expId and integer MJD
        - ``cachePath`` -- path to the cache of ATLAS data

    **Return:**
        - ``dophotRows`` -- the list of matched dophot rows
    """
    log.info('starting the ``_extract_phot_from_exposure`` method')

    global exposureIds

    expId = exposureIds[expIdIndex]

    # SETUP A DATABASE CONNECTION FOR THE remote database
    host = settings["database settings"]["atlasMovers"]["host"]
    user = settings["database settings"]["atlasMovers"]["user"]
    passwd = settings["database settings"]["atlasMovers"]["password"]
    dbName = settings["database settings"]["atlasMovers"]["db"]
    try:
        sshPort = settings["database settings"][
            "atlasMovers"]["tunnel"]["port"]
    except:
        sshPort = False
    thisConn = ms.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=dbName,
        port=sshPort,
        use_unicode=True,
        charset='utf8',
        client_flag=ms.constants.CLIENT.MULTI_STATEMENTS,
        connect_timeout=3600
    )
    thisConn.autocommit(True)

    matchRadius = float(settings["dophot"]["search radius"])

    dophotFilePath = cachePath + "/" + \
        expId[0][:3] + "/" + str(expId[1]) + "/" + expId[0] + ".dph"

    # TEST THE FILE EXISTS
    exists = os.path.exists(dophotFilePath)
    expId = expId[0]
    if not exists:

        sqlQuery = """update atlas_exposures set dophot_match = 99 where expname = "%(expId)s" """ % locals(
        )
        writequery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=thisConn,
        )
        log.info(
            'the dophot file %(expId)s.dph is missing from the local ATLAS data cache' % locals())
        return []

    try:
        log.debug("attempting to open the file %s" %
                  (dophotFilePath,))
        dophotFile = codecs.open(
            dophotFilePath, encoding='utf-8', mode='r')
        dophotData = dophotFile.read()
        dophotFile.close()
    except IOError, e:
        message = 'could not open the file %s' % (dophotFilePath,)
        log.critical(message)
        raise IOError(message)

    ra = []
    dec = []
    dophotLines = dophotData.split("\n")[1:]

    # FREE MEMORY
    dophotData = None
    for r in dophotLines:
        r = r.split()
        if len(r):
            ra.append(float(r[0]))
            dec.append(float(r[1]))

    ra = np.array(ra)
    dec = np.array(dec)

    sqlQuery = u"""
        select * from orbfit_positions where expname = "%(expId)s"
    """ % locals()
    try:
        orbFitRows = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=thisConn,
        )
    except:
        thisConn = ms.connect(
            host=host,
            user=user,
            passwd=passwd,
            db=dbName,
            port=sshPort,
            use_unicode=True,
            charset='utf8',
            client_flag=ms.constants.CLIENT.MULTI_STATEMENTS,
            connect_timeout=3600
        )
        thisConn.autocommit(True)
        orbFitRows = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=thisConn,
        )

    potSources = len(orbFitRows)

    raOrb = []
    raOrb[:] = [r["ra_deg"] for r in orbFitRows]
    decOrb = []
    decOrb[:] = [r["dec_deg"] for r in orbFitRows]

    raOrb = np.array(raOrb)
    decOrb = np.array(decOrb)

    mesh = HTM(
        depth=12,
        log=log
    )
    matchIndices1, matchIndices2, seps = mesh.match(
        ra1=ra,
        dec1=dec,
        ra2=raOrb,
        dec2=decOrb,
        radius=matchRadius / 3600.,
        convertToArray=False,
        maxmatch=0  # 1 = match closest 1, 0 = match all
    )

    # FREE MEMORY
    raOrb = None
    decOrb = None

    dophotRows = []
    for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
        # print ra[m1], dec[m1], " -> ", s * 3600., " arcsec -> ",
        # raOrb[m2], decOrb[m2]
        dList = dophotLines[m1].split()
        dDict = {
            "ra_deg": dList[0],
            "dec_deg": dList[1],
            "m": dList[2],
            "idx": dList[3],
            "type": dList[4],
            "xtsk": dList[5],
            "ytsk": dList[6],
            "fitmag": dList[7],
            "dfitmag": dList[8],
            "sky": dList[9],
            "major": dList[10],
            "minor": dList[11],
            "phi": dList[12],
            "probgal": dList[13],
            "apmag": dList[14],
            "dapmag": dList[15],
            "apsky": dList[16],
            "ap_fit": dList[17],
            "orbfit_separation_arcsec": s * 3600.,
            "orbfit_postions_id": orbFitRows[m2]["primaryId"],
            "expname": expId
        }
        dophotRows.append(dDict)

    # FREE MEMORY
    dophotLines = None
    orbFitRows = None

    log.info('completed the ``_extract_phot_from_exposure`` method')
    return dophotRows
