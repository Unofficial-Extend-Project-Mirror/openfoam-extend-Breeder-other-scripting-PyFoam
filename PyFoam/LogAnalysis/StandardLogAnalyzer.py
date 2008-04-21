#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/StandardLogAnalyzer.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Analyze standard solver"""

from FoamLogAnalyzer import FoamLogAnalyzer

from ContinuityLineAnalyzer import GeneralContinuityLineAnalyzer
from LinearSolverLineAnalyzer import GeneralLinearSolverLineAnalyzer,GeneralLinearSolverIterationsLineAnalyzer
from ExecutionTimeLineAnalyzer import GeneralExecutionLineAnalyzer
from DeltaTLineAnalyzer import GeneralDeltaTLineAnalyzer

class StandardLogAnalyzer(FoamLogAnalyzer):
    """
    The analyzer for the most common OpenFOAM solvers

    It checks:
     - Continuity
     - the Linear solvers
     - Execution time
    """
    def __init__(self,progress=False,doTimelines=False,doFiles=True):
        """
        @param progress: Print time progress on console?
        @param doTimelines: generate timelines?
        @param doFiles: generate files?
        """
        FoamLogAnalyzer.__init__(self,progress=progress)

        self.addAnalyzer("Continuity",GeneralContinuityLineAnalyzer(doTimelines=doTimelines,doFiles=doFiles))
        self.addAnalyzer("Linear",GeneralLinearSolverLineAnalyzer(doTimelines=doTimelines,doFiles=doFiles))
        self.addAnalyzer("Iterations",GeneralLinearSolverIterationsLineAnalyzer(doTimelines=doTimelines,doFiles=doFiles))
        self.addAnalyzer("Execution",GeneralExecutionLineAnalyzer(doTimelines=doTimelines,doFiles=doFiles))
        self.addAnalyzer("DeltaT",GeneralDeltaTLineAnalyzer(doTimelines=doTimelines,doFiles=doFiles))

class StandardPlotLogAnalyzer(StandardLogAnalyzer):
    """This analyzer checks the current residuals and generates timelines"""
    def __init__(self):
        StandardLogAnalyzer.__init__(self,progress=True,doTimelines=True,doFiles=False)
        
##        self.addAnalyzer("PlotContinuity",GeneralContinuityLineAnalyzer())
##        self.addAnalyzer("PlotLinear",GeneralLinearSolverLineAnalyzer())
##        self.addAnalyzer("PlotIterations",GeneralLinearSolverIterationsLineAnalyzer())
##        self.addAnalyzer("PlotExecution",GeneralExecutionLineAnalyzer())
        
