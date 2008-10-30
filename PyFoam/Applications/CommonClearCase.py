"""
Class that implements the common functionality for clearing the cases
"""

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
        
    def clearCase(self,sol):
        if self.opts.clearCase:
            print "Clearing out old timesteps ...."            
            sol.clearResults()

        
