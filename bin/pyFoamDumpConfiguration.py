#!/usr/bin/env python

description="""
Dump the contents of the configuration files
"""

from PyFoam import configuration as config
from os import path

from PyFoam.ThirdParty.six import print_

fName=path.join(path.curdir,"LocalConfigPyFoam")
if path.exists(fName):
    config().addFile(fName)

print_(config().dump())

# Should work with Python3 and Python2
