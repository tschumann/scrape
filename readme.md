scrape
------
scrape is a work in progress website downloader.


Usage
=====
```
bin/python scrape.py https://example.com
```


Installing
==========
```
python bootstrap-buildout.py
```
```
bin/buildout
```


Running tests
=============
```
bin/python tests.py
```


Updating
========
bootstrap-buildout.py is from https://bootstrap.pypa.io/bootstrap-buildout.py

ez_setup.py is from https://bootstrap.pypa.io/ez_setup.py (has_powershell needs to return false due to Powershell's SSL/TLS rules)
