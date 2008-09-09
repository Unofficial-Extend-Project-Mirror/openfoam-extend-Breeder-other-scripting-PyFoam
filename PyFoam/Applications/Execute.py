#  ICE Revision: $Id: Execute.py 9161 2008-08-04 08:01:05Z bgschaid $ 
"""
Application class that implements pyFoamExecute
"""

from PyFoamApplication import PyFoamApplication

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
        pass
    
    def run(self):            
        result=call(self.parser.getArgs())
        if result!=0:
            print "\nError result:",result
