#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/StepAnalyzedCommon.py 6539 2010-05-04T19:25:43.455866Z bgschaid  $ 
"""Common stuff for classes that do something at every timestep"""

from AnalyzedCommon import AnalyzedCommon
from time import time

class StepAnalyzedCommon(AnalyzedCommon):
    """Stuff is performed forevery timestep in the file"""
    
    def __init__(self,filename,analyzer,smallestFreq=0):
        """@param smallestFreq: the smallest intervall of real time (in seconds) that the time change is honored"""
        AnalyzedCommon.__init__(self,filename,analyzer)

        analyzer.addTimeListener(self)
        self.freq=smallestFreq
        self.oldtime=0.
        
    def timeChanged(self):
        """React to a change of the simulation time in the log"""
        now=time()
        if self.freq>0 and (now-self.oldtime)>self.freq:
            self.oldtime=now
            self.timeHandle()
            if self.doPickling:
                self.picklePlots()
            
    def timeHandle(self):
        """Handler that reacts to the change of time. To be overridden be sub-classes"""
        pass
        
    def stopHandle(self):
        if self.doPickling:
            self.picklePlots(wait=True)
