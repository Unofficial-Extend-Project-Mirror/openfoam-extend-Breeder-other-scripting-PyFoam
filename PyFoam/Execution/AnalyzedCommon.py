#  ICE Revision: $Id: AnalyzedCommon.py 8317 2007-12-21 14:45:09Z bgschaid $ 
"""Common stuff for classes that use analyzers"""

from os import path,mkdir

class AnalyzedCommon(object):
    """This class collects information and methods that are needed for
    handling analyzers"""

    def __init__(self,filename,analyzer):
        """@param filename: name of the file that is being analyzed
        @param analyzer: the analyzer itself"""

        self.analyzer=analyzer

        if 'dir' in dir(self):
            self.logDir=path.join(self.dir,filename+".analyzed")
        else:
            self.logDir=filename+".analyzed"
            
        if not path.exists(self.logDir):
            mkdir(self.logDir)
        
        self.reset()

    def tearDown(self):
        self.analyzer.tearDown()

    def listAnalyzers(self):
        """@returns: A list with the names of the analyzers"""
        return self.analyzer.listAnalyzers()
    
    def getAnalyzer(self,name):
        """@param name: name of the LineAnalyzer to get"""
        return self.analyzer.getAnalyzer(name)
    
    def addAnalyzer(self,name,analyzer):
        """@param name: name of the LineAnalyzer to add
        @param analyzer: the analyzer to add"""
        analyzer.setDirectory(self.logDir)
        return self.analyzer.addAnalyzer(name,analyzer)
    
    def lineHandle(self,line):
        """Not to be called: calls the analyzer for the current line"""
        self.analyzer.analyzeLine(line)
        
    def reset(self):
        """reset the analyzer"""
        self.analyzer.setDirectory(self.logDir)

    def getDirname(self):
        """Get the name of the directory where the data is written to"""
        return self.logDir
    
    def getTime(self):
        """Get the execution time"""
        return self.analyzer.getTime()
        
    def addTrigger(self,time,func,once=True,until=None):
        """Adds a timed trigger to the Analyzer
        @param time: the time at which the function should be triggered
        @param func: the trigger function
        @param once: Should this function be called once or at every time-step
        @param until: The time until which the trigger should be called"""

        self.analyzer.addTrigger(time,func,once=once,until=until)
        
