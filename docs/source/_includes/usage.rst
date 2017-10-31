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
    
