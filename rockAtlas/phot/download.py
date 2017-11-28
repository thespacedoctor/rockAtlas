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
from astrocalc.times import now
import math
from astrocalc.times import conversions


atlasMoversDBConn = False


def _download_one_night_of_atlas_data(
        mjd,
        log,
        archivePath):
    """*summary of function*

    **Key Arguments:**
        - ``mjd`` -- the mjd of the night of data to download
        - ``archivePath`` -- the path to the root of the local archive         
    """

    # SETUP A DATABASE CONNECTION FOR THE remote database
    global atlasMoversDBConn

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
        log=log,
        baseFolderPath="%(archivePath)s/02a/%(mjd)s" % locals(),
        whatToList="files"  # all | files | dirs
    )
    theseFiles += recursive_directory_listing(
        log=log,
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
        log=log,
        sqlQuery=sqlQuery,
        dbConn=atlasMoversDBConn
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
            log.debug("attempting to open the file %s" %
                      (pathToReadFile,))
            readFile = codecs.open(
                pathToReadFile, encoding='utf-8', mode='r')
            thisData = readFile.read()
            readFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (pathToReadFile,)
            log.critical(message)
            raise IOError(message)

        fitsDict = {}
        for l in thisData.split("\n"):
            kw = l.split("=")[0].strip()
            if kw in fitskw.keys() and kw not in fitsDict.keys():
                fitsDict[fitskw[kw]] = l.split(
                    "=")[1].split("/")[0].strip().replace("'", "")

        if len(fitsDict) == 7:
            allData.append(fitsDict)

    if len(allData):
        insert_list_of_dictionaries_into_database_tables(
            dbConn=atlasMoversDBConn,
            log=log,
            dictList=allData,
            dbTableName="atlas_exposures",
            dateModified=True,
            batchSize=10000,
            replace=True
        )

    sqlQuery = """
update atlas_exposures set dev_flag = 1 where dev_flag = 0 and floor(mjd) in (select mjd from day_tracker where dev_flag = 1);
update day_tracker set processed = 1, local_data = 1 where mjd = %(mjd)s;""" % locals(
    )
    writequery(
        log=log,
        sqlQuery=sqlQuery,
        dbConn=atlasMoversDBConn
    )

    return str(int(mjd))


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
            settings=False,
            dev_flag=False
    ):
        self.log = log
        log.debug("instansiating a new 'download' object")
        self.settings = settings
        self.dev_flag = dev_flag

        global atlasMoversDBConn

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
        atlasMoversDBConn = dbConns["atlasMovers"]

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
        self._update_day_tracker_table()
        mjds = self._determine_mjds_to_download(days=days)

        if len(mjds) == 0:
            return

        dbConn = self.atlasMoversDBConn

        # DOWNLOAD THE DATA IN PARALLEL
        results = fmultiprocess(log=self.log, function=_download_one_night_of_atlas_data,
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

        if self.dev_flag:
            dev_flag = "and dev_flag = 1"
        else:
            dev_flag = ''

        # RETURN THE REMAINING NIGHT MJDS NEEDING DOWNLOADED
        remainingDownloadCount = int(days) - len(mjds)
        sqlQuery = u"""
            SELECT DISTINCT mjdInt from (
(SELECT DISTINCT
                FLOOR(mjd) AS mjdInt
            FROM
                atlas_exposures
            WHERE
                local_data = 0 and dophot_match = 0 %(dev_flag)s
UNION ALL
SELECT DISTINCT
                FLOOR(mjd) AS mjdInt
            FROM
                day_tracker
            WHERE
                processed = 0 %(dev_flag)s) as a) where mjdInt not in (SELECT
                        *
                    FROM
                        (SELECT DISTINCT
                            FLOOR(mjd)
                        FROM
                            atlas_exposures
                        WHERE
                            local_data = 1) AS a) order by mjdInt asc limit %(remainingDownloadCount)s;
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

    def _remove_processed_data(
            self):
        """*remove processed data*
        """
        self.log.info('starting the ``_remove_processed_data`` method')

        archivePath = self.settings["atlas archive path"]

        from fundamentals.mysql import readquery
        sqlQuery = u"""
            select mjd from (SELECT DISTINCT
    FLOOR(mjd) as mjd
FROM
    atlas_exposures
WHERE
    local_data = 1 AND dophot_match > 0
UNION ALL
SELECT DISTINCT
    FLOOR(mjd) as mjd
FROM
    day_tracker
WHERE
    local_data = 1) as a
        where mjd NOT IN (SELECT 
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

        if not len(mjds):
            return None

        oldMjds = []
        oldMjds[:] = [str(int(o["mjd"])) for o in mjds]

        for m in oldMjds:
            for i in ["01a", "02a"]:
                datapath = archivePath + "/%(i)s/%(m)s" % locals()
                # shutil.rmtree(datapath)
                try:
                    shutil.rmtree(datapath)
                except:
                    self.log.warning(
                        "The path %(datapath)s does not exist - no need to delete" % locals())
                    sys.exit(0)

        mjdString = (',').join(oldMjds)

        sqlQuery = """
update day_tracker set local_data = 0 where floor(mjd) in (%(mjdString)s);
update  atlas_exposures set local_data = 0 where floor(mjd) in (%(mjdString)s) and dophot_match != 0;""" % locals(
        )
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        self.log.info('completed the ``_remove_processed_data`` method')
        return None

    def _update_day_tracker_table(
            self):
        """* update day tracker table*

        **Key Arguments:**
            # -

        **Return:**
            - None

        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - write a command-line tool for this method
                - update package tutorial with command-line tool info if needed

            .. code-block:: python 

                usage code 

        """
        self.log.info('starting the ``_update_day_tracker_table`` method')

        # YESTERDAY MJD
        mjd = now(
            log=self.log
        ).get_mjd()
        yesterday = int(math.floor(mjd - 1))

        sqlQuery = u"""
            SELECT mjd FROM atlas_moving_objects.day_tracker order by mjd desc limit 1
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )
        highestMjd = int(rows[0]["mjd"])

        converter = conversions(
            log=self.log
        )

        sqlData = []
        for m in range(highestMjd, yesterday):
            # CONVERTER TO CONVERT MJD TO DATE
            utDate = converter.mjd_to_ut_datetime(
                mjd=m,
                sqlDate=True,
                datetimeObject=False
            )
            sqlData.append({
                "mjd": m,
                "ut_date": utDate
            })

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            dictList=sqlData,
            dbTableName="day_tracker",
            uniqueKeyList=["mjd"],
            dateModified=False,
            batchSize=10000,
            replace=True
        )

        self.atlasMoversDBConn.commit()

        self.log.info('completed the ``_update_day_tracker_table`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
