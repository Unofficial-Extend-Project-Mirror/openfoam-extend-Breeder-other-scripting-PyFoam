#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/TimeLineAnalyzer.py 2142 2007-10-07T15:16:27.888326Z bgschaid  $ 
"""Analyze Line for Time"""

import re
from sys import stdout

from LogLineAnalyzer import LogLineAnalyzer

class TimeLineAnalyzer(LogLineAnalyzer):
    """Parses the line for the current time and makes it available to
    the parent analyzer (who makes it available to all of his
    children). This side-effect is important for all the other
    line-analyzers that need the time"""

    timeRegExp="^Time = (.+)$"
    
    def __init__(self,progress=False):
        """
        Constructs the analyzer
        
        @param progress: whether to print the time on the console
        """
        LogLineAnalyzer.__init__(self)
        self.exp=re.compile(self.timeRegExp)
        self.progress=progress
        
    def doAnalysis(self,line):
        m=self.exp.match(line)
        if m!=None:
            try:
                self.notify(float(m.group(1)))
                if self.progress:
                    print "\r t = %10g" % self.parent.time,
                    stdout.flush()
                
            except ValueError:
                pass

            
