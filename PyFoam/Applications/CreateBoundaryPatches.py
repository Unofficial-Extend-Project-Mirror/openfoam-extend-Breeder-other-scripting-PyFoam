#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/CreateBoundaryPatches.py 6771 2010-08-08T19:32:36.252973Z bgschaid  $ 
"""
Application class that implements pyFoamCreateBoundaryPatches.py
"""

import re
from os import path

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

class CreateBoundaryPatches(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Takes a field-file. Looks up the polyMesh/boundary-file of the case
and adds the corresponding patches to the boundary field setting it to
zeroGradient for all patches and walls
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <fieldfile>",
                                   changeVersion=False,
                                   nr=1,
                                   interspersed=True)
        
    def addOptions(self):
        self.parser.add_option("--clear-unused",
                               action="store_true",
                               default=None,
                               dest="clear",
                               help="Removes all the boundaries that are not in the boundary-file")
        self.parser.add_option("--no-check",
                               action="store_true",
                               default=None,
                               dest="nocheck",
                               help="Doesn't check whether the boundary tests are consistent")
        
        self.parser.add_option("--test",
                               action="store_true",
                               default=None,
                               dest="test",
                               help="Does not write the file but only prints it to the screen")

        self.parser.add_option("--verbose",
                               action="store_true",
                               default=None,
                               dest="verbose",
                               help="Writes to the screen what is being modified")

        self.parser.add_option("--default",
                               action="store",
                               default="{'type':'zeroGradient'}",
                               dest="default",
                               help="The default value for newly created patches as a Python-dictionary (instead of '{ \"type\" : \"zeroGradient\" }')")

        self.parser.add_option("--filter",
                               action="store",
                               default=None,
                               dest="filter",
                               help="A regular expression by which patch names are filtered before they are set")

        self.parser.add_option("--overwrite",
                               action="store_true",
                               default=False,
                               dest="overwrite",
                               help="Overwrites existing boundary conditions")

        self.parser.add_option("--fix-types",
                               action="store_true",
                               default=False,
                               dest="fixtypes",
                               help="Fix inconsistencies")

    def run(self):
        fName=self.parser.getArgs()[0]

        try:
            dictFile=ParsedParameterFile(fName,backup=False)
        except IOError,e:
            self.error("Problem with file",fName,":",e)

        fName=path.abspath(fName)
        case=path.dirname(path.dirname(fName))
        region=None
        
        if not SolutionDirectory(case,archive=None,paraviewLink=False).isValid():
            # checking for a multi-region case
            case=path.dirname(case)
            region=path.basename(path.dirname(fName))
            print case,region
            if region not in SolutionDirectory(case,archive=None,paraviewLink=False).getRegions():
                self.error(region,"is not a valid region in the case",case)
                
        if self.opts.filter==None:
            flter=re.compile(".+")
        else:
            flter=re.compile(self.opts.filter)
            
        boundaries=dictFile["boundaryField"]

        try:
            bFile=BoundaryDict(case,region=region)
        except IOError,e:
            self.error("Problem reading the boundary file:",e)
            
        if self.opts.clear:
            for b in boundaries.keys():
                if b not in bFile.patches():
                    if self.opts.verbose:
                        print "Deleting patch",b
                    del boundaries[b]

        if not self.opts.nocheck:
            for p in bFile.patches():
                if boundaries.has_key(p):
                    typ=boundaries[p]["type"]
                    pTyp=bFile[p]["type"]
                    if pTyp!="patch" and pTyp!="wall" and pTyp!=typ:
                        if self.opts.fixtypes:
                            if self.opts.verbose:
                                print "Fixing wall/patch patch",p
                            del boundaries[p]
                            continue
                        else:
                            self.error("Inconsistent type for ",p,": Is",typ,"but should be",pTyp)
                    if typ in ["symmetryPlane","empty","wedge","cyclic","processor"] and pTyp!=typ:
                        if self.opts.fixtypes:
                            if self.opts.verbose:
                                print "Fixing special patch",p
                            del boundaries[p]
                            continue
                        else:
                            self.error("Inconsistent type for ",p,": Is",typ,"but should be some kind of patch type")
                        
        for p in bFile.patches():
            if (not boundaries.has_key(p) or self.opts.overwrite) and flter.match(p):
                pTyp=bFile[p]["type"]
                if pTyp!="patch" and pTyp!="wall":
                    tmp={"type":pTyp}
                else:
                    tmp=eval(self.opts.default)
                if self.opts.verbose:
                    print "Writing",tmp,"to patch",p
                boundaries[p]=tmp;

        if self.opts.test:
            print str(dictFile)
        else:
            dictFile.writeFile()
            self.addToCaseLog(case)
    
