"""
Application-class that implements pyFoamCloneCase.py
"""

from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Error import error,warning

from os import path

class CloneCase(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Clones a case by copying the system, constant and 0-directories
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <source> <destination>",
                                   changeVersion=False,
                                   interspersed=True,
                                   nr=2)

    def addOptions(self):
        what=OptionGroup(self.parser,
                         "What",
                         "Define what should be cloned")
        self.parser.add_option_group(what)

        what.add_option("--chemkin",
                        action="store_true",
                        dest="chemkin",
                        default=False,
                        help="Also copy the Chemkin-directory")
        what.add_option("--add-item",
                        action="append",
                        dest="additional",
                        default=[],
                        help="Add a subdirectory to the list of cloned items (can be used more often than once)")
        what.add_option("--no-pyfoam",
                        action="store_false",
                        dest="dopyfoam",
                        default=True,
                        help="Don't copy PyFoam-specific stuff")
        
        behave=OptionGroup(self.parser,
                           "Behaviour")
        self.parser.add_option_group(behave)
        behave.add_option("--force",
                          action="store_true",
                          dest="force",
                          default=False,
                          help="Overwrite destination if it exists")

    def run(self):
        if len(self.parser.getArgs())>2:
            error("Too many arguments:",self.parser.getArgs()[2:],"can not be used")
            
        sName=self.parser.getArgs()[0]
        dName=self.parser.getArgs()[1]

        if path.exists(dName):
            if self.parser.getOptions().force:
                warning("Replacing",dName,"(--force option)")
            elif path.exists(path.join(dName,"system","controlDict")):            
                error("Destination",dName,"already existing and a Foam-Case")
            elif path.isdir(dName):
                dName=path.join(dName,path.basename(sName))
                if path.exists(dName) and not self.parser.getOptions().force:
                    error(dName,"already existing")                    
        elif not path.exists(path.dirname(dName)):
            warning("Directory",path.dirname(dName),"does not exist. Creating")
                
        sol=SolutionDirectory(sName,archive=None,paraviewLink=False)

        if self.parser.getOptions().chemkin:
            sol.addToClone("chemkin")

        if self.parser.getOptions().dopyfoam:
            sol.addToClone("customRegexp")

        for a in self.parser.getOptions().additional:
            sol.addToClone(a)
            
        sol.cloneCase(dName)
