#  ICE Revision: $Id: AnalyzedRunner.py 8292 2007-12-12 15:22:00Z bgschaid $ 
"""Command is run and output is analyzed"""

from BasicRunner import BasicRunner
from AnalyzedCommon import AnalyzedCommon

class AnalyzedRunner(AnalyzedCommon,BasicRunner):
    """The output of a command is analyzed while being run

    Side effects (files written etc) depend on the analyzer"""
    
    def __init__(self,analyzer,argv=None,silent=False,logname="PyFoamSolve",server=False,lam=None,restart=False):
        """ @param analyzer: the analyzer for the output
        argv, silent, logname, server, lam - see BasicRunner"""
        BasicRunner.__init__(self,argv,silent,logname,server=server,lam=lam,restart=restart)
        AnalyzedCommon.__init__(self,logname,analyzer)

    def lineHandle(self,line):
        """Not to be called: calls the analyzer for the current line"""
        AnalyzedCommon.lineHandle(self,line)
        BasicRunner.lineHandle(self,line)

    def lastTime(self):
        return self.getTime()

    def firstCpuTime(self):
        exe=self.getAnalyzer("Execution")
        if exe==None:
            return None
        else:
            return exe.timeFirst()

    def firstClockTime(self):
        exe=self.getAnalyzer("Execution")
        if exe==None:
            return None
        else:
            return exe.clockFirst()        

    def totalCpuTime(self):
        exe=self.getAnalyzer("Execution")
        if exe==None:
            return None
        else:
            return exe.timeTotal()

    def totalClockTime(self):
        exe=self.getAnalyzer("Execution")
        if exe==None:
            return None
        else:
            return exe.clockTotal()

    def stopHandle(self):
        BasicRunner.stopHandle(self)
        self.tearDown()
