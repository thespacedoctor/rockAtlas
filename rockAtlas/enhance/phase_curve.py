#!/usr/local/bin/python
# encoding: utf-8
"""
*Calculate parameters relating to the phase curves of the atlas moving objects*

:Author:
    David Young

:Date Created:
    April 30, 2018
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import readquery, writequery
from scipy.optimize import curve_fit
import numpy as np
from fundamentals import fmultiprocess
from fundamentals.mysql import database
from fundamentals.mysql import insert_list_of_dictionaries_into_database_tables
from datetime import datetime, date, time
# OR YOU CAN REMOVE THE CLASS BELOW AND ADD A WORKER FUNCTION ... SNIPPET TRIGGER BELOW
# xt-worker-def


class phase_curve():
    """
    *The worker class for the phase_curve module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

        To initiate a phase_curve object, use the following:

        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this class
            - add a tutorial about ``phase_curve`` to documentation
            - create a blog post about what ``phase_curve`` does

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
        log.debug("instansiating a new 'phase_curve' object")
        self.settings = settings
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

    # use the tab-trigger below for new method
    def calculate(
            self,
            objectid=False):
        """*calculate the phase curve parameters for all objects in the database with new photometry*

        **Key Arguments:**
            - ``objectid`` -- the ID of an individual SSObject to update. Default *False*

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
        self.log.debug('starting the ``calculate`` method')

        for fil in ['o', 'c']:

            remaining = self.count_phase_curves_remaining(
                filter=fil, objectid=objectid)
            objects = [1]
            batchSize = 1000
            while len(objects) > 0:

                print "%(remaining)s asteroids still need to have their phase-curve parameters updated in the %(fil)s-band" % locals()
                objects = self.get_objects(
                    filter=fil, batchSize=batchSize, objectid=objectid)
                remaining -= batchSize

                # DEFINE AN INPUT ARRAY
                results = fmultiprocess(log=self.log, function=self.calculate_phase_curve_parameters,
                                        inputArray=objects, poolSize=False, timeout=600, filter=fil)

                if len(results):
                    # USE dbSettings TO ACTIVATE MULTIPROCESSING
                    insert_list_of_dictionaries_into_database_tables(
                        dbConn=self.atlasMoversDBConn,
                        log=self.log,
                        dictList=results,
                        dbTableName="atlas_objects",
                        uniqueKeyList=["orbital_elements_id"],
                        dateModified=True,
                        dateCreated=False,
                        batchSize=20000,
                        replace=True,
                        dbSettings=self.settings[
                            "database settings"]["atlasMovers"]
                    )
                if objectid:
                    objects = []

        self.log.debug('completed the ``calculate`` method')
        return None

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def update_database(self):
        """
        *get the phase_curve object*

        **Return:**
            - ``phase_curve``

        **Usage:**
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this method
            - update the package tutorial if needed

        .. code-block:: python

            usage code
        """
        self.log.debug('starting the ``get`` method')

        orbital_elements_ids = self.get_objects()

        self.log.debug('completed the ``get`` method')
        return phase_curve

    def get_objects(
            self,
            filter,
            batchSize=1000,
            objectid=False):
        """*get the ids of the moving objects that require phase curve parameter updates from the database*

        **Key Arguments:**
            - ``filter`` -- the passband of the photometry to return
            - ``batchSize`` -- the maximum number of sources to return at a time. Default *1000*
            - ``objectid`` -- the ID of an individual SSObject to update. Default *False*

        **Return:**
            - ``orbital_elements_ids`` -- a list of the object orbital element database IDs for which phase curve info needs updated


        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - write a command-line tool for this method
                - update package tutorial with command-line tool info if needed

            .. code-block:: python

                usage code

        """
        self.log.debug('starting the ``get_objects`` method')

        if objectid:
            try:
                objectid = int(objectid)
                whereclause = "mpc_number = %(objectid)s" % locals()
            except:
                whereclause = 'name = "%(objectid)s"' % locals()
        else:
            whereclause = "detection_count_%(filter)s > 50 and  (phase_curve_refresh_date_%(filter)s is null or last_photometry_update_date_%(filter)s > phase_curve_refresh_date_%(filter)s)" % locals()

        sqlQuery = u"""
            SELECT orbital_elements_id FROM atlas_objects where %(whereclause)s limit %(batchSize)s;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        orbital_elements_ids = []
        orbital_elements_ids[:] = [r["orbital_elements_id"] for r in rows]

        self.log.debug('completed the ``get_objects`` method')
        return orbital_elements_ids

    # use the tab-trigger below for new method
    def calculate_phase_curve_parameters(
            self,
            orbital_elements_id,
            filter):
        """*calculate phase curve parameters*

        **Key Arguments:**
            - ``orbital_elements_id`` -- the orbital element ID to calculate phase curve parameters for.
            - ``filter`` -- the passband of the photometry to return

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
        self.log.debug(
            'starting the ``calculate_phase_curve_parameters`` method')

        dbSettings = self.settings["database settings"]["atlasMovers"]

        # SETUP ALL DATABASE CONNECTION
        dbConn = database(
            log=self.log,
            dbSettings=dbSettings
        ).connect()

        # GRAB ASTEROID MAGS WITH OUTLIERS CLIPPED
        sqlQuery = u"""
            select * from (SELECT
        (m - o.apparent_mag) as magDiff, phase_angle, m - 5*log10(heliocentric_distance*observer_distance) as reduced_mag, m, dfitmag as err, a.mjd, o.mpc_number, o.object_name, o.orbital_elements_id
    FROM
        dophot_photometry d,
        orbfit_positions o,
        atlas_exposures a
WHERE
        filter = '%(filter)s'
            AND d.orbfit_postions_id = o.primaryId
            AND a.expname = d.expname
            AND o.orbital_elements_id = %(orbital_elements_id)s
            AND sep_rank = 1
            AND dfitmag != 0) as a
INNER JOIN (SELECT
        AVG(m - o.apparent_mag) as avrg, STDDEV(m - o.apparent_mag) as stdv
    FROM
        dophot_photometry d,
        orbfit_positions o,
        atlas_exposures a
    WHERE
        filter = '%(filter)s'
            AND d.orbfit_postions_id = o.primaryId
            AND a.expname = d.expname
            AND o.orbital_elements_id = %(orbital_elements_id)s
            AND sep_rank = 1
            AND dfitmag != 0) as b
on a.magDiff BETWEEN b.avrg-2*b.stdv AND b.avrg+2*b.stdv;
        """ % locals()

        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=dbConn,
            quiet=False
        )

        if len(rows) == 0:
            H = None
            G = None
            Herr = None
            Gerr = None
        else:
            name = rows[0]["object_name"]
            x = np.array([r["phase_angle"] for r in rows])
            y = np.array([r["reduced_mag"] for r in rows])
            yerr = np.array([r["err"] for r in rows])
            mjds = [r["mjd"] for r in rows]
            maxmjd = max(mjds)

            # PHASE CURVE FITTING
            # FIRST PERFORM HELIOCENTRIC CORRECTION -- THIS HAS BEEN DONE WITHIN THE DATABASE QUERY
            # CONVERT PHASE ANGLE TO RADIANS
            phase_radians = np.radians(x)
            y = np.array(y)
            # Fit the H, G function to sparsely sampled photometry
            # SET UP INITIAL ESTIMATES
            Ho_est = min(y)
            G_est = 0.5
            #popt, pcov = curve_fit(magnitude_phase_func,
            #                       phase_radians, y, p0=[Ho_est, G_est])
            #perr = np.sqrt(np.diag(pcov))
            try:
                popt, pcov = curve_fit(magnitude_phase_func,
                                       phase_radians, y, p0=[Ho_est, G_est], maxfev = 1000)
                perr = np.sqrt(np.diag(pcov))
            except:
                self.log.warning(
                    "Could not determine phase-curve parameters for %(name)s - what went wrong?" % locals())
                popt = [None, None]
                perr = [None, None]

            if popt[1] == 1.:
                popt = [None, None]
                perr = [None, None]

            H = popt[0]
            G = popt[1]
            Herr = perr[0]
            Gerr = perr[1]

        print "FILTER: %(filter)s, H: %(H)s, G: %(G)s" % locals()

        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")

        results = {
            "phase_curve_H_%(filter)s" % locals(): H,
            "phase_curve_H_err_%(filter)s" % locals(): Herr,
            "phase_curve_G_%(filter)s" % locals(): G,
            "phase_curve_G_err_%(filter)s" % locals(): Gerr,
            "orbital_elements_id": orbital_elements_id,
            "phase_curve_refresh_date_%(filter)s" % locals(): now,
        }

        return results

    def update_atlas_object_table(
            self):
        """*update atlas object table*

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
        self.log.debug('starting the ``update_atlas_object_table`` method')

        # UPDATE THE ATLAS OBJECTS TABLE BEFORE DOING ANY MORE WORK -
        # `update_atlas_objects` IS A FUNCTION WITHIN THE ATLAS OBJECTS
        # DATABASE
        sqlQuery = """CALL update_atlas_objects""" % locals()
        writequery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn
        )

        self.log.debug('completed the ``update_atlas_object_table`` method')
        return None

    # use the tab-trigger below for new method
    def count_phase_curves_remaining(
            self,
            filter,
            objectid=False):
        """*count phase curves remaining*

        **Key Arguments:**
            - ``filter`` -- the passband of the photometry to return
            - ``count`` -- the number of asteroids still requiring phase-curve parameter updates
            - ``objectid`` -- the ID of an individual SSObject to update. Default *False*

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
        self.log.debug('starting the ``count_phase_curves_remaining`` method')

        if objectid:
            try:
                objectid = int(objectid)
                whereclause = "mpc_number = %(objectid)s" % locals()
            except:
                whereclause = 'name = "%(objectid)s"' % locals()
        else:
            whereclause = "detection_count_%(filter)s > 50 and  (phase_curve_refresh_date_%(filter)s is null or last_photometry_update_date_%(filter)s > phase_curve_refresh_date_%(filter)s)" % locals()

        sqlQuery = u"""
            SELECT count(*) as count FROM atlas_objects where %(whereclause)s;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
            quiet=False
        )

        self.log.debug('completed the ``count_phase_curves_remaining`` method')
        return rows[0]["count"]

    # use the tab-trigger below for new method
    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx


def magnitude_phase_func(alpha, H, G):
    '''
    Implementation of the two-parameter H, G magnitude system definition of Bowell et al. 1989,
    as used by the IAU from 1985 until ~2013.

    :param alpha: solar phrase angle: the angle between the Sun and the Earth as seen from the minor planet,
                  at the time of observation (radians)
    :param H: absolute magnitude in specific filter of photometry supplied. (magnitude)
              Formally, the mean brightness at 0 deg phase angle, when observed at 1 au from both the Sun and the Earth
    :param G: slope parameter, describes shape of magnitude phase function. (unitless)
    :return: reduced magnitude,
    '''

    phi_one_s = 1 - (0.986 * np.sin(alpha) / (0.119 + 1.1341 *
                                              np.sin(alpha) - 0.754 * np.sin(alpha) ** 2))
    phi_one_l = np.exp(-3.332 * np.tan(0.5 * alpha) ** 0.631)

    phi_two_s = 1 - (0.238 * np.sin(alpha) / (0.119 + 1.1341 *
                                              np.sin(alpha) - 0.754 * np.sin(alpha) ** 2))
    phi_two_l = np.exp(-1.862 * np.tan(0.5 * alpha) ** 1.218)

    w = np.exp(-90.56 * np.tan(0.5 * alpha)**2)

    phi_one = w * phi_one_s + (1 - w) * phi_one_l
    phi_two = w * phi_two_s + (1 - w) * phi_two_l

    with np.errstate(all='ignore'):
        V_alpha = H - 2.5 * np.log10((1 - G) * phi_one + G * phi_two)

    return V_alpha
