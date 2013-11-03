"""
Class that implements the common functionality for having a server
"""

class CommonServer(object):
    """ The class that switches on and off the server
    """

    def addOptions(self,haveServer=True):
        self.ensureGeneralOptions()
        if haveServer:
            self.generalOpts.add_option("--no-server-process",
                                        action="store_false",
                                        default=True,
                                        dest="server",
                                        help="Do not start a server process that can control the process")
        else:
            self.generalOpts.add_option("--start-server-process",
                                        action="store_true",
                                        default=True,
                                        dest="server",
                                        help="Start a server process that can control the process")
            
        
