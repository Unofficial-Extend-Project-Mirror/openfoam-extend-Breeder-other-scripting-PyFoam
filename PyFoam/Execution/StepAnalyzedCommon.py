#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/StepAnalyzedCommon.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Common stuff for classes that do something at every timestep"""

from AnalyzedCommon import AnalyzedCommon
from time import time


class StepAnalyzedCommon(AnalyzedCommon):
    """Stuff is performed forevery timestep in the file"""
    
    def __init__(self,filename,analyzer,smallestFreq=0.):
        """@param smallestFreq: the smallest intervall of real time (in seconds) that the time change is honored"""
        AnalyzedCommon.__init__(self,filename,analyzer)

        analyzer.addTimeListener(self)
        self.freq=smallestFreq
        self.oldtime=0.
        
    def timeChanged(self):
        """React to a change of the simulation time in the log"""
        now=time()
        if (now-self.oldtime)>self.freq:
            self.oldtime=now
            self.timeHandle()
            
    def timeHandle(self):
        """Handler that reacts to the change of time. To be overridden be sub-classes"""
        pass
        
