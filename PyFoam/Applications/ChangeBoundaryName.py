"""
Application class that implements pyFoamChangeBoundaryName.py

Author:
  Martin Beaudoin, Hydro-Quebec, 2010.

"""

from .PyFoamApplication import PyFoamApplication

from os import path
from optparse import OptionGroup

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.TimeDirectory import TimeDirectory

from PyFoam.ThirdParty.six import print_

class ChangeBoundaryName(PyFoamApplication):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Changes the name of a boundary in the boundary-file. Also if a
time-step is specified
        """
        PyFoamApplication.__init__(self,args=args,
                                   description=description,
                                   usage="%prog <caseDirectory> <boundaryName> <new name>",
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
        change.add_option("--time-step",
                          action="store",
                          default=None,
                          dest="timestep",
                          help="If specified all the field-files in that directory are updated")

    def run(self):
        fName=self.parser.getArgs()[0]
        bName=self.parser.getArgs()[1]
        nName=self.parser.getArgs()[2]

        boundary=ParsedParameterFile(path.join(".",fName,"constant","polyMesh","boundary"),debug=False,boundaryDict=True)

        bnd=boundary.content

        if type(bnd)!=list:
            self.error("Problem with boundary file (not a list)")

        found=False

        for val in bnd:
            if val==bName:
                found=True
            elif found:
                bnd[bnd.index(bName)]=nName
                break

        if not found:
            self.error("Boundary",bName,"not found in",bnd[::2])

        if self.opts.test:
            print_(boundary)
        else:
            boundary.writeFile()
            self.addToCaseLog(fName)

            if self.opts.timestep:
                print_("Updating the files of timestep",self.opts.timestep)
                td=TimeDirectory(fName,self.opts.timestep,
                                 yieldParsedFiles=True)

                for f in td:
                    print_("Updating",f.name)
                    f["boundaryField"][nName]=f["boundaryField"][bName]
                    del f["boundaryField"][bName]
                    f.writeFile()

# Should work with Python3 and Python2
