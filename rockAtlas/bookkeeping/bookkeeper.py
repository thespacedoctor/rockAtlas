#!/usr/bin/env python
# encoding: utf-8
"""
*Some database bookkeeping services for the ATLAS Movers database*

:Author:
    David Young

:Date Created:
    October 27, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import readquery
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
from HMpTy.mysql import add_htm_ids_to_mysql_database_table
from astrocalc.times import now as mjdnow
from fundamentals.mysql import directory_script_runner

class bookkeeper():
    """
    *The worker class for the bookkeeper module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``fullUpdate`` -- a full update (not just recently changed exposures and sources)

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a bookkeeper object, use the following:

        .. code-block:: python 

            from rockAtlas.bookkeeping import bookkeeper
            bk = bookkeeper(
                log=log,
                settings=settings,
                fullUpdate=False
            )
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,
            fullUpdate=False
    ):
        self.log = log
        log.debug("instansiating a new 'bookkeeper' object")
        self.settings = settings
        # xt-self-arg-tmpx

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
        self.fullUpdate = fullUpdate

        return None

    def clean_all(self):
        """
        *clean and sync all the bookkeeping tables*

        **Return:**
            - ``bookkeeper``

        **Usage:**

            .. code-block:: python 

                from rockAtlas.bookkeeping import bookkeeper
                bk = bookkeeper(
                    log=log,
                    settings=settings,
                    fullUpdate=False
                )
                bk.clean_all()
        """
        self.log.debug('starting the ``get`` method')

        if self.fullUpdate:
            recent = False
        else:
            recent = True

        self.import_new_atlas_pointings(recent)
        self._run_bookkeeping_sql_scripts()

        self.log.debug('completed the ``get`` method')
        return bookkeeper

    def import_new_atlas_pointings(
            self,
            recent=False):
        """
        *Import any new ATLAS pointings from the atlas3/atlas4 databases into the ``atlas_exposures`` table of the Atlas Movers database*

        **Key Arguments:**
            - ``recent`` -- only sync the most recent 2 weeks of data (speeds things up)

        **Return:**
            - None

         **Usage:**

            .. code-block:: python

                from rockAtlas.bookkeeping import bookkeeper
                bk = bookkeeper(
                    log=log,
                    settings=settings
                )
                bk.import_new_atlas_pointings()
        """
        self.log.debug('starting the ``import_new_atlas_pointings`` method')

        if recent:
            mjd = mjdnow(
                log=self.log
            ).get_mjd()
            recent = mjd - 14
            recent = " mjd_obs > %(recent)s " % locals()
        else:
            recent = "1=1"

        # SELECT ALL OF THE POINTING INFO REQUIRED FROM THE ATLAS3 DATABASE
        sqlQuery = u"""
            SELECT
                `expname`,
                `dec` as `decDeg`,
                `exptime` as `exp_time`,
                `filter`,
                `mjd_obs` as `mjd`,
                `ra` as `raDeg`,
                if(mjd_obs<57855.0,mag5sig-0.75,mag5sig) as `limiting_magnitude`,
                `object` as `atlas_object_id` from atlas_metadata where %(recent)s and object like "TA%%" order by mjd_obs desc;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlas3DbConn,
            quiet=False
        )

        dbSettings = self.settings["database settings"]["atlasMovers"]

        # TIDY RESULTS BEFORE IMPORT
        entries = list(rows)

        if len(rows) > 0:
            # ADD THE NEW RESULTS TO THE atlas_exposures TABLE
            insert_list_of_dictionaries_into_database_tables(
                dbConn=self.atlasMoversDBConn,
                log=self.log,
                dictList=entries,
                dbTableName="atlas_exposures",
                uniqueKeyList=["expname"],
                dateModified=False,
                batchSize=10000,
                replace=True,
                dbSettings=dbSettings
            )

        recent = recent.replace("mjd_obs", "mjd")

        # SELECT ALL OF THE POINTING INFO REQUIRED FROM THE ATLAS4 DATABASE
        sqlQuery = u"""
            SELECT
                `obs` as `expname`,
                `dec` as `decDeg`,
                `texp` as `exp_time`,
                `filt` as `filter`,
                `mjd`,
                `ra` as `raDeg`,
                `mag5sig` as `limiting_magnitude`,
                `obj` as `atlas_object_id` from atlas_metadataddc where %(recent)s and obj like "TA%%" order by mjd desc;
        """ % locals()

        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlas4DbConn,
            quiet=False
        )

        # TIDY RESULTS BEFORE IMPORT
        entries = list(rows)

        if len(rows) > 0:
            # ADD THE NEW RESULTS TO THE atlas_exposures TABLE
            insert_list_of_dictionaries_into_database_tables(
                dbConn=self.atlasMoversDBConn,
                log=self.log,
                dictList=entries,
                dbTableName="atlas_exposures",
                uniqueKeyList=["expname"],
                dateModified=False,
                batchSize=10000,
                replace=True,
                dbSettings=dbSettings
            )

        # APPEND HTMIDs TO THE atlas_exposures TABLE
        add_htm_ids_to_mysql_database_table(
            raColName="raDeg",
            declColName="decDeg",
            tableName="atlas_exposures",
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            primaryIdColumnName="primaryId"
        )

        print "ATLAS pointings synced between ATLAS3/ATLAS4 databases and the ATLAS Movers `atlas_exposures` database table"

        self.log.debug('completed the ``import_new_atlas_pointings`` method')
        return None

    def _run_bookkeeping_sql_scripts(
            self):
        """*run bookkeeping sql scripts*
        """
        self.log.debug('starting the ``_run_bookkeeping_sql_scripts`` method')

        moduleDirectory = os.path.dirname(__file__)
        mysqlScripts = moduleDirectory + "/mysql"

        directory_script_runner(
            log=self.log,
            pathToScriptDirectory=mysqlScripts,
            databaseName=self.settings[
                "database settings"]["atlasMovers"]["db"],
            force=True,
            loginPath=self.settings["database settings"][
                "atlasMovers"]["loginPath"],
            waitForResult=True,
            successRule=False,
            failureRule=False
        )

        self.log.debug('completed the ``_run_bookkeeping_sql_scripts`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
