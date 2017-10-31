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




    
