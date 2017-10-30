rockAtlas
=========

[![Documentation Status](https://readthedocs.org/projects/rockAtlas/badge/)](http://rockAtlas.readthedocs.io/en/latest/?badge)

[![Coverage Status](https://cdn.rawgit.com/thespacedoctor/rockAtlas/master/coverage.svg)](https://cdn.rawgit.com/thespacedoctor/rockAtlas/master/htmlcov/index.html)

*A python package and command-line tools for A suite of tools to pull known solar-system small-body detections out of ATLAS data*.

Command-Line Usage
==================

``` sourceCode
Documentation for rockAtlas can be found here: http://rockAtlas.readthedocs.org/en/stable

Usage:
    rockAtlas init
    rockAtlas bookkeeping [-s <pathToSettingsFile>]

Commands:
    bookkeeping           update and clean database tables, perform essential bookkeeping tasks

Options:
    init                  setup the rockAtlas settings file for the first time
    -h, --help            show this help message
    -v, --version         show version
    -s, --settings        the settings file
```

Installation
============

The easiest way to install rockAtlas is to use `pip`:

``` sourceCode
pip install rockAtlas
```

Or you can clone the [github repo](https://github.com/thespacedoctor/rockAtlas) and install from a local version of the code:

``` sourceCode
git clone git@github.com:thespacedoctor/rockAtlas.git
cd rockAtlas
python setup.py install
```

To upgrade to the latest version of rockAtlas use the command:

``` sourceCode
pip install rockAtlas --upgrade
```

Documentation
=============

Documentation for rockAtlas is hosted by [Read the Docs](http://rockAtlas.readthedocs.org/en/stable/) (last [stable version](http://rockAtlas.readthedocs.org/en/stable/) and [latest version](http://rockAtlas.readthedocs.org/en/latest/)).

Command-Line Tutorial
=====================

Before you begin using rockAtlas you will need to populate some custom settings within the rockAtlas settings file.

To setup the default settings file at `~/.config/rockAtlas/rockAtlas.yaml` run the command:

``` sourceCode
rockAtlas init
```

This should create and open the settings file; follow the instructions in the file to populate the missing settings values (usually given an `XXX` placeholder).

Bookkeeping
-----------
