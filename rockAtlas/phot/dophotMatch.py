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
import numpy as np
import codecs


class dophotMatch():
    """
    *The worker class for the dophotMatch module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

        To initiate a dophotMatch object, use the following:

        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this class
            - add a tutorial about ``dophotMatch`` to documentation
            - create a blog post about what ``dophotMatch`` does

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

    ):
        self.log = log
        log.debug("instansiating a new 'dophotMatch' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

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
        *get the dophotMatch object*

        **Return:**
            - ``dophotMatch``

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

        dophotMatch = None

        self.log.info('completed the ``get`` method')
        return dophotMatch

    def _select_exposures_requiring_dophot_extraction(
            self):
        """* select exposures requiring dophot extraction*

        **Key Arguments:**
            # -

        **Return:**
            - None
        """
        self.log.info(
            'starting the ``_select_exposures_requiring_dophot_extraction`` method')

        from fundamentals.mysql import readquery
        sqlQuery = u"""
            select expname, floor(mjd) as mjd from atlas_exposures where local_data = 1 and dophot_match = 0;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        expnames = []
        expnames[:] = [(r["expname"], int(r["mjd"])) for r in rows]

        self.log.info(
            'completed the ``_select_exposures_requiring_dophot_extraction`` method')
        return expnames

    def _extract_phot_from_exposure(
            self,
            expId,
            cachePath):
        """* extract phot from exposure*

        **Key Arguments:**
            - ``expId`` -- the exposure to extract the dophot photometry from. A tuple of expId and integer MJD
            - ``cachePath`` -- path to the cache of ATLAS data

        **Return:**
            - None
        """
        self.log.info('starting the ``_extract_phot_from_exposure`` method')

        dophotFilePath = cachePath + "/" + \
            expId[0][:3] + "/" + str(expId[1]) + "/" + expId[0] + ".dph"
        print dophotFilePath

        # TEST THE FILE EXISTS
        exists = os.path.exists(dophotFilePath)
        expId = expId[0]
        if not exists:

            sqlQuery = """update atlas_exposures set dophot_match = 99 where expname = "%(expId)s" """ % locals(
            )
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.atlasMoversDBConn,
            )
            self.log.error(
                'the dophot file %(expId)s.dph is missing from the local ATLAS data cache' % locals())
            return None

        try:
            self.log.debug("attempting to open the file %s" %
                           (dophotFilePath,))
            dophotFile = codecs.open(
                dophotFilePath, encoding='utf-8', mode='r')
            dophotData = dophotFile.read()
            dophotFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (dophotFilePath,)
            self.log.critical(message)
            raise IOError(message)

        ra = []
        dec = []
        rows = dophotData.split("\n")
        for r in rows[1:]:
            r = r.split()
            if len(r):
                ra.append(float(r[0]))
                dec.append(float(r[1]))

        ra = np.array(ra)
        dec = np.array(dec)

        sqlQuery = u"""
            select ra_deg, dec_deg from orbfit_positions where expname = "%(expId)s"
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )

        raOrb = []
        raOrb[:] = [r["ra_deg"] for r in rows]
        decOrb = []
        decOrb[:] = [r["dec_deg"] for r in rows]

        raOrb = np.array(raOrb)
        decOrb = np.array(decOrb)

        from HMpTy import HTM
        mesh = HTM(
            depth=12,
            log=self.log
        )
        matchIndices1, matchIndices2, seps = mesh.match(
            ra1=ra,
            dec1=dec,
            ra2=raOrb,
            dec2=decOrb,
            radius=3.6 / 3600.,
            convertToArray=False,
            maxmatch=0  # 1 = match closest 1, 0 = match all
        )

        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
            print ra[m1], dec[m1], " -> ", s * 3600., " arcsec -> ", raOrb[m2], decOrb[m2]

        self.log.info('completed the ``_extract_phot_from_exposure`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
