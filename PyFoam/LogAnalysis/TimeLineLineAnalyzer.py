#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/TimeLineLineAnalyzer.py 8415 2013-07-26T11:32:37.193675Z bgschaid  $
"""Line analyzer that collects datga in arrays"""

from .GeneralLineAnalyzer import GeneralLineAnalyzer

class TimeLineLineAnalyzer(GeneralLineAnalyzer):
    """Base class for analyzers that collect data in arrays

    Just a stub to enable legacy code"""
    def __init__(self):
        GeneralLineAnalyzer.__init__(self,doTimelines=True)

# Should work with Python3 and Python2
