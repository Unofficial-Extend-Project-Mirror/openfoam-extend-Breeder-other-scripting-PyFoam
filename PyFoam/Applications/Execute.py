#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/Execute.py 2547 2007-12-31T11:01:25.898379Z bgschaid  $ 
"""
Application class that implements pyFoamExecute
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.FoamInformation import changeFoamVersion

from subprocess import call

class Execute(PyFoamApplication):
    def __init__(self,args=None):
        description="""
        Runs a command, but first switches the environment to a specific
OpenFOAM-version. Is of use for using wmake for a specific version
        """
        
        PyFoamApplication.__init__(self,
                                   nr=1,
                                   exactNr=False,
                                   args=args,
                                   usage="%prog [options] <command> [arguments]",
                                   description=description)
        
    def addOptions(self):
        self.parser.add_option("--foamVersion",
                               dest="foamVersion",
                               default=None,
                               help="Change the OpenFOAM-version that is to be used")
                               
    def run(self):
        if self.opts.foamVersion!=None:
            changeFoamVersion(self.opts.foamVersion)
        else:
            self.error("No Foam Version specified!")
            
        result=call(self.parser.getArgs())
        if result!=0:
            print "\nError result:",result
