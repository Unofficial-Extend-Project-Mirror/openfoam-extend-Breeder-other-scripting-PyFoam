#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/LogLineAnalyzer.py 2494 2007-12-14T14:37:46.025021Z bgschaid  $ 
"""Base class for analyzing lines"""

from PyFoam.Error import error

class LogLineAnalyzer(object):
    """Base class for the analysis of all lines from a OpenFOAM-log

    Lines are available one at a time"""
    
    def __init__(self):
        self.parent=None
        self.eventListeners=[]
        
    def doAnalysis(self,line):
        """Analyze a line

        line - the line to be analyzed

        This method carries the main functionality in the sub-classes"""
        pass

    def timeChanged(self):
        """The value of the time has changed in the Log-file
        
        For subclasses that need to know the current time"""
        pass
    
    def setParent(self,parent):
        """Introduces the LineAnalyzer to its supervisor

        @param parent: The Analyzer class of which this is a part"""
        self.parent=parent
        
    def setDirectory(self,oDir):
        """Set the directory to which output is to be written (if any
        output is written)"""
        pass
    
    def goOn(self):
        """If the analyzer thinks the simulation should be stopped
        (for instance because of convergence) it returns false"""
        return True

    def getTime(self):
        """@returns: current time"""
        return self.parent.getTime()

    def addListener(self,func):
        """@param func: a new listener-function that gets notified every time
        the line-analyzer encounters something interesting"""

        self.eventListeners.append(func)

    def notify(self,*data):
        """Notifys the event listeners of an event
        @param data: The data of the event. Everything is possible"""

        for f in self.eventListeners:
            f(*data)
            
    def tearDown(self):
        """Hook to let every analyzer give its stuff back when the analysis has ended"""
        pass
    
