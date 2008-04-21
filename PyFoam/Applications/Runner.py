#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/Runner.py 2881 2008-03-11T18:56:34.676111Z bgschaid  $ 
"""
Application class that implements pyFoamRunner
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.FoamInformation import changeFoamVersion

from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.RegionCases import RegionCases

from PyFoam.Execution.ParallelExecution import LAMMachine

from PyFoam.Error import warning,error

from CommonPlotLines import CommonPlotLines
from CommonClearCase import CommonClearCase
from CommonWriteAllTrigger import CommonWriteAllTrigger

from os import path

class Runner(PyFoamApplication,
             CommonPlotLines,
             CommonWriteAllTrigger,
             CommonClearCase):
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
        self.parser.add_option("--foamVersion",
                               dest="foamVersion",
                               default=None,
                               help="Change the OpenFOAM-version that is to be used")
        self.parser.add_option("--logname",
                               dest="logname",
                               default=None,
                               help="Name of the logfile")
        
        self.parser.add_option("--all-regions",
                               action="store_true",
                               default=False,
                               dest="regions",
                               help="Executes the command for all available regions (builds a pseudo-case for each region)")

        self.parser.add_option("--region",
                               dest="region",
                               default=None,
                               help="Executes the command for a region (builds a pseudo-case for that region)")

        self.parser.add_option("--keep-pseudocases",
                               action="store_true",
                               default=False,
                               dest="keeppseudo",
                               help="Keep the pseudo-cases that were built for a multi-region case")
        self.parser.add_option("--report-usage",
                               action="store_true",
                               default=False,
                               dest="reportUsage",
                               help="After the execution the maximum memory usage is printed to the screen")
        
        CommonPlotLines.addOptions(self)
        CommonClearCase.addOptions(self)
        CommonWriteAllTrigger.addOptions(self)
                               
    def run(self):
        if self.opts.keeppseudo and (not self.opts.regions and self.opts.region==None):
            warning("Option --keep-pseudocases only makes sense for multi-region-cases")
        regionNames=[self.opts.region]
        regions=None
        
        if self.opts.regions or self.opts.region!=None:
            print "Building Pseudocases"
            sol=SolutionDirectory(self.parser.getArgs()[2],archive=None)
            regions=RegionCases(sol,clean=True)
            
            if self.opts.regions:
                regionNames=sol.getRegions()
            
        if self.opts.foamVersion!=None:
            changeFoamVersion(self.opts.foamVersion)
            
        self.processPlotLineOptions(autoPath=path.join(self.parser.getArgs()[1],self.parser.getArgs()[2]))

        self.clearCase(SolutionDirectory(self.parser.getArgs()[2],archive=None))

        lam=None
        if self.opts.procnr!=None or self.opts.machinefile!=None:
            lam=LAMMachine(machines=self.opts.machinefile,nr=self.opts.procnr)

        for theRegion in regionNames:
            args=self.parser.getArgs()[:]
            if theRegion!=None:
                args[2]+="."+theRegion

            if self.opts.logname==None:
                self.opts.logname="PyFoamSolve."+args[0]
                
            run=AnalyzedRunner(BoundingLogAnalyzer(progress=self.opts.progress),silent=self.opts.progress,argv=args,server=True,lam=lam,restart=self.opts.restart,logname=self.opts.logname)

            self.addPlotLineAnalyzers(run)
            
            self.addWriteAllTrigger(run,SolutionDirectory(self.parser.getArgs()[2],archive=None))

            run.start()

            if self.opts.reportUsage:
                print "\n  Used Memory: ",run.run.usedMemory(),"MB"

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
