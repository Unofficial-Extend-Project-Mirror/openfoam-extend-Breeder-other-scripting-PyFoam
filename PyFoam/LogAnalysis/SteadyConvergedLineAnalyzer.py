#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/SteadyConvergedLineAnalyzer.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Analyze Steady Solver"""

import re

from LogLineAnalyzer import LogLineAnalyzer

class SteadyConvergedLineAnalyzer(LogLineAnalyzer):
    """
    Checks whether a Steady-solver has converged

    Convergence is assumed if all the linear solvers have their
    initial residual below their threshold
    """

    linearRegExp="^(.+):  Solving for (.+), Initial residual = (.+), Final residual = (.+), No Iterations (.+)$"
    
    def __init__(self):
        LogLineAnalyzer.__init__(self)
        self.exp=re.compile(self.linearRegExp)
        self.firstTime=True
        self.lastTime=""
        self.isConverged=False
        self.counter=0
        
    def doAnalysis(self,line):
        """Counts the number of linear solvers that have not converged"""
        time=self.parent.getTime()
        if time!=self.lastTime:
            if self.firstTime:
                self.firstTime=False
            else:
                if self.counter==0:
                    self.isConverged=True
                else:
                    self.isConverged=False
                self.counter=0
            self.lastTime=time
            
        m=self.exp.match(line)
        if m!=None:
            if int(m.group(5))>0:
                self.counter+=1
    
    def goOn(self):
        """Converged
        @return: False if converged"""
        return not self.isConverged
