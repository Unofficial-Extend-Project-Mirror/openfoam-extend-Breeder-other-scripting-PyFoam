#  ICE Revision: $Id: PyFoamApplication.py 9336 2008-09-08 13:33:27Z bgschaid $ 
"""Base class for pyFoam-applications

Classes can also be called with a command-line string"""

from PyFoam.Basics.FoamOptionParser import FoamOptionParser
from PyFoam.Error import error,warning
from PyFoam.FoamInformation import oldAppConvention as oldApp

import sys
from os import path

class PyFoamApplication(object):
    def __init__(self,
                 args=None,
                 description=None,
                 usage=None,
                 interspersed=False,
                 nr=None,
                 changeVersion=True,
                 exactNr=True):
        """
        @param description: description of the command
        @param usage: Usage
        @param interspersed: Is the command line allowed to be interspersed (options after the arguments)
        @param args: Command line arguments when using the Application as a 'class' from a script
        @param nr: Number of required arguments
        @param chaneVersion: May this application change the version of OF used?
        @param exactNr: Must not have more than the required number of arguments
        """
        self.parser=FoamOptionParser(args=args,
                                     description=description,
                                     usage=usage,
                                     interspersed=interspersed)
        if changeVersion:
            self.parser.add_option("--foamVersion",
                                   dest="foamVersion",
                                   default=None,
                                   help="Change the OpenFOAM-version that is to be used")

        self.parser.add_option("--psyco-accelerated",
                               dest="psyco",
                               default=False,
                               action="store_true",
                               help="Accelerate the script using the psyco-library (EXPERIMENTAL and requires a separatly installed psyco)")

        self.addOptions()
        self.parser.parse(nr=nr,exactNr=exactNr)
        self.opts=self.parser.getOptions()

        if self.opts.psyco:
            try:
                import psco
                psyco.full()
            except ImportError:
                warning("No psyco installed. Continuing without acceleration")
                
        self.run()
        
    def addOptions(self):
        """
        Add options to the parser
        """
        pass

    def run(self):
        """
        Run the real application
        """
        error("Not a valid application")
        

    def error(self,*args):
        """
        Prints an error message and exits
        @param args: Arguments that are to be printed
        """
        print "Error in",sys.argv[0],":",
        for a in args:
            print a,
        print
        sys.exit(-1)
        
    def checkCase(self,name):
        """
        Check whether this is a valid OpenFOAM-case
        @param name: the directory-bame that is supposed to be the case
        """
        if not path.exists(name):
            self.error("Case",name,"does not exist")
        if not path.isdir(name):
            self.error("Case",name,"is not a directory")
        if not path.exists(path.join(name,"system")):
            self.error("Case",name,"does not have a 'system' directory")
        if not path.exists(path.join(name,"constant")):
            self.error("Case",name,"does not have a 'constant' directory")
