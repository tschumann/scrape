scrape
======
scrape is a work in progress site downloader.

Usage
-----
bin/python ./scrape.py

Installing
----------
python bootstrap-buildout.py
bin/buildout

Requirements
------------
Python 3

Running tests
-------------
bin/python test.py

Updating
--------
bootstrap-buildout.py is from https://bootstrap.pypa.io/bootstrap-buildout.py
ez_setup.py is from https://bootstrap.pypa.io/ez_setup.py (has_powershell needs to return false due to Powershell's SSL/TLS rules)
