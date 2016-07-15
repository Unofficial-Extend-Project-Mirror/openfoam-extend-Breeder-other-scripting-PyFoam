"""
Class that implements common functionality for plotting options
"""

from optparse import OptionGroup
from PyFoam.Basics.GnuplotTimelines import validTerminals

class CommonPlotOptions(object):
    """ The class that adds plot options
    """

    def __init__(self,persist):
        self.persistDefault=persist

    def addOptions(self):
        behaveGroup=OptionGroup(self.parser,
                                "Plot Behaviour",
                                "How the plots should behave (most of these options are passed to gnuplot)")

        behaveGroup.add_option("--frequency",
                               type="float",
                               dest="frequency",
                               default=1.,
                               help="The frequency with which output should be generated (in seconds). Default: %default")
        behaveGroup.add_option("--persist",
                               action="store_true",
                               dest="persist",
                               default=self.persistDefault,
                               help="Gnuplot windows stay after interrupt")
        behaveGroup.add_option("--non-persist",
                               action="store_false",
                               dest="persist",
                               help="Gnuplot windows close after interrupt")
        behaveGroup.add_option("--raise",
                               action="store_true",
                               dest="raiseit",
                               help="Raise the Gnuplot windows after every replot")
        behaveGroup.add_option("--implementation",
                               default=None,
                               dest="implementation",
                               help="The implementation that should be used for plotting")
        behaveGroup.add_option("--gnuplot-terminal",
                               default=None,
                               type="choice",
                               dest="gnuplotTerminal",
                               choices=validTerminals(),
                               help="Terminal implementation of gnuplot to use. Options: "+", ".join(validTerminals()))

        self.parser.add_option_group(behaveGroup)

        writeDGroup=OptionGroup(self.parser,
                                "Write plot data",
                                "How data and the plots themself should be written to disk")
        writeDGroup.add_option("--hardcopy",
                               action="store_true",
                               default=False,
                               dest="hardcopy",
                               help="Writes hardcopies of the plot at the end of the run")
        hcChoices=["postscript","png","pdf","svg","eps"]
        writeDGroup.add_option("--format-of-hardcopy",
                               type="choice",
                               action="store",
                               default="png",
                               dest="hardcopyformat",
                               choices=hcChoices,
                               help="File-format the hardcopy should be written in (Formats: "+", ".join(hcChoices)+") Default: %default")
        writeDGroup.add_option("--prefix-hardcopy",
                               action="store",
                               default=None,
                               dest="hardcopyPrefix",
                               help="Prefix for the hardcopy-files")
        writeDGroup.add_option("--terminal-hardcopy-options",
                               action="store",
                               default="",
                               dest="hardcopyTerminalOptions",
                               help="Options for the gnuplot terminal that does the hardcopy. Overrides the setting in [Plotting] with the name 'hardcopyOptions_<term>' (with <term> being the value of --format-of-hardcopy)")

        writeDGroup.add_option("--no-pickled-file",
                               action="store_false",
                               default=True,
                               dest="writePickled",
                               help="Do not write a pickled file with the plot data")

        self.parser.add_option_group(writeDGroup)

        plotItGroup=OptionGroup(self.parser,
                                "What to plot",
                                "Predefined quantities that the program looks for and plots")
        plotItGroup.add_option("--no-default",
                               action="store_true",
                               default=False,
                               dest="nodefault",
                               help="Switch off the default plots (linear, continuity and bound)")
        plotItGroup.add_option("--no-linear",
                               action="store_false",
                               default=True,
                               dest="linear",
                               help="Don't plot the linear solver convergence")
        plotItGroup.add_option("--no-continuity",
                               action="store_false",
                               default=True,
                               dest="cont",
                               help="Don't plot the continuity info")
        plotItGroup.add_option("--no-bound",
                               action="store_false",
                               default=True,
                               dest="bound",
                               help="Don't plot the bounding of variables")
        plotItGroup.add_option("--with-iterations",
                               action="store_true",
                               default=False,
                               dest="iterations",
                               help="Plot the number of iterations of the linear solver")
        plotItGroup.add_option("--with-courant",
                               action="store_true",
                               default=False,
                               dest="courant",
                               help="Plot the courant-numbers of the flow")
        plotItGroup.add_option("--with-execution",
                               action="store_true",
                               default=False,
                               dest="execution",
                               help="Plot the execution time of each time-step")
        plotItGroup.add_option("--with-deltat",
                               action="store_true",
                               default=False,
                               dest="deltaT",
                               help="'Plot the timestep-size time-step")
        plotItGroup.add_option("--with-all",
                               action="store_true",
                               default=False,
                               dest="withAll",
                               help="Switch all possible plots on")
        self.parser.add_option_group(plotItGroup)

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

        if self.opts.hardcopy and self.opts.hardcopyTerminalOptions=="":
            from PyFoam import configuration as conf

            self.opts.hardcopyTerminalOptions=conf().get("Plotting",
                                                         "hardcopyOptions_"+self.opts.hardcopyformat,
                                                         default="")

# Should work with Python3 and Python2
