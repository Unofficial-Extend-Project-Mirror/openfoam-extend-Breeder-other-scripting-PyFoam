#  ICE Revision: $Id: GeneralLineAnalyzer.py 8292 2007-12-12 15:22:00Z bgschaid $ 
"""Line analyzer with output and the capability to store lines"""

from LogLineAnalyzer import LogLineAnalyzer
from PyFoam.Basics.OutFileCollection import OutFileCollection
from PyFoam.Basics.TimeLineCollection import TimeLineCollection

class GeneralLineAnalyzer(LogLineAnalyzer):
    """Base class for analyzers that write data to files and store time-lines

    Combines the capabilities of TimeLineLineAnalyzer and FileLineAnalyzer"""
    
    def __init__(self,doTimelines=False,doFiles=False,titles=[]):
        """
        @param titles: The titles of the data elements
        """
        LogLineAnalyzer.__init__(self)

        self.doTimelines=doTimelines
        self.doFiles=doFiles
        
        self.files=None
        self.titles=titles
        
        self.setTitles(titles)
        if self.doTimelines:
            self.lines=TimeLineCollection()
        else:
            self.lines=None
            
    def setTitles(self,titles):
        """
        Sets the titles anew
        @param titles: the new titles
        """
        if self.doFiles:
            self.titles=titles
            if self.files!=None:
                self.files.setTitles(titles)
            
    def setDirectory(self,oDir):
        """Creates the OutFileCollection-object"""
        if self.doFiles:
            self.files=OutFileCollection(oDir,titles=self.titles)
        else:
            self.files=None

    def timeChanged(self):
        """Sets the current time in the timelines"""
        if self.doTimelines:
            self.lines.setTime(self.getTime())

    def getTimeline(self,name):
        """@param name: Name of the timeline to return
        @return: the timeline as two list: the times and the values"""
        if self.doTimelines:
            return self.lines.getTimes(),self.lines.getValues(name)
        else:
            return [],[]

    def doAnalysis(self,line):
        """General analysis method. Derived classes should instead override callbacks"""
        
        m=self.exp.match(line)
        if m!=None:
            self.startAnalysis(m)
            
            if self.doTimelines:
                self.addToTimelines(m)
            if self.doFiles:
                self.addToFiles(m)

            self.endAnalysis(m)

    def startAnalysis(self,match):
        """Method at the start of a successfull match"""
        pass
    
    def endAnalysis(self,match):
        """Method at the end of a successfull match"""
        pass
    
    def addToTimelines(self,match):
        """Method that adds matched data to timelines

        @param match: data matched by a regular expression"""
        
        pass

    def addToFiles(self,match):
        """Method that adds matched data to files

        @param match: data matched by a regular expression"""
        
        pass

    def tearDown(self):
        """Closes files"""
        LogLineAnalyzer.tearDown(self)

        if self.files!=None:
            self.files.close()
            
