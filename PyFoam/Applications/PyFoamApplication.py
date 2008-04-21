#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/PyFoamApplication.py 2529 2007-12-29T16:43:36.743396Z bgschaid  $ 
"""Base class for pyFoam-applications

Classes can also be called with a command-line string"""

from PyFoam.Basics.FoamOptionParser import FoamOptionParser
from PyFoam.Error import error

import sys

class PyFoamApplication(object):
    def __init__(self,args=None,description=None,usage=None,interspersed=False,nr=3,exactNr=True):
        """
        @param description: description of the command
        @param usage: Usage
        @param interspersed: Is the command line allowed to be interspersed (options after the arguments)
        @param args: Command line arguments when using the Application as a 'class' from a script
        @param nr: Number of required arguments
        @param exactNr: Must not have more than the required number of arguments
        """
        self.parser=FoamOptionParser(args=args,description=description,usage=usage,interspersed=interspersed)
        self.addOptions()
        self.parser.parse(nr=nr,exactNr=exactNr)
        self.opts=self.parser.getOptions()

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
        
