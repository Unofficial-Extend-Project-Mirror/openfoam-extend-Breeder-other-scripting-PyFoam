#  ICE Revision: $Id:$
"""
Application class that implements pyFoamChangeBoundaryType.py
"""

from PyFoamApplication import PyFoamApplication

from os import path
import sys
from optparse import OptionGroup

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.ListFile import ListFile

class ChangeBoundaryType(PyFoamApplication):
    def __init__(self,args=None):
        description="""\
Changes the type of a boundary in the boundary-file
        """
        PyFoamApplication.__init__(self,args=args,
                                   description=description,
                                   usage="%prog <caseDirectory> <boundaryName> <new type>",
                                   changeVersion=False,
                                   nr=3,
                                   interspersed=True)
        
    def addOptions(self):
        change=OptionGroup(self.parser,
                           "Change",
                           "Change specific options")
        self.parser.add_option_group(change)

        change.add_option("--test",
                          action="store_true",
                          default=False,
                          dest="test",
                          help="Only print the new boundary file")

    def run(self):
        fName=self.parser.getArgs()[0]
        bName=self.parser.getArgs()[1]
        tName=self.parser.getArgs()[2]

        boundary=ParsedParameterFile(path.join(".",fName,"constant","polyMesh","boundary"),debug=False,boundaryDict=True)

        bnd=boundary.content

        if type(bnd)!=list:
            self.error("Problem with boundary file (not a list)")

        found=False

        for val in bnd:
            if val==bName:
                found=True
            elif found:
                val["type"]=tName
                break

        if not found:
            self.error("Boundary",bName,"not found in",bnd[::2])

        if self.opts.test:
            print boundary
        else:
            boundary.writeFile()
            self.addToCaseLog(fName)
