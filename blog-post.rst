rockAtlas 
=========================

.. image:: https://readthedocs.org/projects/rockAtlas/badge/
    :target: http://rockAtlas.readthedocs.io/en/latest/?badge
    :alt: Documentation Status

.. image:: https://cdn.rawgit.com/thespacedoctor/rockAtlas/master/coverage.svg
    :target: https://cdn.rawgit.com/thespacedoctor/rockAtlas/master/htmlcov/index.html
    :alt: Coverage Status

*A python package and command-line tools for A suite of tools to pull known solar-system small-body detections out of ATLAS data*.





Command-Line Usage
==================

.. code-block:: bash 
   
    
    Documentation for rockAtlas can be found here: http://rockAtlas.readthedocs.org/en/stable
    
    Usage:
        rockAtlas init
        rockAtlas bookkeeping [-f] [-s <pathToSettingsFile>]
        rockAtlas astorb
        rockAtlas pyephem [-o]
    
    Commands:
        bookkeeping           update and clean database tables, perform essential bookkeeping tasks
        astorb                download astorb.dat orbital elements file and update the orbital elements database table
        pyephem               generate the pyephem positions overlapping the ATLAS exposures in the moving objects database
    
    Options:
        init                  setup the rockAtlas settings file for the first time
        -h, --help            show this help message
        -v, --version         show version
        -s, --settings        the settings file
        -f, --full            a full update (not just recently changed exposures and sources)
        -o, --one             only generate positions for a single pyephem snapshot (few 10s of exposures - useful for testing)
    

Installation
============

The easiest way to install rockAtlas is to use ``pip``:

.. code:: bash

    pip install rockAtlas

Or you can clone the `github repo <https://github.com/thespacedoctor/rockAtlas>`__ and install from a local version of the code:

.. code:: bash

    git clone git@github.com:thespacedoctor/rockAtlas.git
    cd rockAtlas
    python setup.py install

To upgrade to the latest version of rockAtlas use the command:

.. code:: bash

    pip install rockAtlas --upgrade


Documentation
=============

Documentation for rockAtlas is hosted by `Read the Docs <http://rockAtlas.readthedocs.org/en/stable/>`__ (last `stable version <http://rockAtlas.readthedocs.org/en/stable/>`__ and `latest version <http://rockAtlas.readthedocs.org/en/latest/>`__).

Command-Line Tutorial
=====================

Before you begin using rockAtlas you will need to populate some custom settings within the rockAtlas settings file.

To setup the default settings file at ``~/.config/rockAtlas/rockAtlas.yaml`` run the command:

.. code-block:: bash 
    
    rockAtlas init

This should create and open the settings file; follow the instructions in the file to populate the missing settings values (usually given an ``XXX`` placeholder). 

Bookkeeping
-----------

To update the ATLAS Moving Object database tables with recent ATLAS exposures (from last 2 weeks), perform cleanup tasks and to set certain bookkeeping flags run the command:

.. code-block:: bash 
    
    rockAtlas bookkeeping 

or to do a full update (e.g. if the command has not been run in a long time) run the command with the `-f, --full` flag:

.. code-block:: bash 
    
    rockAtlas bookkeeping --full

Orbital Elements Cache
----------------------

rockAtlas caches the orbital elements from `astorb.dat <ftp://ftp.lowell.edu/pub/elgb/astorb.dat.gz>`_ in an ``orbital_elements`` table in the ATLAS Moving Objects database. To update the cache (should be done once a day or so), run the command:

.. code-block:: bash 
    
    rockAtlas astorb

This downloads a fresh copy of astorb.dat, parses it and refreshes the cache in the ``orbital_elements`` table.

PyEphem Positions
-----------------

To generate the PyEphem positions for moving objects in the neighbourhoods of the ATLAS exposures run the command:

.. code-block:: bash 
    
    rockAtlas pyephem

Depending on the backlog of ATLAS exposures this may take minutes .. or days! The running log printed to stdout should give you an idea of how long it will take to generate the positions for all new exposures.

To only generate positions for a single pyephem snapshot (few 10s of exposures) run the command with the `--one` flag:

.. code-block:: bash 
    
    rockAtlas pyephem --one

Orbfit Positions
----------------

To tighten up the positions of moving objects found by PyEphem to be located in the neighbourhood of an ATLAS exposure, and reject those movers not found exactly within the exposure FOV, run the command:

.. code-block:: bash 
    
    rockAtlas orbfit

Again the running log printed to stdout will give you an idea of how long it will take to process all of the ATLAS exposures that have already been process using PyEphem but still need orbfit to be run.

To only generate orbfit positions for a single ATLAS exposure run the command with the `--one` flag:

.. code-block:: bash 
    
    rockAtlas orbfit --one




    

