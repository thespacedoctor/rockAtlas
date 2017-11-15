#!/usr/local/bin/python
# encoding: utf-8
"""
*Download requested ATLAS data from Hawaii*

:Author:
    David Young

:Date Created:
    November 13, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from subprocess import Popen, PIPE, STDOUT
from fundamentals.mysql import readquery
from fundamentals import fmultiprocess
from fundamentals.mysql import writequery


# OR YOU CAN REMOVE THE CLASS BELOW AND ADD A WORKER FUNCTION ... SNIPPET TRIGGER BELOW
# xt-worker-def


class download():
    """
    *The worker class for the download module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a download object, use the following:

        .. todo::

            - create cl-util for this class
            - add a tutorial about ``download`` to documentation

        .. code-block:: python 

            from rockAtlas.phot import download
            data = download(
                log=log,
                settings=settings
            )
            data.get()   
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False
    ):
        self.log = log
        log.debug("instansiating a new 'download' object")
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

    def get(
            self,
            days):
        """
        *download a cache of ATLAS nights data*

        **Key Arguments:**
            - ``days`` -- the number of days data to cache locally

        **Return:**
            - None

        **Usage:**

            See class docstring
        """
        self.log.info('starting the ``get`` method')

        archivePath = self.settings["atlas archive path"]
        mjds = self._determine_mjds_to_download(days=days)

        if len(mjds) == 0:
            return

        dbConn = self.atlasMoversDBConn

        # DOWNLOAD THE DATA IN PARALLEL
        results = fmultiprocess(log=self.log, function=self._download_one_night_of_atlas_data,
                                inputArray=mjds, archivePath=archivePath, dbConn=self.atlasMoversDBConn)

        # UPDATE BOOKKEEPING
        mjds = []
        mjds[:] = [r for r in results if r is not None]
        mjds = (',').join(mjds)

        sqlQuery = """update atlas_exposures set local_data = 1 where floor(mjd) in (%(mjds)s)""" % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )

        self.log.info('completed the ``get`` method')
        return None

    def _determine_mjds_to_download(
            self,
            days):
        """*determine which ATLAS nights require to be cached locally*

        **Key Arguments:**
            - ``days`` -- the number of days data to cache locally

        **Return:**
            - ``mjds`` -- a list of the MJDs to be downloaded from the ATLAS datastore in hawaii
        """
        self.log.info('starting the ``_determine_mjds_to_download`` method')

        # COUNT DOWNLOADED NIGHTS
        sqlQuery = u"""
            SELECT DISTINCT
                FLOOR(mjd) AS mjdInt
            FROM
                atlas_exposures
            WHERE
                local_data = 1
        """ % locals()
        mjds = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        if len(mjds) >= int(days):
            print "%(days)s nights of ATLAS data already cached locally" % locals()
            return []

        # RETURN THE REMAINING NIGHT MJDS NEEDING DOWNLOADED
        remainingDownloadCount = int(days) - len(mjds)
        sqlQuery = u"""
            SELECT DISTINCT
                FLOOR(mjd) AS mjdInt
            FROM
                atlas_exposures
            WHERE
                orbfit_positions = 1
                    AND FLOOR(mjd) NOT IN (SELECT 
                        *
                    FROM
                        (SELECT DISTINCT
                            FLOOR(mjd)
                        FROM
                            atlas_exposures
                        WHERE
                            orbfit_positions != 1) AS a) order by mjdInt asc limit %(remainingDownloadCount)s;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        mjds = []
        mjds[:] = [int(r["mjdInt"]) for r in rows]

        self.log.info('completed the ``_determine_mjds_to_download`` method')
        return mjds

    def _download_one_night_of_atlas_data(
            self,
            mjd,
            archivePath,
            dbConn):
        """*summary of function*

        **Key Arguments:**
            - ``mjd`` -- the mjd of the night of data to download
            - ``archivePath`` -- the path to the root of the local archive
            - ``dbConn`` -- connector for the atlas movers database            
        """
        cmd = "rsync -avzL --include='*.dph' --include='*/' --exclude='*' dyoung@atlas-base-adm01.ifa.hawaii.edu:/atlas/red/02a/%(mjd)s %(archivePath)s/02a/" % locals(
        )

        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if len(stderr):
            print 'error in rsyncing MJD %(mjd)s data: %(stderr)s' % locals()
            return None

        cmd = "rsync -avzL --include='*.dph' --include='*/' --exclude='*' dyoung@atlas-base-adm01.ifa.hawaii.edu:/atlas/red/01a/%(mjd)s %(archivePath)s/01a/" % locals(
        )
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if len(stderr):
            print 'error in rsyncing MJD %(mjd)s data: %(stderr)s' % locals()
            return None

        return str(int(mjd))
