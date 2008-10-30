#  ICE Revision: $Id: Runner.py 9441 2008-09-22 20:51:21Z bgschaid $ 
"""
Application class that implements pyFoamRunner
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.RegionCases import RegionCases

from PyFoam.Error import warning,error

from CommonMultiRegion import CommonMultiRegion
from CommonPlotLines import CommonPlotLines
from CommonClearCase import CommonClearCase
from CommonReportUsage import CommonReportUsage
from CommonWriteAllTrigger import CommonWriteAllTrigger
from CommonLibFunctionTrigger import CommonLibFunctionTrigger
from CommonStandardOutput import CommonStandardOutput
from CommonParallel import CommonParallel
from CommonRestart import CommonRestart

from os import path

class Runner(PyFoamApplication,
             CommonPlotLines,
             CommonWriteAllTrigger,
             CommonLibFunctionTrigger,
             CommonClearCase,
             CommonRestart,
             CommonReportUsage,
             CommonMultiRegion,
             CommonParallel,
             CommonStandardOutput):
    def __init__(self,args=None):
        description="""
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
                                   description=description)
        
    def addOptions(self):
        CommonClearCase.addOptions(self)
        CommonReportUsage.addOptions(self)
        CommonRestart.addOptions(self)        
        CommonStandardOutput.addOptions(self)
        CommonParallel.addOptions(self)
        CommonPlotLines.addOptions(self)
        CommonWriteAllTrigger.addOptions(self)
        CommonLibFunctionTrigger.addOptions(self)
        CommonMultiRegion.addOptions(self)
        
    def run(self):
        if self.opts.keeppseudo and (not self.opts.regions and self.opts.region==None):
            warning("Option --keep-pseudocases only makes sense for multi-region-cases")
        regionNames=[self.opts.region]
        regions=None

        casePath=self.parser.casePath()
        self.checkCase(casePath)
        
        if self.opts.regions or self.opts.region!=None:
            print "Building Pseudocases"
            sol=SolutionDirectory(casePath,archive=None)
            regions=RegionCases(sol,clean=True)
            
            if self.opts.regions:
                regionNames=sol.getRegions()
            
        self.processPlotLineOptions(autoPath=casePath)

        self.clearCase(SolutionDirectory(casePath,archive=None))

        lam=self.getParallel()
        
        for theRegion in regionNames:
            args=self.buildRegionArgv(casePath,theRegion)
            self.setLogname()
            run=AnalyzedRunner(BoundingLogAnalyzer(progress=self.opts.progress),
                               silent=self.opts.progress,
                               argv=args,
                               server=True,
                               lam=lam,
                               restart=self.opts.restart,
                               logname=self.opts.logname)

            self.addPlotLineAnalyzers(run)
            
            self.addWriteAllTrigger(run,SolutionDirectory(casePath,archive=None))
            self.addLibFunctionTrigger(run,SolutionDirectory(casePath,archive=None))

            run.start()

            self.reportUsage(run)

            if theRegion!=None:
                print "Syncing into master case"
                regions.resync(theRegion)


        if regions!=None:
            if not self.opts.keeppseudo:
                print "Removing pseudo-regions"
                regions.cleanAll()
            else:
                for r in sol.getRegions():
                    if r not in regionNames:
                        regions.clean(r)
