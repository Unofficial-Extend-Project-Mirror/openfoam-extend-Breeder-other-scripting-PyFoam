#! /usr/bin/env python

description="""
Clears all empty boundaries (those with zero faces) from a
polyMesh/boundaries file
"""

from PyFoam.Basics.FoamOptionParser import FoamOptionParser
from os import path
import sys

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.MeshInformation import MeshInformation

from PyFoam.ThirdParty.six import print_

parse=FoamOptionParser(description=description,usage="%prog <caseDirectory>")
parse.parse(nr=1)

fName=parse.getArgs()[0]

boundary=BoundaryDict(fName)

cleared=[]

for b in boundary.patches():
    if boundary[b]["nFaces"]==0:
        cleared.append(b)
        del  boundary[b]

if len(cleared)>0:
    print_("Cleared boundaries",", ".join(cleared))
    boundary.writeFile()
else:
    print_("No empty boundaries")

# Should work with Python3 and Python2
