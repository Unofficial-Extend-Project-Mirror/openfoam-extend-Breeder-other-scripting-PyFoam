#  ICE Revision: $Id$
"""Analyzes lines with regular expressions"""

import re

from .GeneralLineAnalyzer import GeneralLineAnalyzer

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

    def __init__(self,
                 name,
                 exp,
                 idNr=None,
                 titles=[],
                 doTimelines=False,
                 doFiles=True,
                 accumulation=None,
                 progressTemplate=None,
                 singleFile=False,
                 startTime=None,
                 endTime=None):
        """
        :param name: name of the expression (needed for output
        :param exp: the regular expression, %f% will be replaced with the
        regular expression for a float
        :param idNr: number of the pattern group that is used as an identifier
        :param titles: titles of the columns
        :param accumulation: How multiple values should be accumulated
        """
        GeneralLineAnalyzer.__init__(self,
                                     titles=titles,
                                     doTimelines=doTimelines,
                                     doFiles=doFiles,
                                     accumulation=accumulation,
                                     progressTemplate=progressTemplate,
                                     singleFile=singleFile,
                                     startTime=startTime,
                                     endTime=endTime)

        self.name=name
        self.idNr=idNr

        self.multiLine=False
        self.linesToMatch=None

        exp=exp.replace("%f%",self.floatRegExp)

        self.strExp=exp
        reFlags=0

        if self.strExp.find(r"\n")>-1:
            self.multiLine=True
            from collections import deque

            self.linesToMatch=deque([],maxlen=1+self.strExp.count(r'\n'))
            reFlags=re.MULTILINE

        self.exp=re.compile(self.strExp,reFlags)

        self.data={}

    def stringToMatch(self,line):
        """Returns string to match. To be overriden for multi-line expressions"""
        if self.multiLine:
            self.linesToMatch.append(line)

            return "\n".join(self.linesToMatch)
        else:
            return line.strip()

    def startAnalysis(self,match):
        self.tm=self.parent.getTime()
        if self.tm=="":
            self.tm="-1e10"

    def makeID(self,match):
        if isinstance(self.idNr,(int,)):
            return match.group(self.idNr)
        else:
            return "_".join(match.group(i) for i in self.idNr)

    def filterIdFromData(self,fdata):
        if isinstance(self.idNr,(int,)):
            return fdata[:self.idNr-1]+fdata[self.idNr:]
        else:
            return [fdata[i] for i in range(len(fdata)) if i+1 not in self.idNr]

    def addToFiles(self,match):
        name=self.fName(self.name)
        fdata=match.groups()
        if self.idNr!=None:
            ID=self.makeID(match)
            name+="_"+ID
            fdata=self.filterIdFromData(fdata)
        else:
            ID=""

        self.sub(ID)[float(self.tm)]=fdata
        if ID!="":
            self.sub("")[float(self.tm)]=match.groups()

        self.files.write(name,self.tm,fdata)

    def addToTimelines(self,match):
        name=self.fName(self.name)
        fdata=match.groups()

        prefix=""
        if self.idNr!=None:
            ID=self.makeID(match)
            prefix=ID+"_"
            fdata=self.filterIdFromData(fdata)

        for i in range(len(fdata)):
            val=float(fdata[i])
            name=prefix+"value %d" % i
            if i<len(self.titles):
                if self.idNr!=None and self.titles[i].find("%s")>=0:
                    name=self.titles[i] % ID
                else:
                    name=prefix+str(self.titles[i])

            self.lines.setValue(self.fName(name),val)

    def sub(self,ID):
        """ get the data set for the identifier ID"""
        if ID not in self.data:
            self.data[ID]={}
        return self.data[ID]

    def getTimes(self,ID=None):
        """get the available time for the identifier ID"""
        if ID==None:
            ID=""
        return list(self.sub(ID).keys())

    def getIDs(self):
        """get a list of the available IDs"""
        ids=list(self.data.keys())
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

        if time in data:
            return data[time]
        else:
            return None

class RegExpTimeLineLineAnalyzer(RegExpLineAnalyzer):
    """Class that stores results as timelines, too"""

    def __init__(self,
                 name,
                 exp,
                 titles=[],
                 startTime=None,
                 endTime=None):
        """
        :param name: name of the expression (needed for output
        :param exp: the regular expression, %f% will be replaced with the
        regular expression for a float
        :param titles: titles of the columns
        """
        RegExpLineAnalyzer.__init__(self,
                                    name,
                                    exp,
                                    idNr=None,
                                    titles=titles,
                                    doTimelines=True,
                                    doFiles=False,
                                    startTime=startTime,
                                    endTime=endTime)

# Should work with Python3 and Python2
