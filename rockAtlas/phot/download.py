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
import codecs
from fundamentals import tools
from subprocess import Popen, PIPE, STDOUT
from fundamentals.mysql import readquery
from fundamentals import fmultiprocess
from fundamentals.mysql import writequery
from fundamentals.files import recursive_directory_listing
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
import pymysql as ms
from rockAtlas.bookkeeping import bookkeeper
import shutil


class download():
    """
    *The worker class for the download module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a download object, and download the next 5 days worth of ATLAS data from Hawaii use the following:

        .. code-block:: python 

            from rockAtlas.phot import download
            data = download(
                log=log,
                settings=settings
            )
            data.get(days=5)   
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

        self._remove_processed_data()

        archivePath = self.settings["atlas archive path"]
        mjds = self._determine_mjds_to_download(days=days)

        if len(mjds) == 0:
            return

        dbConn = self.atlasMoversDBConn

        # DOWNLOAD THE DATA IN PARALLEL
        results = fmultiprocess(log=self.log, function=self._download_one_night_of_atlas_data,
                                inputArray=mjds, archivePath=archivePath)

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

        bk = bookkeeper(
            log=self.log,
            settings=self.settings,
            fullUpdate=False
        )
        bk.clean_all()

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
            archivePath):
        """*summary of function*

        **Key Arguments:**
            - ``mjd`` -- the mjd of the night of data to download
            - ``archivePath`` -- the path to the root of the local archive
            - ``dbConn`` -- connector for the atlas movers database            
        """

        # SETUP A DATABASE CONNECTION FOR THE remote database
        host = self.settings["database settings"]["atlasMovers"]["host"]
        user = self.settings["database settings"]["atlasMovers"]["user"]
        passwd = self.settings["database settings"]["atlasMovers"]["password"]
        dbName = self.settings["database settings"]["atlasMovers"]["db"]
        try:
            sshPort = self.settings["database settings"][
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
            charset='utf8'
        )
        thisConn.autocommit(True)

        cmd = "rsync -avzL --include='*.dph' --include='*.meta' --include='*/' --exclude='*' dyoung@atlas-base-adm01.ifa.hawaii.edu:/atlas/red/02a/%(mjd)s %(archivePath)s/02a/" % locals(
        )

        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if len(stderr):
            print 'error in rsyncing MJD %(mjd)s data: %(stderr)s' % locals()
            return None

        cmd = "rsync -avzL --include='*.dph' --include='*.meta' --include='*/' --exclude='*' dyoung@atlas-base-adm01.ifa.hawaii.edu:/atlas/red/01a/%(mjd)s %(archivePath)s/01a/" % locals(
        )
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        if len(stderr):
            print 'error in rsyncing MJD %(mjd)s data: %(stderr)s' % locals()
            return None

        theseFiles = recursive_directory_listing(
            log=self.log,
            baseFolderPath="%(archivePath)s/02a/%(mjd)s" % locals(),
            whatToList="files"  # all | files | dirs
        )
        theseFiles += recursive_directory_listing(
            log=self.log,
            baseFolderPath="%(archivePath)s/01a/%(mjd)s" % locals(),
            whatToList="files"  # all | files | dirs
        )

        metaFilenames = []
        metaFilenames[:] = [(os.path.splitext(os.path.basename(m))[
            0], m) for m in theseFiles if "meta" in m]

        metaDict = {}
        for m in metaFilenames:
            metaDict[m[0]] = m[1]

        sqlQuery = u"""
            select expname from atlas_exposures where floor(mjd) = %(mjd)s 
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=thisConn
        )

        dbExps = []
        dbExps[:] = [r["expname"]for r in rows]

        missingMeta = []
        missingMeta[:] = [m for m in metaDict.keys() if m not in dbExps]

        fitskw = {
            "MJD-OBS": "mjd",
            "OBJECT": "atlas_object_id",
            "RA": "raDeg",
            "DEC": "decDeg",
            "FILTER": "filter",
            "EXPTIME": "exp_time",
            "OBSNAME": "expname"
        }

        allData = []
        for m in missingMeta:

            pathToReadFile = metaDict[m]
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToReadFile,))
                readFile = codecs.open(
                    pathToReadFile, encoding='utf-8', mode='r')
                thisData = readFile.read()
                readFile.close()
            except IOError, e:
                message = 'could not open the file %s' % (pathToReadFile,)
                self.log.critical(message)
                raise IOError(message)

            fitsDict = {}
            for l in thisData.split("\n"):
                kw = l.split("=")[0].strip()
                if kw in fitskw.keys() and kw not in fitsDict.keys():
                    fitsDict[fitskw[kw]] = l.split(
                        "=")[1].split("/")[0].strip().replace("'", "")

            if len(fitsDict) == 7:
                allData.append(fitsDict)

        insert_list_of_dictionaries_into_database_tables(
            dbConn=thisConn,
            log=self.log,
            dictList=allData,
            dbTableName="atlas_exposures",
            dateModified=True,
            batchSize=2500,
            replace=True
        )

        thisConn.close()

        return str(int(mjd))

    def _remove_processed_data(
            self):
        """*remove processed data*
        """
        self.log.info('starting the ``_remove_processed_data`` method')

        archivePath = self.settings["atlas archive path"]

        from fundamentals.mysql import readquery
        sqlQuery = u"""
            SELECT DISTINCT
    FLOOR(mjd) as mjd
FROM
    atlas_exposures
WHERE
    local_data = 1 AND dophot_match > 0
        AND FLOOR(mjd) NOT IN (SELECT 
            *
        FROM
            (SELECT DISTINCT
                FLOOR(mjd)
            FROM
                atlas_exposures
            WHERE
                local_data = 1 AND dophot_match = 0) AS a);
        """ % locals()
        mjds = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        oldMjds = []
        oldMjds[:] = [str(int(o["mjd"])) for o in mjds]

        for m in oldMjds:
            for i in ["01a", "02a"]:
                datapath = archivePath + "/%(i)s/%(m)s" % locals()
                try:
                    shutil.rmtree(datapath)
                except:
                    self.log.warning(
                        "The path %(datapath)s does not exist - no need to delete" % locals())

        mjdString = (',').join(oldMjds)

        sqlQuery = """update  atlas_exposures set local_data = 0 where floor(mjd) in (%(mjdString)s) and dophot_match = 1""" % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        self.log.info('completed the ``_remove_processed_data`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
