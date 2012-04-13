#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/ConvergenceRunner.py 7636 2011-11-30T13:54:29.838641Z bgschaid  $ 
"""Stop solver at convergence"""

from AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.SteadyConvergedLineAnalyzer import SteadyConvergedLineAnalyzer

class ConvergenceRunner(AnalyzedRunner):
    """It is assumed that the provided solver is a steady state
    solver. After all the linear solvers have initial residuals below
    their limits the run is assumed to be convergent and the run is
    stopped by setting

    stopAt nextWrite;
    writeInterval 1;

    in the controlDict"""
    
    def __init__(self,analyzer,
                 argv=None,
                 silent=False,
                 logname="PyFoamSolve",
                 server=False,
                 lam=None,
                 restart=False,
                 compressLog=False,
                 noLog=False,
                 logTail=None,
                 remark=None,
                 jobId=None):
        """See AnalyzedRunner"""
        AnalyzedRunner.__init__(self,
                                analyzer,
                                argv,
                                silent,
                                logname,
                                server=server,
                                lam=lam,
                                compressLog=compressLog,
                                restart=restart,
                                noLog=noLog,
                                logTail=logTail,
                                remark=remark,
                                jobId=jobId)
        
        self.analyzer.addAnalyzer("Convergence",SteadyConvergedLineAnalyzer())
        
    def lineHandle(self,line):
        """Not to be called: Stops the solver"""
        AnalyzedRunner.lineHandle(self,line)

        if not self.analyzer.goOn():
            self.stopGracefully()
            
        
