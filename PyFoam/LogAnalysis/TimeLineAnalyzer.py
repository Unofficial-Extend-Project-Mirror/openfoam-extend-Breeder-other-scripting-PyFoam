#  ICE Revision: $Id: TimeLineAnalyzer.py 11642 2010-06-01 08:19:35Z bgschaid $ 
"""Analyze Line for Time"""

import re
from sys import stdout

from LogLineAnalyzer import LogLineAnalyzer

from PyFoam import configuration as conf

class TimeLineAnalyzer(LogLineAnalyzer):
    """Parses the line for the current time and makes it available to
    the parent analyzer (who makes it available to all of his
    children). This side-effect is important for all the other
    line-analyzers that need the time"""

    def __init__(self,progress=False):
        """
        Constructs the analyzer
        
        @param progress: whether to print the time on the console
        """
        LogLineAnalyzer.__init__(self)
        self.exp=re.compile(conf().get("SolverOutput","timeRegExp"))
        self.progress=progress
        
    def doAnalysis(self,line):
        m=self.exp.match(line)
        if m!=None:
            try:
                self.notify(float(m.group(2)))
                if self.progress and type(self.parent.time)==float:
                    print "\r t = %10g" % self.parent.time,
                    stdout.flush()
                
            except ValueError:
                pass

            
