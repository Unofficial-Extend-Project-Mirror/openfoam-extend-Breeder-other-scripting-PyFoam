#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/StepAnalyzedWatcher.py 8415 2013-07-26T11:32:37.193675Z bgschaid  $
"""An Analyzed Runner that does something at every time-step"""

from .BasicWatcher import BasicWatcher
from .StepAnalyzedCommon import StepAnalyzedCommon

class StepAnalyzedWatcher(StepAnalyzedCommon,BasicWatcher):
    """The output of a command is analyzed while being run. At every time-step a command is performed"""

    def __init__(self,filename,analyzer,silent=False,smallestFreq=0.,tailLength=1000,sleep=0.1):
        """@param smallestFreq: the smallest intervall of real time (in seconds) that the time change is honored"""
        BasicWatcher.__init__(self,filename,silent=silent,tailLength=tailLength,sleep=sleep)
        StepAnalyzedCommon.__init__(self,filename,analyzer,smallestFreq=smallestFreq)

# Should work with Python3 and Python2
