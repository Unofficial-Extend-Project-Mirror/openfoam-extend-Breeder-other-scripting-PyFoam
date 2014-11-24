#  ICE Revision: $Id$
"""
Application class that implements pyFoamChangeBoundaryType.py
"""

from .PyFoamApplication import PyFoamApplication

from os import path
from optparse import OptionGroup

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from PyFoam.ThirdParty.six import print_,string_types

class ChangeBoundaryType(PyFoamApplication):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Changes the type of a boundary in the boundary-file
        """
        PyFoamApplication.__init__(self,args=args,
                                   description=description,
                                   usage="%prog <caseDirectory> <boundaryName> <new type>",
                                   changeVersion=False,
                                   nr=3,
                                   interspersed=True,
                                   **kwargs)

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

        change.add_option("--additional-values",
                          action="store",
                          default=None,
                          dest="additionalValues",
                          help="Dictionary in Python-format with additional values to add to the boundary")

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
                if self.opts.additionalValues:
                    vals=self.opts.additionalValues
                    if isinstance(vals,string_types):
                        # we're called from the command line. Convert string to usable format
                        vals=eval(vals)
                    for k in vals:
                        val[k]=vals[k]
                break

        if not found:
            self.error("Boundary",bName,"not found in",bnd[::2])

        if self.opts.test:
            print_(boundary)
        else:
            boundary.writeFile()
            self.addToCaseLog(fName)

# Should work with Python3 and Python2
