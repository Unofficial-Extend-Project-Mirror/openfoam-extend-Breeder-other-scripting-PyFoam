#  ICE Revision: $Id: TimeLineLineAnalyzer.py 7832 2007-08-28 13:07:26Z bgschaid $ 
"""Line analyzer that collects datga in arrays"""

from GeneralLineAnalyzer import GeneralLineAnalyzer

class TimeLineLineAnalyzer(GeneralLineAnalyzer):
    """Base class for analyzers that collect data in arrays

    Just a stub to enable legacy code"""
    def __init__(self):
        GeneralLineAnalyzer.__init__(self,doTimelines=True)
        
