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
    
    Commands:
        bookkeeping           update and clean database tables, perform essential bookkeeping tasks
        astorb                download astorb.dat orbital elements file and update the orbital elements database table
    
    Options:
        init                  setup the rockAtlas settings file for the first time
        -h, --help            show this help message
        -v, --version         show version
        -s, --settings        the settings file
        -f, --full            a full update (not just recently changed exposures and sources)
    

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


    

