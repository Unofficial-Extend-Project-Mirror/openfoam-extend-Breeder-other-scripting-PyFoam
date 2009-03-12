#  ICE Revision: $Id: SteadyRunner.py 9973 2009-02-05 12:47:31Z bgschaid $ 
"""
Application class that implements pyFoamSteadyRunner
"""

from os import path

from PyFoamApplication import PyFoamApplication

from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Error import warning

from CommonParallel import CommonParallel
from CommonRestart import CommonRestart
from CommonPlotLines import CommonPlotLines
from CommonClearCase import CommonClearCase
from CommonReportUsage import CommonReportUsage
from CommonSafeTrigger import CommonSafeTrigger
from CommonWriteAllTrigger import CommonWriteAllTrigger
from CommonStandardOutput import CommonStandardOutput
from CommonServer import CommonServer

class SteadyRunner(PyFoamApplication,
                   CommonPlotLines,
                   CommonSafeTrigger,
                   CommonWriteAllTrigger,
                   CommonClearCase,
                   CommonServer,
                   CommonReportUsage,
                   CommonParallel,
                   CommonRestart,
                   CommonStandardOutput):
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
        CommonClearCase.addOptions(self)
        CommonRestart.addOptions(self)
        CommonReportUsage.addOptions(self)
        CommonStandardOutput.addOptions(self)
        CommonParallel.addOptions(self)
        CommonPlotLines.addOptions(self)
        CommonSafeTrigger.addOptions(self)
        CommonWriteAllTrigger.addOptions(self)
        CommonServer.addOptions(self)
        
    def run(self):
        cName=self.parser.casePath()
        self.checkCase(cName)

        self.processPlotLineOptions(autoPath=cName)

        sol=SolutionDirectory(cName,archive=None)
        
        self.clearCase(sol)

        lam=self.getParallel()

        self.setLogname()
        
        run=ConvergenceRunner(BoundingLogAnalyzer(progress=self.opts.progress),
                              silent=self.opts.progress,
                              argv=self.parser.getArgs(),
                              restart=self.opts.restart,
                              server=self.opts.server,
                              logname=self.opts.logname,
                              lam=lam,
                              noLog=self.opts.noLog)

        self.addPlotLineAnalyzers(run)

        self.addSafeTrigger(run,sol)
        self.addWriteAllTrigger(run,sol)
        
        run.start()

        self.reportUsage(run)

