#  ICE Revision: $Id: SimpleLineAnalyzer.py 7581 2007-06-27 15:29:14Z bgschaid $ 
"""Do analysis for simple expressions"""

import re

# from FileLineAnalyzer import FileLineAnalyzer
# from TimeLineLineAnalyzer import TimeLineLineAnalyzer

from GeneralLineAnalyzer import GeneralLineAnalyzer

class GeneralSimpleLineAnalyzer(GeneralLineAnalyzer):
    """Parses lines for an arbitrary regular expression

    Differs from RegExpLineAnalyzer because it doesn't store its data"""

    def __init__(self,name,exp,idNr=None,idList=None,titles=[],doTimelines=True,doFiles=True):
        """
        @param name: name of the expression (needed for output)
        @param exp: the regular expression
        @param idNr: number of the pattern group that is used as an identifier
        @param idList: numbers of the pattern group that are used from the expression
        @param titles: titles for the data items"""
        GeneralLineAnalyzer.__init__(self,titles=titles,doTimelines=doTimelines,doFiles=doFiles)

        self.name=name
        self.idNr=idNr
        self.idList=idList
        self.strExp=exp
        self.exp=re.compile(self.strExp)
        
    def addToFiles(self,match):
        tm=self.parent.getTime()
        if tm=="":
            return

        name=self.name
        fdata=match.groups()
        if self.idNr!=None:
            ID=match.group(self.idNr)
            name+="_"+ID
            fdata=fdata[:self.idNr-1]+fdata[self.idNr:]

        self.files.write(name,tm,fdata)

    def addToTimelines(self,match):
        tm=self.parent.getTime()
        if tm=="":
            return

        mLen=len(match.groups())
        ids=self.idList
        if ids==None:
            ids=range(mLen)
        for i in range(len(ids)):
            ID=ids[i]
            if ID>=mLen:
                continue
            name="%s_%d" % (self.name,ID)
            if i<len(self.titles):
                name=self.titles[i]
            data=match.groups()[ID]
            self.lines.setValue(name,data)
        
class SimpleLineAnalyzer(GeneralSimpleLineAnalyzer):
    """Parses lines for an arbitrary regular expression

    Differs from RegExpLineAnalyzer because it doesn't store its data"""

    def __init__(self,name,exp,idNr=None,titles=[]):
        """
        @param name: name of the expression (needed for output)
        @param exp: the regular expression
        @param idNr: number of the pattern group that is used as an identifier
        @param titles: titles for the data items"""
        GeneralSimpleLineAnalyzer.__init__(self,name,exp,idNr=idNr,titles=titles,doTimelines=False)

##        self.name=name
##        self.idNr=idNr
        
##        self.strExp=exp
##        self.exp=re.compile(self.strExp)

##    def doAnalysis(self,line):
##        """Analyzes line and writes the data"""
##        tm=self.parent.getTime()
##        if tm=="":
##            return
##        m=self.exp.match(line)
##        if m!=None:
##            name=self.name
##            fdata=m.groups()
##            if self.idNr!=None:
##                ID=m.group(self.idNr)
##                name+="_"+ID
##                fdata=fdata[:self.idNr-1]+fdata[self.idNr:]
                
##            self.files.write(name,tm,fdata)

class TimeLineSimpleLineAnalyzer(GeneralSimpleLineAnalyzer):
    """Parses lines for an arbitrary regular expression"""

    def __init__(self,name,exp,idList=None,titles=[]):
        """@param  name: name of the expression (needed for output)
        @param exp: the regular expression
        @param idList: numbers of the pattern group that are used from the expression
        @param titles: titles for the data items"""

        GeneralSimpleLineAnalyzer.__init__(self,name,exp,idNr=idList,titles=titles,doFiles=False)

##        TimeLineLineAnalyzer.__init__(self)

##        self.name=name
##        self.idList=idList
##        self.titles=titles
##        if len(self.titles)>0 and self.idList==None:
##            self.idList=range(len(self.titles))
            
##        self.strExp=exp
##        self.exp=re.compile(self.strExp)
        
##    def doAnalysis(self,line):
##        """Analyzes line and writes the data"""
##        tm=self.parent.getTime()
##        if tm=="":
##            return
##        m=self.exp.match(line)
##        if m!=None:
##            mLen=len(m.groups())
##            ids=self.idList
##            if ids==None:
##                ids=range(mLen)
##            for i in range(len(ids)):
##                ID=ids[i]
##                if ID>=mLen:
##                    continue
##                name="%s_%d" % (self.name,ID)
##                if i<len(self.titles):
##                    name=self.titles[i]
##                data=m.groups()[ID]
##                self.lines.setValue(name,data)
