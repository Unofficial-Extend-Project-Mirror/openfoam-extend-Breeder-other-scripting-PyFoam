#!/usr/bin/env python

description="""
Dump the contents of the configuration files
"""

from PyFoam import configuration as config
from os import path
fName=path.join(path.curdir,"LocalConfigPyFoam")
if path.exists(fName):
    config().addFile(fName)
    
print config().dump()
