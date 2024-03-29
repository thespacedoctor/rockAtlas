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

Downloading a Cache of ATLAS data
---------------------------------

To download a cache of ATLAS dophot and meta files to work on locally, run ``rockAtlas cache <days>``. So to download 5 days of data:

.. code-block:: bash 
    
    rockAtlas cache 5

The rockAtlas code checks on what the earliest data there is that still requires the dophot files to be read and parsed. Data is download from this day forward. If there is data in the local cache that has already been processed then this data is removed from the cache to create space for new data.

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

Note, for a known moving object to be included in the exposure match it must be flagged with ``include_in_match`` in the ``orbital_elements`` database table.

Orbfit Positions
----------------

To tighten up the positions of moving objects found by PyEphem to be located in the neighbourhood of an ATLAS exposure, and reject those movers not found exactly within the exposure FOV, run the command:

.. code-block:: bash 
    
    rockAtlas orbfit

Again the running log printed to stdout will give you an idea of how long it will take to process all of the ATLAS exposures that have already been process using PyEphem but still need orbfit to be run.

To only generate orbfit positions for a single ATLAS exposure run the command with the `--one` flag:

.. code-block:: bash 
    
    rockAtlas orbfit --one

dophot Matching
---------------

To parse the local dophot files that have orbfit estimated known asteriod positions generated, run the command:

.. code-block:: bash 
    
    rockAtlas dophot

This will open the dophot files and crossmatch the reported dections with the positions estimated by orbfit. Use the "dophot search radius" parameter in the settings file to adjust the crossmatch tolerance. All matches (often multiple matches for a single orbfit estimated position in crowded fields) are recorded in the ``dophot_matches`` database table.




    
