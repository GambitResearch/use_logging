[![Build Status](https://travis-ci.org/GambitResearch/use_logging.svg?branch=master)](https://travis-ci.org/GambitResearch/use_logging)
[![Coverage Status](https://coveralls.io/repos/github/GambitResearch/use_logging/badge.svg?branch=master)](https://coveralls.io/github/GambitResearch/use_logging?branch=master)

use_logging
========================

Tool for changing python print statements into logging module invocations. Automatically adds the appropriate imports.

Implemented by wrapping lib2to3, hence some oddities.

Installation
------------------------

	$ pip install use_logging

Example Useage
------------------------

    $ use_logging -w my_project/*.py
    

Links
------------------------
https://docs.python.org/2/library/2to3.html



ToDo
------------------------
1. Any more tests?

1. Rest of stuff in https://github.com/vitorbaptista/pyconuk_helloworld (bandit, manifest/+check)

