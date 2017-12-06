#!/usr/local/bin/python
# encoding: utf-8
"""
*Tools for ingest and manipulation of the astorb.dat orbital elements database file*

:Author:
    David Young

:Date Created:
    October 31, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
import urllib2
import gzip
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables


class astorb():
    """
    *The worker class for the astorb module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a astorb object, use the following:

        .. code-block:: python 

            from rockAtlas.orbital_elements import astorb
            elements = astorb(
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
        log.debug("instansiating a new 'astorb' object")
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
        *refresh the orbital elements in the astorb.dat database table*

        **Return:**
            - ``astorb``

        **Usage:**

            See class docstring
        """
        self.log.info('starting the ``refresh`` method')

        astorbgz = self._download_astorb()
        astorbDictList = self._parse_astorb_database_file(astorbgz)
        self._import_astorb_to_database(astorbDictList)

        self.log.info('completed the ``refresh`` method')
        return None

    def _download_astorb(
            self):
        """*download the astorb database file*

        **Key Arguments:**
            - ``astorbgz`` -- path to the downloaded astorb database file
        """
        self.log.info('starting the ``_download_astorb`` method')

        # DOWNLOAD ASTORB
        url = self.settings["astorb"]["url"]
        print "Downloading orbital elements from '%(url)s'" % locals()

        response = urllib2.urlopen(url)
        data = response.read()
        astorbgz = "/tmp/astorb.dat.gz"
        file_ = open(astorbgz, 'w')
        file_.write(data)
        file_.close()

        print "Finished downloading orbital elements" % locals()

        self.log.info('completed the ``_download_astorb`` method')
        return astorbgz

    def _parse_astorb_database_file(
            self,
            astorbgz):
        """* parse astorb database file*

        **Key Arguments:**
            - ``astorbgz`` -- path to the downloaded astorb database file

        **Return:**
            - ``astorbDictList`` -- the astorb database parsed as a list of dictionaries
        """
        self.log.info('starting the ``_parse_astorb_database_file`` method')

        print "Parsing the astorb.dat orbital elements file"

        with gzip.open(astorbgz, 'rb') as f:
            thisData = f.read()

        astorbDictList = []

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

            # CONVERT ASTORB DATABASE LINE TO XEPHEM DATABASE FORMAT
            xephemStr = "%(mpc_number)s %(name)s,e,%(i_inclination_deg)s,%(O_long_asc_node_deg)s,%(o_arg_peri_deg)s,%(a_semimajor_axis)s,0,%(e_eccentricity)s,%(M_mean_anomaly_deg)s,%(epoch_xeph)s,2000.0,%(H_abs_mag)s,%(G_slope)s" % d
            xephemStr = xephemStr.strip()

            d["pyephem_string"] = xephemStr
            d["astorb_string"] = l

            # TIDYUP
            if len(d["mpc_number"]) == 0:
                d["mpc_number"] = None

            for k, v in d.iteritems():
                if v != None and len(v) == 0:
                    d[k] = None

            astorbDictList.append(d)

        print "Finshed parsing the astorb.dat orbital elements file"

        self.log.info('completed the ``_parse_astorb_database_file`` method')
        return astorbDictList

    def _import_astorb_to_database(
            self,
            astorbDictList):
        """*import the astorb orbital elements to database*

        **Key Arguments:**
            - ``astorbDictList`` -- the astorb database parsed as a list of dictionaries

        **Return:**
            - None
        """
        self.log.info('starting the ``_import_astorb_to_database`` method')

        print "Refreshing the orbital elements database table"

        dbSettings = self.settings["database settings"]["atlasMovers"]

        insert_list_of_dictionaries_into_database_tables(
            dbConn=self.atlasMoversDBConn,
            log=self.log,
            dictList=astorbDictList,
            dbTableName="orbital_elements",
            uniqueKeyList=["name"],
            dateModified=True,
            batchSize=10000,
            replace=True,
            dbSettings=dbSettings
        )

        print "Finished refreshing the orbital elements database table"

        self.log.info('completed the ``_import_astorb_to_database`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
