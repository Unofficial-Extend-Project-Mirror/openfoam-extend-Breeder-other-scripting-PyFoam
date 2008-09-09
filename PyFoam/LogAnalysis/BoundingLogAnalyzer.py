#  ICE Revision: $Id: BoundingLogAnalyzer.py 7832 2007-08-28 13:07:26Z bgschaid $ 
"""Basic log analyer with boundedness"""

from StandardLogAnalyzer import StandardLogAnalyzer

from BoundingLineAnalyzer import GeneralBoundingLineAnalyzer
from SimpleLineAnalyzer import GeneralSimpleLineAnalyzer

from PyFoam.FoamInformation import foamVersionNumber

class BoundingLogAnalyzer(StandardLogAnalyzer):
    """
    This analyzer also checks for bounded solutions
    """
    def __init__(self,progress=False,doTimelines=False,doFiles=True):
        """
        @param progress: Print time progress on console?
        """
        StandardLogAnalyzer.__init__(self,progress=progress,doTimelines=doTimelines,doFiles=doFiles)

        self.addAnalyzer("Bounding",GeneralBoundingLineAnalyzer(doTimelines=doTimelines,doFiles=doFiles))
        
        if foamVersionNumber()<(1,4):
            courantExpression="^Mean and max Courant Numbers = (.+) (.+)$"
        else:
            courantExpression="^Courant Number mean: (.+) max: (.+)$"
            
        self.addAnalyzer("Courant",GeneralSimpleLineAnalyzer("courant",courantExpression,titles=["mean","max"],doTimelines=doTimelines,doFiles=doFiles))

class BoundingPlotLogAnalyzer(BoundingLogAnalyzer):
    """
    This analyzer also checks for bounded solutions
    """
    def __init__(self):
        BoundingLogAnalyzer.__init__(self,progress=True,doTimelines=True,doFiles=False)

##        self.addAnalyzer("Bounding",GeneralBoundingLineAnalyzer())
##        self.addAnalyzer("Courant",TimeLineSimpleLineAnalyzer("courant","^Mean and max Courant Numbers = (.+) (.+)$",titles=["mean","max"]))
