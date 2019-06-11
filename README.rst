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
    

Documentation
=============

Documentation for rockAtlas is hosted by `Read the Docs <http://rockAtlas.readthedocs.org/en/stable/>`__ (last `stable version <http://rockAtlas.readthedocs.org/en/stable/>`__ and `latest version <http://rockAtlas.readthedocs.org/en/latest/>`__).

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


Development
-----------

If you want to tinker with the code, then install in development mode.
This means you can modify the code from your cloned repo:

.. code:: bash

    git clone git@github.com:thespacedoctor/rockAtlas.git
    cd rockAtlas
    python setup.py develop

`Pull requests <https://github.com/thespacedoctor/rockAtlas/pulls>`__
are welcomed!

Sublime Snippets
~~~~~~~~~~~~~~~~

If you use `Sublime Text <https://www.sublimetext.com/>`_ as your code editor, and you're planning to develop your own python code with rockAtlas, you might find `my Sublime Snippets <https://github.com/thespacedoctor/rockAtlas-Sublime-Snippets>`_ useful. 

Issues
------

Please report any issues
`here <https://github.com/thespacedoctor/rockAtlas/issues>`__.

License
=======

Copyright (c) 2018 David Young

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
