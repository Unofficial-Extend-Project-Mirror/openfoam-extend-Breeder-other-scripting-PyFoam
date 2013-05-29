#! /usr/bin/env python

description="""
Adds an empty boundary to a case file
"""

from PyFoam.Basics.FoamOptionParser import FoamOptionParser
from os import path
import sys

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.MeshInformation import MeshInformation

from PyFoam.ThirdParty.six import print_

parse=FoamOptionParser(description=description,usage="%prog <caseDirectory> <boundaryName>")
parse.parse(nr=2)

fName=parse.getArgs()[0]
bName=parse.getArgs()[1]

boundary=BoundaryDict(fName)

lastFace=MeshInformation(fName).nrOfFaces()

if bName in boundary.patches():
    print_("Patch",bName,"already exists in file")
    sys.exit(-1)

val={}
val["type"]="wall"
val["nFaces"]="0"
val["startFace"]=str(lastFace)

boundary[bName]=val

boundary.writeFile()

# Should work with Python3 and Python2
