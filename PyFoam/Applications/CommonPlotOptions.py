"""
Class that implements common functionality for plotting options
"""

class CommonPlotOptions(object):
    """ The class that adds plot options
    """

    def __init__(self,persist):
        self.persistDefault=persist
        
    def addOptions(self):
        self.parser.add_option("--frequency",
                               type="float",
                               dest="frequency",
                               default=1.,
                               help="The frequency with which output should be generated (in seconds)")
        self.parser.add_option("--persist",
                               action="store_true",
                               dest="persist",
                               default=self.persistDefault,
                               help="Gnuplot windows stay after interrupt")
        self.parser.add_option("--non-persist",
                               action="store_false",
                               dest="persist",
                               help="Gnuplot windows close after interrupt")
        self.parser.add_option("--raise",
                               action="store_true",
                               dest="raiseit",
                               help="Raise the Gnuplot windows after every replot")
        self.parser.add_option("--no-default",
                               action="store_true",
                               default=False,
                               dest="nodefault",
                               help="Switch off the default plots (linear, continuity and bound)")
        self.parser.add_option("--no-linear",
                               action="store_false",
                               default=True,
                               dest="linear",
                               help="Don't plot the linear solver convergence")
        self.parser.add_option("--no-continuity",
                               action="store_false",
                               default=True,
                               dest="cont",
                               help="Don't plot the continuity info")
        self.parser.add_option("--no-bound",
                               action="store_false",
                               default=True,
                               dest="bound",
                               help="Don't plot the bounding of variables")
        self.parser.add_option("--with-iterations",
                               action="store_true",
                               default=False,
                               dest="iterations",
                               help="Plot the number of iterations of the linear solver")
        self.parser.add_option("--with-courant",
                               action="store_true",
                               default=False,
                               dest="courant",
                               help="Plot the courant-numbers of the flow")
        self.parser.add_option("--with-execution",
                               action="store_true",
                               default=False,
                               dest="execution",
                               help="Plot the execution time of each time-step")
        self.parser.add_option("--with-deltat",
                               action="store_true",
                               default=False,
                               dest="deltaT",
                               help="'Plot the timestep-size time-step")
        self.parser.add_option("--with-all",
                               action="store_true",
                               default=False,
                               dest="withAll",
                               help="Switch all possible plots on")
        self.parser.add_option("--write-files",
                               action="store_true",
                               default=False,
                               dest="writeFiles",
                               help="Writes the parsed data to files")
        self.parser.add_option("--hardcopy",
                               action="store_true",
                               default=False,
                               dest="hardcopy",
                               help="Writes postscript hardcopies of the plot at the end of the run")

    def processPlotOptions(self):
        if self.opts.nodefault:
            self.opts.linear=False
            self.opts.cont=False
            self.opts.bound=False
            
        if self.opts.withAll:
            self.opts.linear=True
            self.opts.cont=True
            self.opts.bound=True
            self.opts.iterations=True
            self.opts.courant=True
            self.opts.execution=True
            self.opts.deltaT=True

        
        
