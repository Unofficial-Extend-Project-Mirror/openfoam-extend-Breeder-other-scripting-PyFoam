#  ICE Revision: $Id$
"""Common stuff for classes that use analyzers"""

from os import path,mkdir
from shutil import move,rmtree

from PyFoam.Basics.PlotTimelinesFactory import createPlotTimelines,createPlotTimelinesDirect
from PyFoam.Basics.TimeLineCollection import signedMax
from PyFoam.LogAnalysis.RegExpLineAnalyzer import RegExpLineAnalyzer
from PyFoam.LogAnalysis.PhaseChangerLineAnalyzer import PhaseChangerLineAnalyzer

from PyFoam.Error import error

# import pickle
from PyFoam.ThirdParty.six.moves import cPickle as pickle

from PyFoam.Basics.GeneralPlotTimelines import allPlots
from PyFoam.Basics.TimeLineCollection import allLines

from threading import Lock

class AnalyzedCommon(object):
    """This class collects information and methods that are needed for
    handling analyzers"""

    def __init__(self,
                 filename,
                 analyzer,
                 doPickling=True):
        """@param filename: name of the file that is being analyzed
        @param analyzer: the analyzer itself
        @param doPickling: write the pickled plot data"""

        self.analyzer=analyzer

        if 'dir' in dir(self):
            self.logDir=path.join(self.dir,filename+".analyzed")
        else:
            self.logDir=filename+".analyzed"

        if path.exists(self.logDir):
            # Clean away
            rmtree(self.logDir,ignore_errors=True)
        mkdir(self.logDir)

        self.doPickling=doPickling
        if self.doPickling:
            self.pickleLock=Lock()

        self.reset()

        if hasattr(self,"data"):
            pickleFile=path.join(self.logDir,"pickledStartData")
            pick=pickle.Pickler(open(pickleFile,"wb"))
            pick.dump(self.data)

    def tearDown(self):
        self.analyzer.tearDown()
        if hasattr(self,"data"):
            pickleFile=path.join(self.logDir,"pickledData")
            pick=pickle.Pickler(open(pickleFile,"wb"))
            pick.dump(self.data)

    def listAnalyzers(self):
        """@returns: A list with the names of the analyzers"""
        return self.analyzer.listAnalyzers()

    def getAnalyzer(self,name):
        """@param name: name of the LineAnalyzer to get"""
        return self.analyzer.getAnalyzer(name)

    def hasAnalyzer(self,name):
        """@param name: name of the LineAnalyzer we ask for"""
        return self.analyzer.hasAnalyzer(name)

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

    def createPlots(self,
                    persist=None,
                    raiseit=False,
                    splitThres=2048,
                    plotLinear=True,
                    plotCont=True,
                    plotBound=True,
                    plotIterations=True,
                    plotCourant=True,
                    plotExecution=True,
                    plotDeltaT=True,
                    start=None,
                    end=None,
                    writeFiles=False,
                    customRegexp=None,
                    plottingImplementation="dummy"):

        plots={}

        if plotLinear and self.hasAnalyzer("Linear"):
            plots["linear"]=createPlotTimelinesDirect("linear",
                                                      self.getAnalyzer("Linear").lines,
                                                      persist=persist,
                                                      raiseit=raiseit,
                                                      forbidden=["final","iterations"],
                                                      start=start,
                                                      end=end,
                                                      logscale=True,
                                                      implementation=plottingImplementation)
            self.getAnalyzer("Linear").lines.setSplitting(splitThres=splitThres,
                                                          splitFun=max,
                                                          advancedSplit=True)

            plots["linear"].setTitle("Residuals")
            plots["linear"].setYLabel("Initial residual")

        if plotCont and self.hasAnalyzer("Continuity"):
            plots["cont"]=createPlotTimelinesDirect("continuity",
                                                    self.getAnalyzer("Continuity").lines,
                                                    persist=persist,
                                                    alternateAxis=["Global"],
                                                    raiseit=raiseit,
                                                    start=start,
                                                    end=end,
                                                    implementation=plottingImplementation)
            plots["cont"].setYLabel("Cumulative")
            plots["cont"].setYLabel2("Global")
            self.getAnalyzer("Continuity").lines.setSplitting(splitThres=splitThres,
                                                              advancedSplit=True)

            plots["cont"].setTitle("Continuity")

        if plotBound and self.hasAnalyzer("Bounding"):
            plots["bound"]=createPlotTimelinesDirect("bounding",
                                                     self.getAnalyzer("Bounding").lines,
                                                     persist=persist,
                                                     raiseit=raiseit,
                                                     start=start,
                                                     end=end,
                                                     implementation=plottingImplementation)
            self.getAnalyzer("Bounding").lines.setSplitting(splitThres=splitThres,
                                                            splitFun=signedMax,
                                                            advancedSplit=True)
            plots["bound"].setTitle("Bounded variables")

        if plotIterations and self.hasAnalyzer("Iterations"):
            plots["iter"]=createPlotTimelinesDirect("iterations",
                                                    self.getAnalyzer("Iterations").lines,
                                                    persist=persist,
                                                    with_="steps",
                                                    raiseit=raiseit,
                                                    start=start,
                                                    end=end,
                                                    implementation=plottingImplementation)
            self.getAnalyzer("Iterations").lines.setSplitting(splitThres=splitThres,
                                                              advancedSplit=True)

            plots["iter"].setTitle("Iterations")
            plots["iter"].setYLabel("Sum of iterations")

        if plotCourant and self.hasAnalyzer("Courant"):
            plots["courant"]=createPlotTimelinesDirect("courant",
                                                       self.getAnalyzer("Courant").lines,
                                                       persist=persist,
                                                       raiseit=raiseit,
                                                       start=start,
                                                       end=end,
                                                       implementation=plottingImplementation)
            self.getAnalyzer("Courant").lines.setSplitting(splitThres=splitThres,
                                                           advancedSplit=True)

            plots["courant"].setTitle("Courant")
            plots["courant"].setYLabel("Courant Number [1]")

        if plotDeltaT and self.hasAnalyzer("DeltaT"):
            plots["deltaT"]=createPlotTimelinesDirect("timestep",
                                                      self.getAnalyzer("DeltaT").lines,
                                                      persist=persist,
                                                      raiseit=raiseit,
                                                      start=start,
                                                      end=end,
                                                      logscale=True,
                                                      implementation=plottingImplementation)
            self.getAnalyzer("DeltaT").lines.setSplitting(splitThres=splitThres,
                                                          advancedSplit=True)

            plots["deltaT"].setTitle("DeltaT")
            plots["deltaT"].setYLabel("dt [s]")

        if plotExecution and self.hasAnalyzer("Execution"):
            plots["execution"]=createPlotTimelinesDirect("execution",
                                                         self.getAnalyzer("Execution").lines,
                                                         persist=persist,
                                                         with_="steps",
                                                         raiseit=raiseit,
                                                         start=start,
                                                         end=end,
                                                         implementation=plottingImplementation)
            self.getAnalyzer("Execution").lines.setSplitting(splitThres=splitThres,
                                                             advancedSplit=True)

            plots["execution"].setTitle("Execution Time")
            plots["execution"].setYLabel("Time [s]")

        if customRegexp:
            self.plotCustom=[]
            masters={}
            slaves=[]
            for i,custom in enumerate(customRegexp):
                if not custom.enabled:
                    continue

                if persist!=None:
                    custom.persist=persist
                if start!=None:
                    custom.start=start
                if end!=None:
                    custom.end=end
                custom.raiseit=raiseit

                createPlot=True
                if custom.type=="phase":
                    self.addAnalyzer(custom.name,
                                     PhaseChangerLineAnalyzer(custom.expr,
                                                              idNr=custom.idNr))
                    createPlot=False
                elif custom.type in ["dynamic","dynamicslave"]:
                    self.addAnalyzer(custom.name,
                                     RegExpLineAnalyzer(custom.name.lower(),
                                                        custom.expr,
                                                        titles=custom.titles,
                                                        doTimelines=True,
                                                        doFiles=writeFiles,
                                                        accumulation=custom.accumulation,
                                                        progressTemplate=custom.progress,
                                                        singleFile=True,
                                                        idNr=custom.idNr,
                                                        startTime=custom.start,
                                                        endTime=custom.end))

                elif custom.type in ["regular","slave"]:
                    self.addAnalyzer(custom.name,
                                     RegExpLineAnalyzer(custom.name.lower(),
                                                        custom.expr,
                                                        titles=custom.titles,
                                                        doTimelines=True,
                                                        doFiles=writeFiles,
                                                        accumulation=custom.accumulation,
                                                        progressTemplate=custom.progress,
                                                        singleFile=True,
                                                        startTime=custom.start,
                                                        endTime=custom.end))
                else:
                    error("Unknown type",custom.type,"in custom expression",custom.name)

                if createPlot:
                    if custom.master==None:
                        if custom.type in ["slave","dynamicslave"]:
                            error("Custom expression",custom.name,"is supposed to be a 'slave' but no master is defined")
                        masters[custom.id]=custom
                        plotCustom=createPlotTimelines(self.getAnalyzer(custom.name).lines,
                                                       custom=custom,
                                                       implementation=plottingImplementation)
                        self.getAnalyzer(custom.name).lines.setSplitting(splitThres=splitThres,
                                                                     advancedSplit=True)
                        plotCustom.setTitle(custom.theTitle)
                        plots["custom%04d" % i]=plotCustom
                    else:
                        if custom.type not in ["slave","dynamicslave"]:
                            error("'master' only makes sense if type is 'slave' or 'dynamicslave' for",custom.name)
                        if getattr(custom,"alternateAxis",None):
                            error("Specify alternate values in 'alternateAxis' of master",
                                  custom.master,"for",custom.name)
                        slaves.append(custom)

            for s in slaves:
                if s.master not in masters:
                    error("The custom plot",s.id,"wants the master plot",
                          s.master,"but it is not found in the list of masters",
                          list(masters.keys()))
                else:
                    slave=self.getAnalyzer(s.name)
                    master=self.getAnalyzer(masters[s.master].name)
                    slave.setMaster(master)

            self.reset()

        return plots

    def picklePlots(self,wait=False):
        """Writes the necessary information for the plots permanently to disc,
        so that it doesn't have to be generated again
        @param wait: wait for the lock to be allowed to pickle"""

        #        print "Putting some pickles in the jar"

        lines=allLines()
        plots=allPlots()
        if lines and plots:
            gotIt=self.pickleLock.acquire(wait)
            if not gotIt:
                return

            pickleFile=path.join(self.logDir,"pickledPlots")
            pick=pickle.Pickler(open(pickleFile+".tmp","wb"))
            pick.dump(lines.prepareForTransfer())
            pick.dump(plots.prepareForTransfer())
            move(pickleFile+".tmp",pickleFile)

            if hasattr(self,"data"):
                pickleFile=path.join(self.logDir,"pickledUnfinishedData")
                pick=pickle.Pickler(open(pickleFile+".tmp","wb"))
                pick.dump(self.data)
                del pick
                move(pickleFile+".tmp",pickleFile)

            self.pickleLock.release()

    def setDataSet(self,data):
        if hasattr(self,"data"):
            self.data["analyzed"]=data

# Should work with Python3 and Python2
