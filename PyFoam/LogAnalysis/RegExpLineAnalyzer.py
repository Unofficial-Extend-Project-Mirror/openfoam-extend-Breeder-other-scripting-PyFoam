#  ICE Revision: $Id: RegExpLineAnalyzer.py 7581 2007-06-27 15:29:14Z bgschaid $ 
"""Analyzes lines with regular expressions"""

import re

# from FileLineAnalyzer import FileLineAnalyzer
# from TimeLineLineAnalyzer import TimeLineLineAnalyzer

from GeneralLineAnalyzer import GeneralLineAnalyzer

class RegExpLineAnalyzer(GeneralLineAnalyzer):
    """Parses lines for an arbitrary regular expression

    Only one data-set is stored per time-step

    One pattern group of the RegExp can be used as a unique
    identifier, so that more than one data-sets can be stored per
    time-step

    The string %f% in the regular expression is replaced with the
    regular expression for a floating point number
    """

    floatRegExp="[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"
    
    def __init__(self,name,exp,idNr=None,titles=[],doTimelines=False,doFiles=True):
        """
        @param name: name of the expression (needed for output
        @param exp: the regular expression, %f% will be replaced with the
        regular expression for a float
        @param idNr: number of the pattern group that is used as an identifier
        @param titles: titles of the columns
        """
        GeneralLineAnalyzer.__init__(self,titles=titles,doTimelines=doTimelines,doFiles=doFiles)

        self.name=name
        self.idNr=idNr

        exp=exp.replace("%f%",self.floatRegExp)

        self.strExp=exp
        self.exp=re.compile(self.strExp)

        self.data={}
        
    def startAnalysis(self,match):
        self.tm=self.parent.getTime()
        if self.tm=="":
            self.tm="-1e10"
            
    def addToFiles(self,match):
        name=self.name
        fdata=match.groups()
        if self.idNr!=None:
            ID=match.group(self.idNr)
            name+="_"+ID
            fdata=fdata[:self.idNr-1]+fdata[self.idNr:]
        else:
            ID=""

        self.sub(ID)[float(self.tm)]=fdata
        if ID!="":
            self.sub("")[float(self.tm)]=match.groups()

        self.files.write(name,self.tm,fdata)

    def addToTimelines(self,match):
        name=self.name
        fdata=match.groups()

        for i in range(len(fdata)):
            val=float(fdata[i])
            name="value %d" % i
            if i<len(self.titles):
                name=self.titles[i]

            self.lines.setValue(name,val)
        
    def sub(self,ID):
        """ get the data set for the identifier ID"""
        if not self.data.has_key(ID):
            self.data[ID]={}
        return self.data[ID]
    
    def getTimes(self,ID=None):
        """get the available time for the identifier ID"""
        if ID==None:
            ID=""
        return self.sub(ID).keys()

    def getIDs(self):
        """get a list of the available IDs"""
        ids=self.data.keys()
        if "" in ids:
            ids.remove("")
        return ids
    
    def getLast(self,ID=None):
        """get the last time for the identifier ID"""
        times=self.getTimes(ID)
        if len(times)>0:
            return max(times)
        else:
            return None
        
    def getData(self,time=None,ID=None):
        """get a data value at a specific time for a specific ID"""
        if ID==None:
            ID=""

        if time==None:
            time=self.getLast(ID)
        else:
            time=float(time)
            
        data=self.sub(ID)
        
        if data.has_key(time):
            return data[time]
        else:
            return None
        
class RegExpTimeLineLineAnalyzer(RegExpLineAnalyzer):
    """Class that stores results as timelines, too"""
    
    def __init__(self,name,exp,titles=[]):
        """
        @param name: name of the expression (needed for output
        @param exp: the regular expression, %f% will be replaced with the
        regular expression for a float
        @param titles: titles of the columns
        """
        RegExpLineAnalyzer.__init__(self,name,exp,idNr=None,titles=titles,doTimelines=True,doFiles=False)

