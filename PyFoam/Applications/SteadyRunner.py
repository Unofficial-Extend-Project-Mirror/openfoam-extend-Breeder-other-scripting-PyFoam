#  ICE Revision: $Id: SteadyRunner.py 9161 2008-08-04 08:01:05Z bgschaid $ 
"""
Application class that implements pyFoamSteadyRunner
"""

from os import path

from PyFoamApplication import PyFoamApplication

from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Execution.ParallelExecution import LAMMachine
from PyFoam.Error import warning

from CommonPlotLines import CommonPlotLines
from CommonClearCase import CommonClearCase
from CommonSafeTrigger import CommonSafeTrigger
from CommonWriteAllTrigger import CommonWriteAllTrigger

class SteadyRunner(PyFoamApplication,
                   CommonPlotLines,
                   CommonSafeTrigger,
                   CommonWriteAllTrigger,
                   CommonClearCase):
    def __init__(self,args=None):
        description="""
Runs an OpenFoam steady solver.  Needs the usual 3 arguments (<solver>
<directory> <case>) and passes them on (plus additional arguments)
Output is sent to stdout and a logfile inside the case directory
(PyFoamSolver.logfile).  The Directory PyFoamSolver.analyzed contains
this information a) Residuals and other information of the linear
solvers b) Execution time c) continuity information d) bounding of
variables
        
If the solver has converged (linear solvers below threshold) it is
stopped and the last simulation state is written to disk
        """

        CommonPlotLines.__init__(self)        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description)

    def addOptions(self):
        self.parser.add_option("--procnr",
                               type="int",
                               dest="procnr",
                               default=None,
                               help="The number of processors the run should be started on")
        self.parser.add_option("--machinefile",
                               dest="machinefile",
                               default=None,
                               help="The machinefile that specifies the parallel machine")
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
        cName=self.parser.casePath()
        self.checkCase(cName)

        self.processPlotLineOptions(autoPath=cName)

        sol=SolutionDirectory(cName,archive=None)
        
        self.clearCase(sol)

        lam=None
        if self.opts.procnr!=None or self.opts.machinefile!=None:
            lam=LAMMachine(machines=self.opts.machinefile,nr=self.opts.procnr)


        run=ConvergenceRunner(BoundingLogAnalyzer(progress=self.opts.progress),silent=self.opts.progress,argv=self.parser.getArgs(),restart=self.opts.restart,server=True,lam=lam)

        self.addPlotLineAnalyzers(run)

        self.addSafeTrigger(run,sol)
        self.addWriteAllTrigger(run,sol)
        
        run.start()

        if self.opts.reportUsage:
            print "\n  Used Memory: ",run.run.usedMemory(),"MB"

