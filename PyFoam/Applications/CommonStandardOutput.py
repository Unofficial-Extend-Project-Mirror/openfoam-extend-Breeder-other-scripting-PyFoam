"""
Class that implements the common functionality for treatment of the standard output
"""

from optparse import OptionGroup
from os import path

class CommonStandardOutput(object):
    """ The class that defines options for standard output
    """

    def addOptions(self):
        grp=OptionGroup(self.parser,
                        "Standard Output",
                        "Treatment of the standard output that is captured from the OpenFOAM-application")
        grp.add_option("--progress",
                       action="store_true",
                       default=False,
                       dest="progress",
                       help="Only prints the progress of the simulation, but swallows all the other output")
        grp.add_option("--logname",
                       dest="logname",
                       default=None,
                       help="Name of the logfile")
        self.parser.add_option_group(grp)

    def setLogname(self,
                   default="PyFoamRunner",
                   useApplication=True):
        """Builds a logfile-name
        @param default: Default value if no prefix for the logfile-has been defined
        @param useApplication: append the name of the application to the prefix"""

        if self.opts.logname==None:
            self.opts.logname=default
        if useApplication:
            self.opts.logname+="."+path.basename(self.parser.getArgs()[0])
            
