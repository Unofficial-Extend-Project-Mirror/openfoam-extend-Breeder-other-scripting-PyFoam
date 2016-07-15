#  ICE Revision: $Id$
"""Analyze Line for Time"""

import re

from .LogLineAnalyzer import LogLineAnalyzer

from PyFoam import configuration as conf

class TimeLineAnalyzer(LogLineAnalyzer):
    """Parses the line for the current time and makes it available to
    the parent analyzer (who makes it available to all of his
    children). This side-effect is important for all the other
    line-analyzers that need the time"""

    def __init__(self,progress=False):
        """
        Constructs the analyzer

        :param progress: whether to print the time on the console
        """
        LogLineAnalyzer.__init__(self)
        self.exp=re.compile(conf().get("SolverOutput","timeRegExp"))

        self.fallback=re.compile("^(Time =|Iteration:) (.+)$")
        self.tryFallback=True

        self.progress=progress

    def notifyNewTime(self,m):
        try:
            self.notify(float(m.group(2)))
            if self.progress and type(self.parent.time)==float:
                self.writeProgress("t = %10g" % self.parent.time)

        except ValueError:
            pass

    def doAnalysis(self,line):
        m=self.exp.match(line.strip())
        if m!=None:
            self.tryFallback=False
            self.notifyNewTime(m)

        if self.tryFallback:
            # this is for cases that use a different regular expression for the time
            m=self.fallback.match(line)
            if m!=None:
                self.notifyNewTime(m)

# Should work with Python3 and Python2
