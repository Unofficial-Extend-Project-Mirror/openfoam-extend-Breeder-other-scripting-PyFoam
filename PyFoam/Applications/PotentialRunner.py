#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/PotentialRunner.py 2535 2007-12-30T10:08:58.891162Z bgschaid  $ 
"""
Application class that implements pyFoamSteadyRunner
"""

from os import path,environ

from PyFoamApplication import PyFoamApplication
from PyFoam.FoamInformation import changeFoamVersion

from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Execution.ParallelExecution import LAMMachine
from PyFoam.Error import warning,error

class PotentialRunner(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Runs the potentialFoam solver on a case to get a decent initial condition.

Copies the current fields for U and p to backup-files.
        """

        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <caseDirectory>",
                                   interspersed=True,
                                   nr=1)

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
        self.parser.add_option("--foamVersion",
                               dest="foamVersion",
                               default=None,
                               help="Change the OpenFOAM-version that is to be used")
        self.parser.add_option("--non-orthogonal-correctors",
                               type="int",
                               dest="noCorr",
                               default=None,
                               help="The number of non-orthogonal corrections")
        self.parser.add_option("--tolerance",
                               type="float",
                               dest="tolerance",
                               default=None,
                               help="Overwrite the tolerance of the linear solver")
        self.parser.add_option("--relTol",
                               type="float",
                               dest="relTol",
                               default=None,
                               help="Overwrite the relative tolerance of the linear solver")
        self.parser.add_option("--no-write-p",
                               action="store_false",
                               dest="writep",
                               default=True,
                               help="Don't write pressure p")
        self.parser.add_option("--pRefCell",
                               type="int",
                               dest="pRefCell",
                               default=None,
                               help="Sets the number of the reference cell for closed cases")
        self.parser.add_option("--pRefValue",
                               type="int",
                               dest="pRefValue",
                               default=None,
                               help="Sets the pressure reference value for closed cases")

    def run(self):
        if self.opts.foamVersion!=None:
            changeFoamVersion(self.opts.foamVersion)
            
        cName=self.parser.getArgs()[0]
        sol=SolutionDirectory(cName,archive=None)
        initial=sol[0]
        if "U" not in initial or "p" not in initial:
            error("Either 'p' or 'U' missing from the initial directory",initial.baseName())
        if self.opts.writep:
            initial["p.prepotential"]=initial["p"]
        initial["U.prepotential"]=initial["U"]
        
        lam=None
        if self.opts.procnr!=None or self.opts.machinefile!=None:
            lam=LAMMachine(machines=self.opts.machinefile,nr=self.opts.procnr)

        if self.opts.writep:
            writep=["-writep"]
        else:
            writep=[]
            
        run=BasicRunner(argv=["potentialFoam",".",cName]+writep,
                        server=False,
                        logname="PotentialFoam",
                        lam=lam)

        print "Setting system-directory for potentialFoam"
        trig=PotentialTrigger(sol,
                              self.opts.noCorr,
                              self.opts.tolerance,
                              self.opts.relTol,
                              pRefCell=self.opts.pRefCell,
                              pRefValue=self.opts.pRefValue)
        run.addEndTrigger(trig.resetIt)

        run.start()

import re
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

class PotentialTrigger:
    def __init__(self,sol,correctors,tolerance,relTol,pRefValue=None,pRefCell=None):
        self.solution=ParsedParameterFile(path.join(sol.systemDir(),"fvSolution"),backup=True)
        self.schemes=ParsedParameterFile(path.join(sol.systemDir(),"fvSchemes"),backup=True)
        self.control=ParsedParameterFile(path.join(sol.systemDir(),"controlDict"),backup=True)
        pot=SolutionDirectory(path.join(environ["FOAM_TUTORIALS"],"potentialFoam","cylinder"),archive=None,paraviewLink=False)
        
        self.fresh=True
        
        try:
            if "SIMPLE" not in self.solution:
                self.solution["SIMPLE"]=ParsedParameterFile(path.join(pot.systemDir(),"fvSolution"),backup=False)["SIMPLE"]

            if "nNonOrthogonalCorrectors" not in self.solution["SIMPLE"] and correctors==None:
                correctors=3
                warning("Setting number of correctors to default value",correctors)
            if correctors!=None:
                self.solution["SIMPLE"]["nNonOrthogonalCorrectors"]=correctors

            if pRefCell!=None:
                self.solution["SIMPLE"]["pRefCell"]=pRefCell
            if pRefValue!=None:
                self.solution["SIMPLE"]["pRefValue"]=pRefValue
                
            if tolerance!=None:
                self.solution["solvers"]["p"][1]["tolerance"]=tolerance
            if relTol!=None:
                self.solution["solvers"]["p"][1]["relTol"]=relTol
                
            self.schemes.content=ParsedParameterFile(path.join(pot.systemDir(),"fvSchemes"),backup=False).content
            self.control.content=ParsedParameterFile(path.join(pot.systemDir(),"controlDict"),backup=False).content
            
            self.solution.writeFile()
            self.schemes.writeFile()
            self.control.writeFile()
        except Exception,e:
            warning("Restoring defaults")
            self.solution.restore()
            self.schemes.restore()
            self.control.restore()
            raise e
        
    def resetIt(self):
        if self.fresh:
            warning("Trigger called: Resetting fvSchemes and fvSolution")
            self.solution.restore()
            self.schemes.restore()
            self.control.restore()
            self.fresh=False
