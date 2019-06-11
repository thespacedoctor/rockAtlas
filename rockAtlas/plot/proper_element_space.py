#!/usr/local/bin/python
# encoding: utf-8
"""
*Plot SSObjects in Proper Element Space*

:Author:
    David Young

:Date Created:
    September  3, 2018
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class proper_element_space():
    """
    *The worker class for the proper_element_space module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a proper_element_space object, use the following:

        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this class
            - add a tutorial about ``proper_element_space`` to documentation
            - create a blog post about what ``proper_element_space`` does

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
        log.debug("instansiating a new 'proper_element_space' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

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

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def get(self):
        """
        *get the proper_element_space object*

        **Return:**
            - ``proper_element_space``

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

        proper_element_space = None

        self.log.debug('completed the ``get`` method')
        return proper_element_space

    def get_asteroid_data(
            self):
        """*query the S4 database for the asteroid data required to plot asteroids in proper element space*

        **Key Arguments:**
            # -

        **Return:**
            - ``ssobjectData`` -- the SSObject data matched against their proper elements

        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - write a command-line tool for this method
                - update package tutorial with command-line tool info if needed

            .. code-block:: python 

                usage code 

        """
        self.log.debug('starting the ``get_asteroid_data`` method')

        from fundamentals.mysql import readquery
        sqlQuery = u"""
            SELECT 
                phase_curve_G_o, a, e, sin_i
            FROM
                proper_elements p,
                atlas_objects a
            WHERE
                phase_curve_G_o is not null and phase_curve_G_err_o < 0.2 and 
                a.mpc_number = p.mpc_number
                    AND p.mpc_number IS NOT NULL;
        """ % locals()
        ssobjectData = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.atlasMoversDBConn,
        )

        self.log.debug('completed the ``get_asteroid_data`` method')
        return ssobjectData

    def plot_asteroids(
            self,
            ssobjectData):
        """*plot the asteroids in proper element space*

        **Key Arguments:**
            - ``ssobjectData`` -- the SSObject data matched against their proper elements

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
        self.log.debug('starting the ``plot_asteroids`` method')

        import numpy as np
        import matplotlib.pyplot as plt

        a = []
        a[:] = [row["a"] for row in ssobjectData]
        sin_i = []
        sin_i[:] = [row["sin_i"] for row in ssobjectData]
        e = []
        e[:] = [row["e"] for row in ssobjectData]
        # gc = []
        # gc[:] = [row["phase_curve_G_c"] for row in ssobjectData]
        go = []
        go[:] = [row["phase_curve_G_o"] for row in ssobjectData]

        # plt.scatter(a, sin_i, s=area, c=colors, alpha=0.15)
        cmap = plt.get_cmap('jet', 8)

        fig, axes = plt.subplots(1, 3, figsize=(12, 5))
        # fig.autolayout = False
        # fig.tight_layout = False

        (ax1, ax2, ax3) = axes.flat

        im = ax1.scatter(a, sin_i, c=go, s=.05, alpha=0.5,
                         cmap=cmap,  vmin=-0.1, vmax=0.6)
        ax1.clear()
        ax1.scatter(a, sin_i, c=go, s=.05, alpha=0.15, edgecolors=None,
                    cmap=cmap,  vmin=-0.1, vmax=0.6)
        ax1.set_ylim((-0.01, 0.6))
        ax1.set_xlabel("proper a (AU)")
        ax1.set_ylabel("proper sin(i)")

        ax2.scatter(e, sin_i, c=go, s=.05, alpha=0.15, edgecolors=None,
                    cmap=cmap,  vmin=-0.1, vmax=0.6)
        ax2.set_ylim((-0.01, 0.6))
        ax2.set_xlim((-0.01, 0.4))
        ax2.set_xlabel("proper e (AU)")
        ax2.set_ylabel("proper sin(i)")

        ax3.scatter(a, e, c=go, s=.05, alpha=0.15, edgecolors=None,
                    cmap=cmap,  vmin=-0.1, vmax=0.6)
        ax3.set_ylim((-0.01, 0.4))

        ax3.set_xlabel("proper a (AU)")
        ax3.set_ylabel("proper e")

        fig.subplots_adjust(left=None, bottom=None, right=None, top=None,
                            wspace=0.3, hspace=None)
        cb = fig.colorbar(im, ax=axes.ravel().tolist(), alpha=1.0)
        cb.ax.tick_params(axis=u'both', which=u'both', length=0)

        title = "ATLAS SSObjects Proper Element Plots"
        # plt.title(title)
        fileName = title.replace(" ", "_") + ".pdf"
        # mdLog.write("""![%s_plot]\n\n[%s_plot]: %s\n\n""" % (title.replace(" ", "_"), title.replace(" ", "_"), fileName,))
        plt.savefig(fileName)
        plt.clf()  # clear figure

        self.log.debug('completed the ``plot_asteroids`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
