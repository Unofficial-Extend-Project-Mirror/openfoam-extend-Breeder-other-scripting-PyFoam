#  ICE Revision: $Id: ChangeBoundaryType.py 12762 2013-01-03 23:11:02Z bgschaid $
"""
Application class that implements pyFoamChangeBoundaryType.py
"""

from .PyFoamApplication import PyFoamApplication

from os import path
import sys
from optparse import OptionGroup

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.ListFile import ListFile

from PyFoam.ThirdParty.six import print_

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

        change.add_option("--region",
                          action="store",
                          default="",
                          dest="region",
                          help="Region to use. If unset the default mesh is used")

        change.add_option("--time-directory",
                          action="store",
                          default="constant",
                          dest="time",
                          help="Time to use. If unset the mesh in 'constant'' is used")

    def run(self):
        fName=self.parser.getArgs()[0]
        bName=self.parser.getArgs()[1]
        tName=self.parser.getArgs()[2]

        boundaryPath=path.join(".",fName,self.opts.time,self.opts.region,"polyMesh","boundary")
        try:
            boundary=ParsedParameterFile(boundaryPath,debug=False,boundaryDict=True)
        except IOError:
            self.error("Problem opening boundary file",boundaryPath)

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
            print_(boundary)
        else:
            boundary.writeFile()
            self.addToCaseLog(fName)

# Should work with Python3 and Python2
