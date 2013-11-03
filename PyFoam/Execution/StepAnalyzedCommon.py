#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/StepAnalyzedCommon.py 8033 2012-05-11T23:38:01.081636Z bgschaid  $ 
"""Common stuff for classes that do something at every timestep"""

from PyFoam.ThirdParty.six import print_

from PyFoam.Execution.AnalyzedCommon import AnalyzedCommon
from time import time

picklingFreqFactor=50

class StepAnalyzedCommon(AnalyzedCommon):
    """Stuff is performed forevery timestep in the file"""
    
    def __init__(self,
                 filename,
                 analyzer,
                 writePickled=True,
                 smallestFreq=0):
        """@param smallestFreq: the smallest intervall of real time (in seconds) that the time change is honored"""
        AnalyzedCommon.__init__(self,
                                filename,
                                analyzer,
                                doPickling=writePickled)

        analyzer.addTimeListener(self)
        self.freq=smallestFreq
        self.oldtime=0.
        self.lastPickleDuration=0
        
    def timeChanged(self):
        """React to a change of the simulation time in the log"""
        now=time()
        if self.freq>0 and (now-self.oldtime)>max(self.lastPickleDuration*picklingFreqFactor,self.freq):
            self.timeHandle()
            if self.doPickling:
                self.picklePlots()
                # store this to make sure that pickling is not the only thing we do
                self.lastPickleDuration=time()-now
                if self.lastPickleDuration*picklingFreqFactor>self.freq:
                    print_("Duration of pickling",self.lastPickleDuration,
                           "too long. Extending frequency from",self.freq,
                           "to",self.lastPickleDuration*picklingFreqFactor)
            self.oldtime=time()
            
    def timeHandle(self):
        """Handler that reacts to the change of time. To be overridden be sub-classes"""
        pass
        
    def stopHandle(self):
        if self.doPickling:
            self.picklePlots(wait=True)
