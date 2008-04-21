#!/usr/bin/env python

description="""
Dump the contents of the configuration files
"""

from PyFoam import configuration as config

print config().dump()
