#  ICE Revision: $Id$
"""Analyze OpenFOAM logs"""

from .TimeLineAnalyzer import TimeLineAnalyzer
from PyFoam.Basics.LineReader import LineReader
from PyFoam.Error import error

from PyFoam.Basics.ProgressOutput import ProgressOutput
from PyFoam import configuration as config

from sys import stdout

from copy import deepcopy

import re

class FoamLogAnalyzer(object):
    """Base class for all analyzers

    Administrates and calls a number of LogLineAnlayzers for each
    line"""

    def __init__(self,progress=False):
        """
        :param progress: Print time progress on console?
        """
        self.analyzers={}
        self.time=""
        self.oDir=""
        self.line=LineReader(config().getboolean("SolverOutput","stripSpaces"))
        self.timeListeners=[]
        self.timeTriggers=[]

        self.customExpr=re.compile("Custom([0-9]+)_(.+)")

        self.progressOut=None
        if progress:
            self.progressOut=ProgressOutput(stdout)

        tm=TimeLineAnalyzer(progress=progress)
        self.addAnalyzer("Time",tm)
        tm.addListener(self.setTime)

    def tearDown(self):
        """Remove reference to self in children (hoping to remove
        circular dependencies)"""

        for a in list(self.analyzers.values()):
            a.tearDown()
            a.setParent(None)

    def collectData(self):
        """Collect dictionaries of collected data (current state)
        from the analyzers
        :return: the dictionary"""

        result={}

        for nm in self.analyzers:
            data=self.analyzers[nm].getCurrentData()
            if len(data)>0:
                m=self.customExpr.match(nm)
                if m:
                    if not "Custom" in result:
                        result["Custom"]={}
                    nr,name=m.groups()
                    result["Custom"][name]=data

                # this will store custom data twice. But we'll keep it
                    # for backward-compatibility
                result[nm]=data

        return result

    def setTime(self,time):
        """Sets the time and alert all the LineAnalyzers that the time has changed
        :param time: the new value of the time
        """
        if time!=self.time:
            if self.progressOut:
                self.progressOut.reset()

            self.time=time
            for listener in self.timeListeners:
                listener.timeChanged()
            for nm in self.analyzers:
                self.analyzers[nm].timeChanged()
            self.checkTriggers()

            data=self.collectData()
            for listener in self.timeListeners:
                try:
                    # make sure everyone gets a separate copy
                    listener.setDataSet(deepcopy(data))
                except AttributeError:
                    # seems that the listener doesn't want the data
                    pass

    def writeProgress(self,msg):
        """Write a message to the progress output"""
        if self.progressOut:
            self.progressOut(msg)

    def addTimeListener(self,listener):
        """:param listener: An object that is notified when the time changes. Has to
        implement a timeChanged method"""
        if not 'timeChanged' in dir(listener):
            error("Error. Object has no timeChanged-method:"+str(listener))
        else:
            self.timeListeners.append(listener)

    def listAnalyzers(self):
        """:returns: A list with the names of the Analyzers"""
        return list(self.analyzers.keys())

    def hasAnalyzer(self,name):
        """Is this LogLineAnalyzer name there"""
        return name in self.analyzers

    def getAnalyzer(self,name):
        """Get the LogLineAnalyzer name"""
        if name in self.analyzers:
            return self.analyzers[name]
        else:
            return None

    def addAnalyzer(self,name,obj):
        """Adds an analyzer

        obj - A LogLineAnalyzer
        name - the name of the analyzer"""

        obj.setParent(self)
        self.analyzers[name]=obj

    def analyzeLine(self,line):
        """Calls all the anlyzers for a line"""
        for nm in self.analyzers:
            self.analyzers[nm].doAnalysis(line)

    def analyze(self,fh):
        """Analyzes a file (one line at a time)

        fh - handle of the file"""
        while(self.line.read(fh)):
            self.analyzeLine(self.line.line)

    def goOn(self):
        """Checks with all the analyzers

        If one analyzer returns False it returns False"""
        result=True

        for nm in self.analyzers:
            #            print nm,self.analyzers[nm].goOn()
            result=result and self.analyzers[nm].goOn()

        return result

    def getTime(self):
        """Gets the current time"""
        return str(self.time)

    def setDirectory(self,d):
        """Sets the output directory for all the analyzers"""
        self.oDir=d
        for nm in self.analyzers:
            self.analyzers[nm].setDirectory(self.oDir)

    def getDirectory(self):
        """Gets the output directory"""
        return self.oDir

    def addTrigger(self,time,func,once=True,until=None):
        """Adds a trigger function that is to be called as soon as
        the simulation time exceeds a certain value
        :param time: the time at which the function should be triggered
        :param func: the trigger function
        :param once: Should this function be called once or at every time-step
        :param until: The time until which the trigger should be called"""

        data={}
        data["time"]=float(time)
        data["func"]=func
        if until!=None:
            data["until"]=float(until)
            once=False
        data["once"]=once

        self.timeTriggers.append(data)

    def checkTriggers(self):
        """Check for and execute the triggered functions"""

        remove=[]
        for i in range(len(self.timeTriggers)):
            t=self.timeTriggers[i]
            if t["time"]<=self.time:
                t["func"]()
                if t["once"]:
                    remove.append(i)
                elif "until" in t:
                    if t["until"]<=self.time:
                        remove.append(i)

        remove.reverse()

        for i in remove:
            self.timeTriggers.pop(i)

# Should work with Python3 and Python2
