#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/ContinuityLineAnalyzer.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Check lines for continuity information"""

import re

continutityRegExp="^time step continuity errors : sum local = (.+), global = (.+), cumulative = (.+)$"
    
# from FileLineAnalyzer import FileLineAnalyzer
# from TimeLineLineAnalyzer import TimeLineLineAnalyzer

from GeneralLineAnalyzer import GeneralLineAnalyzer

class GeneralContinuityLineAnalyzer(GeneralLineAnalyzer):
    """Parses line for continuity information"""

    def __init__(self,doTimelines=True,doFiles=True):
        GeneralLineAnalyzer.__init__(self,titles=["Local","Global","Cumulative"],doTimelines=doTimelines,doFiles=doFiles)
        self.exp=re.compile(continutityRegExp)

    def addToFiles(self,match):
        self.files.write("continuity",self.parent.getTime(),match.groups())

    def addToTimelines(self,match):
        self.lines.setValue("Global",match.groups()[1]) 
        self.lines.setValue("Cumulative",match.groups()[2]) 
        
class ContinuityLineAnalyzer(GeneralContinuityLineAnalyzer):
    """Parses line for continuity information"""

    def __init__(self):
        GeneralContinuityLineAnalyzer.__init__(self,doTimelines=False)

        
##        self.exp=re.compile(continutityRegExp)

##    def doAnalysis(self,line):
##        m=self.exp.match(line)
##        if m!=None:
##            self.files.write("continuity",self.parent.getTime(),m.groups())
            
    
class TimeLineContinuityLineAnalyzer(GeneralContinuityLineAnalyzer):
    """Parses line for continuity information"""

    def __init__(self):
        GeneralContinuityLineAnalyzer.__init__(self,doFiles=False)
##        self.exp=re.compile(continutityRegExp)

##    def doAnalysis(self,line):
##        m=self.exp.match(line)
##        if m!=None:
##            #            self.lines.setValue("Local",m.groups()[0]) 
##            self.lines.setValue("Global",m.groups()[1]) 
##            self.lines.setValue("Cumulative",m.groups()[2]) 
    
