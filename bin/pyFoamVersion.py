#!/usr/bin/env python
# Provided by Mark Olesen

description="""
print setup
"""
import os
import PyFoam
import PyFoam.FoamInformation

print "PYTHONPATH:", os.environ["PYTHONPATH"]
print "OpenFOAM", PyFoam.FoamInformation.foamVersion(),"of the installed versions",PyFoam.FoamInformation.foamInstalledVersions()
print "pyFoam-Version:",PyFoam.versionString()
