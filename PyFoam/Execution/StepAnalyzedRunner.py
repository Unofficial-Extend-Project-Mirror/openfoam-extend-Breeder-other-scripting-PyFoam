#  ICE Revision: $Id: StepAnalyzedRunner.py 10900 2009-09-28 13:04:35Z bgschaid $ 
"""An Analyzed Runner that does something at every time-step"""

from BasicRunner import BasicRunner
from StepAnalyzedCommon import StepAnalyzedCommon

class StepAnalyzedRunner(StepAnalyzedCommon,BasicRunner):
    """The output of a command is analyzed while being run. At every time-step a command is performed"""
    
    def __init__(self,
                 analyzer,
                 argv=None,
                 silent=False,
                 logname="PyFoamSolve",
                 smallestFreq=0.,
                 server=False,
                 remark=None,
                 jobId=None):
        """@param smallestFreq: the smallest intervall of real time (in seconds) that the time change is honored"""
        BasicRunner.__init__(self,
                             argv,
                             silent,
                             logname,
                             server=server,
                             remark=remark,
                             jobId=jobId)
        StepAnalyzedCommon.__init__(self,
                                    logname,
                                    analyzer,
                                    smallestFreq=smallestFreq)
        
    
