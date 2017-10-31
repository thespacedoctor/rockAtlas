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
    
