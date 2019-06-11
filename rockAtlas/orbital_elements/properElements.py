#!/usr/local/bin/python
# encoding: utf-8
"""
*Tools for ingest and manipulation of the ast-dys2 proper elements database file*

:Author:
    David Young

:Date Created:
    September 3, 2018
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
import urllib2
import gzip
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables


class properElements():
    """
    *The worker class for the properElements module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

        To initiate a properElements object, use the following:

        .. code-block:: python

            from rockAtlas.orbital_elements import properElements
            elements = properElements(
                log=log,
                settings=settings
            )
            elements.refresh()
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'properElements' object")
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

        return None

    def refresh(self):
        """
        *refresh the orbital elements in the proper_elements database table*

        **Return:**
            - None

        **Usage:**

            See class docstring
        """
        self.log.debug('starting the ``refresh`` method')

        proper_elements_file = self._download_proper_elements()
        properElementsDictList = self._parse_proper_elements_database_file(
            proper_elements_file)
        self._import_proper_elements_to_database(properElementsDictList)

        self.log.debug('completed the ``refresh`` method')
        return None

    def _download_proper_elements(
            self):
        """*download the proper elements database file*

        **Key Arguments:**
            - ``proper_elements_file`` -- path to the downloaded proper elements database file
        """
        self.log.debug('starting the ``_download_proper_elements`` method')

        # DOWNLOAD PROPER ELEMENTS DATABASE FILE
        url = self.settings["astdys2"]["synth_proper_elements_url"]
        print "Downloading orbital elements from '%(url)s'" % locals()

        response = urllib2.urlopen(url)
        data = response.read()
        proper_elements_file = "/tmp/proper_elements.dat"
        file_ = open(proper_elements_file, 'w')
        file_.write(data)
        file_.close()

        print "Finished downloading orbital elements" % locals()

        self.log.debug('completed the ``_download_proper_elements`` method')
        return proper_elements_file

    def _parse_proper_elements_database_file(
            self,
            proper_elements_file):
        """*parse proper elements database file*

        **Key Arguments:**
            - ``proper_elements_file`` -- path to the downloaded proper elements database file

        **Return:**
            - ``properElementsDictList`` -- the proper elements database parsed as a list of dictionaries
        """
        self.log.debug(
            'starting the ``_parse_proper_elements_database_file`` method')

        print "Parsing the proper elements file"

        with open(proper_elements_file, 'r') as f:
            thisData = f.read()

        properElementsDictList = []

        lines = thisData.split("\n")
        for l in lines[2:]:

            d = {}

            l = l.split()
            if len(l) < 3:
                continue

            # PARSE THE LINE FROM astorb.dat (UNNEEDED VALUES COMMENTED OUT)
            d["name"] = l[0]
            try:
                d["mpc_number"] = int(l[0])
            except:
                d["mpc_number"] = None
            d["abs_magnitude"] = float(l[1])
            d["a"] = float(l[2])
            d["e"] = float(l[3])
            d["sin_i"] = float(l[4])
            d["n_mean_proper_motion_deg_per_yr"] = float(l[5])
            d["g_frequency_arcsec_per_yr"] = float(l[6])
            d["s_frequency_arcsec_per_yr"] = float(l[7])
            d["lce_1e6"] = float(l[8])
            d["integration_time_1e6_yr"] = float(l[9])

            properElementsDictList.append(d)

        print "Finshed parsing the proper elements file"

        self.log.debug(
            'completed the ``_parse_proper_elements_database_file`` method')
        return properElementsDictList

    def _import_proper_elements_to_database(
            self,
            properElementsDictList):
        """*import the proper element to database*

        **Key Arguments:**
            - ``properElementsDictList`` -- the proper element database parsed as a list of dictionaries

        **Return:**
            - None
        """
        self.log.debug(
            'starting the ``_import_proper_elements_to_database`` method')

        print "Refreshing the proper element database table"

        dbSettings = self.settings["database settings"]["atlasMovers"]

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            dictList=properElementsDictList,
            dbTableName="proper_elements",
            uniqueKeyList=["name"],
            dateModified=True,
            batchSize=10000,
            replace=True,
            dbSettings=dbSettings
        )

        print "Finished refreshing the proper elements database table"

        self.log.debug(
            'completed the ``_import_proper_elements_to_database`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
