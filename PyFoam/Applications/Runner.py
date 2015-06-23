#  ICE Revision: $Id$
"""
Application class that implements pyFoamRunner
"""

from .PyFoamApplication import PyFoamApplication

from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.RegionCases import RegionCases

from PyFoam.Error import warning

from .CommonMultiRegion import CommonMultiRegion
from .CommonPlotLines import CommonPlotLines
from .CommonClearCase import CommonClearCase
from .CommonReportUsage import CommonReportUsage
from .CommonReportRunnerData import CommonReportRunnerData
from .CommonWriteAllTrigger import CommonWriteAllTrigger
from .CommonLibFunctionTrigger import CommonLibFunctionTrigger
from .CommonStandardOutput import CommonStandardOutput
from .CommonParallel import CommonParallel
from .CommonRestart import CommonRestart
from .CommonServer import CommonServer
from .CommonVCSCommit import CommonVCSCommit
from .CommonPrePostHooks import CommonPrePostHooks

from PyFoam.ThirdParty.six import print_

class Runner(PyFoamApplication,
             CommonPlotLines,
             CommonWriteAllTrigger,
             CommonLibFunctionTrigger,
             CommonClearCase,
             CommonRestart,
             CommonReportUsage,
             CommonReportRunnerData,
             CommonMultiRegion,
             CommonParallel,
             CommonServer,
             CommonStandardOutput,
             CommonVCSCommit,
             CommonPrePostHooks):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Runs an OpenFoam solver.  Needs the usual 3 arguments (<solver>
<directory> <case>) and passes them on (plus additional arguments).
Output is sent to stdout and a logfile inside the case directory
(PyFoamSolver.logfile) The Directory PyFoamSolver.analyzed contains
this information: a) Residuals and other information of the linear
solvers b Execution time c) continuity information d) bounding of
variables
        """

        CommonPlotLines.__init__(self)
        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description,
                                   findLocalConfigurationFile=self.localConfigFromCasename,
                                   **kwargs)

    def addOptions(self):
        CommonClearCase.addOptions(self)
        CommonReportUsage.addOptions(self)
        CommonReportRunnerData.addOptions(self)
        CommonRestart.addOptions(self)
        CommonStandardOutput.addOptions(self)
        CommonParallel.addOptions(self)
        CommonPlotLines.addOptions(self)
        CommonWriteAllTrigger.addOptions(self)
        CommonLibFunctionTrigger.addOptions(self)
        CommonMultiRegion.addOptions(self)
        CommonServer.addOptions(self)
        CommonVCSCommit.addOptions(self)
        CommonPrePostHooks.addOptions(self)

    def run(self):
        if self.opts.keeppseudo and (not self.opts.regions and self.opts.region==None):
            warning("Option --keep-pseudocases only makes sense for multi-region-cases")

        if self.opts.region:
            regionNames=self.opts.region
        else:
            regionNames=[None]

        regions=None

        casePath=self.parser.casePath()
        self.checkCase(casePath)
        #        self.addLocalConfig(casePath)

        self.addToCaseLog(casePath,"Starting")
        self.prepareHooks()

        if self.opts.regions or self.opts.region!=None:
            print_("Building Pseudocases")
            sol=SolutionDirectory(casePath,archive=None)
            regions=RegionCases(sol,clean=True)

            if self.opts.regions:
                regionNames=sol.getRegions()

        self.processPlotLineOptions(autoPath=casePath)

        self.clearCase(SolutionDirectory(casePath,archive=None))

        lam=self.getParallel(SolutionDirectory(casePath,archive=None))

        self.checkAndCommit(SolutionDirectory(casePath,archive=None))

        for theRegion in regionNames:
            args=self.buildRegionArgv(casePath,theRegion)
            self.setLogname()
            run=AnalyzedRunner(BoundingLogAnalyzer(progress=self.opts.progress,
                                                   doFiles=self.opts.writeFiles,
                                                   singleFile=self.opts.singleDataFilesOnly,
                                                   doTimelines=True),
                               silent=self.opts.progress or self.opts.silent,
                               argv=args,
                               server=self.opts.server,
                               lam=lam,
                               restart=self.opts.restart,
                               logname=self.opts.logname,
                               compressLog=self.opts.compress,
                               logTail=self.opts.logTail,
                               noLog=self.opts.noLog,
                               remark=self.opts.remark,
                               parameters=self.getRunParameters(),
                               echoCommandLine=self.opts.echoCommandPrefix,
                               jobId=self.opts.jobId)

            run.createPlots(customRegexp=self.lines_,
                            writeFiles=self.opts.writeFiles)

            self.addWriteAllTrigger(run,SolutionDirectory(casePath,archive=None))
            self.addLibFunctionTrigger(run,SolutionDirectory(casePath,archive=None))
            self.runPreHooks()

            run.start()

            if len(regionNames)>1:
                self.setData({theRegion:run.data})
            else:
                self.setData(run.data)

            self.runPostHooks()

            self.reportUsage(run)
            self.reportRunnerData(run)

            if theRegion!=None:
                print_("Syncing into master case")
                regions.resync(theRegion)

        if regions!=None:
            if not self.opts.keeppseudo:
                print_("Removing pseudo-regions")
                regions.cleanAll()
            else:
                for r in sol.getRegions():
                    if r not in regionNames:
                        regions.clean(r)

        self.addToCaseLog(casePath,"Ended")

# Should work with Python3 and Python2
