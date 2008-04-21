#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/PlotRunner.py 2881 2008-03-11T18:56:34.676111Z bgschaid  $ 
"""
Class that implements pyFoamPlotRunner
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.FoamInformation import changeFoamVersion

from PyFoam.Execution.GnuplotRunner import GnuplotRunner

from PyFoam.Execution.ParallelExecution import LAMMachine

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Error import warning

from CommonPlotLines import CommonPlotLines
from CommonPlotOptions import CommonPlotOptions
from CommonClearCase import CommonClearCase
from CommonSafeTrigger import CommonSafeTrigger
from CommonWriteAllTrigger import CommonWriteAllTrigger

from os import path

class PlotRunner(PyFoamApplication,
                 CommonPlotOptions,
                 CommonPlotLines,
                 CommonSafeTrigger,
                 CommonWriteAllTrigger,
                 CommonClearCase):
    def __init__(self,args=None):
        description="""
        runs an OpenFoam solver needs the usual 3 arguments (<solver>
        <directory> <case>) and passes them on (plus additional arguments).
        Output is sent to stdout and a logfile inside the case directory
        (PyFoamSolver.logfile) Information about the residuals is output as
        graphs
        
        If the directory contains a file customRegexp this is automatically
        read and the regular expressions in it are displayed
        """
        CommonPlotOptions.__init__(self,persist=True)
        CommonPlotLines.__init__(self)
        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description)
        
    def addOptions(self):
        CommonPlotOptions.addOptions(self)
        
        self.parser.add_option("--procnr",
                               type="int",
                               dest="procnr",
                               default=None,
                               help="The number of processors the run should be started on")
        
        self.parser.add_option("--machinefile",
                               dest="machinefile",
                               default=None,
                               help="The machinefile that specifies the parallel machine")
        
        self.parser.add_option("--steady-run",
                               action="store_true",
                               default=False,
                               dest="steady",
                               help="This is a steady run. Stop it after convergence")
        
        self.parser.add_option("--restart",
                               action="store_true",
                               default=False,
                               dest="restart",
                               help="Restart the simulation from the last time-step")
        
        self.parser.add_option("--progress",
                               action="store_true",
                               default=False,
                               dest="progress",
                               help="Only prints the progress of the simulation, but swallows all the other output")
        
        self.parser.add_option("--foamVersion",
                               dest="foamVersion",
                               default=None,
                               help="Change the OpenFOAM-version that is to be used")

        self.parser.add_option("--report-usage",
                               action="store_true",
                               default=False,
                               dest="reportUsage",
                               help="After the execution the maximum memory usage is printed to the screen")

        CommonPlotLines.addOptions(self)
        CommonClearCase.addOptions(self)
        CommonSafeTrigger.addOptions(self)
        CommonWriteAllTrigger.addOptions(self)
        
    def run(self):
        if self.opts.foamVersion!=None:
            changeFoamVersion(self.opts.foamVersion)

        self.processPlotOptions()
        
        self.processPlotLineOptions(autoPath=path.join(self.parser.getArgs()[1],self.parser.getArgs()[2]))
        
        cName=self.parser.getArgs()[2]
        sol=SolutionDirectory(cName,archive=None)
        
        self.clearCase(sol)

        lam=None
        if self.opts.procnr!=None or self.opts.machinefile!=None:
            lam=LAMMachine(machines=self.opts.machinefile,nr=self.opts.procnr)
        
        run=GnuplotRunner(argv=self.parser.getArgs(),
                          smallestFreq=self.opts.frequency,
                          persist=self.opts.persist,
                          plotLinear=self.opts.linear,
                          plotCont=self.opts.cont,
                          plotBound=self.opts.bound,
                          plotIterations=self.opts.iterations,
                          plotCourant=self.opts.courant,
                          plotExecution=self.opts.execution,
                          plotDeltaT=self.opts.deltaT,
                          customRegexp=self.plotLines(),
                          writeFiles=self.opts.writeFiles,
                          server=True,
                          lam=lam,
                          raiseit=self.opts.raiseit,
                          steady=self.opts.steady,
                          progress=self.opts.progress,
                          restart=self.opts.restart)

        self.addSafeTrigger(run,sol,steady=self.opts.steady)
        self.addWriteAllTrigger(run,sol)
        
        run.start()

        if self.opts.reportUsage:
            print "\n  Used Memory: ",run.run.usedMemory(),"MB"

