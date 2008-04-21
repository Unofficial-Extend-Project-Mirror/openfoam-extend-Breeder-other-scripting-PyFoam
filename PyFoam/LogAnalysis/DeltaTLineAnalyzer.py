#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/DeltaTLineAnalyzer.py 2142 2007-10-07T15:16:27.888326Z bgschaid  $ 
"""Check lines for timestep information"""

import re

continutityRegExp="^deltaT = (.+)$"
    
# from FileLineAnalyzer import FileLineAnalyzer
# from TimeLineLineAnalyzer import TimeLineLineAnalyzer

from GeneralLineAnalyzer import GeneralLineAnalyzer

class GeneralDeltaTLineAnalyzer(GeneralLineAnalyzer):
    """Parses line for continuity information"""

    def __init__(self,doTimelines=True,doFiles=True):
        GeneralLineAnalyzer.__init__(self,titles=["deltaT"],doTimelines=doTimelines,doFiles=doFiles)
        self.exp=re.compile(continutityRegExp)

    def addToFiles(self,match):
        self.files.write("deltaT",self.parent.getTime(),match.groups())

    def addToTimelines(self,match):
        self.lines.setValue("deltaT",match.groups()[0]) 
        
class DeltaTLineAnalyzer(GeneralDeltaTLineAnalyzer):
    """Parses line for continuity information"""

    def __init__(self):
        GeneralDeltaTLineAnalyzer.__init__(self,doTimelines=False)

            
    
class TimeLineDeltaTLineAnalyzer(GeneralDeltaTLineAnalyzer):
    """Parses line for continuity information"""

    def __init__(self):
        GeneralDeltaTLineAnalyzer.__init__(self,doFiles=False)
    
