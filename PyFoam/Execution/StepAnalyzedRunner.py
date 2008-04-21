#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/StepAnalyzedRunner.py 1906 2007-08-28T16:16:19.392553Z bgschaid  $ 
"""An Analyzed Runner that does something at every time-step"""

from BasicRunner import BasicRunner
from StepAnalyzedCommon import StepAnalyzedCommon

class StepAnalyzedRunner(StepAnalyzedCommon,BasicRunner):
    """The output of a command is analyzed while being run. At every time-step a command is performed"""
    
    def __init__(self,analyzer,argv=None,silent=False,logname="PyFoamSolve",smallestFreq=0.,server=False):
        """@param smallestFreq: the smallest intervall of real time (in seconds) that the time change is honored"""
        BasicRunner.__init__(self,argv,silent,logname,server=server)
        StepAnalyzedCommon.__init__(self,logname,analyzer,smallestFreq=smallestFreq)
        
    
