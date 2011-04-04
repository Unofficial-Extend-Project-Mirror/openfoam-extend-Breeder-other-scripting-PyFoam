#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/TimeLineLineAnalyzer.py 1906 2007-08-28T16:16:19.392553Z bgschaid  $ 
"""Line analyzer that collects datga in arrays"""

from GeneralLineAnalyzer import GeneralLineAnalyzer

class TimeLineLineAnalyzer(GeneralLineAnalyzer):
    """Base class for analyzers that collect data in arrays

    Just a stub to enable legacy code"""
    def __init__(self):
        GeneralLineAnalyzer.__init__(self,doTimelines=True)
        
