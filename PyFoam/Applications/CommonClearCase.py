"""
Class that implements the common functionality for clearing the cases
"""

from PyFoam.ThirdParty.six import print_

class CommonClearCase(object):
    """ The class that clears the case
    """

    def addOptions(self):
        self.ensureGeneralOptions()
        self.generalOpts.add_option("--clear-case",
                                    action="store_true",
                                    default=False,
                                    dest="clearCase",
                                    help="Clear all timesteps except for the first before running")
        self.generalOpts.add_option("--complete-clear",
                                    action="store_true",
                                    default=False,
                                    dest="clearComplete",
                                    help="Like clear-case but removes the function-object data as well")

    def clearCase(self,sol):
        if self.opts.clearComplete:
            self.opts.clearCase=True
        if self.opts.clearCase:
            print_("Clearing out old timesteps ....")
            sol.clearResults(functionObjectData=self.opts.clearComplete)

# Should work with Python3 and Python2
