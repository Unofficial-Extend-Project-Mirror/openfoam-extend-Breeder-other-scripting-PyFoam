#  ICE Revision: $Id$
"""Runner that outputs the residuals of the linear solver with Gnuplot"""

from .StepAnalyzedCommon import StepAnalyzedCommon
from .BasicRunner import BasicRunner
from .BasicWatcher import BasicWatcher

from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.LogAnalysis.SteadyConvergedLineAnalyzer import SteadyConvergedLineAnalyzer
from PyFoam.Basics.TimeLineCollection import TimeLineCollection
from PyFoam.Error import error

from os import path

class GnuplotCommon(StepAnalyzedCommon):
    """Class that collects the Gnuplotting-Stuff for two other classes"""
    def __init__(self,
                 fname,
                 smallestFreq=0.,
                 persist=None,
                 splitThres=2048,
                 plotLinear=True,
                 plotCont=True,
                 plotBound=True,
                 plotIterations=False,
                 plotCourant=False,
                 plotExecution=False,
                 plotDeltaT=False,
                 hardcopy=False,
                 hardcopyFormat="png",
                 hardcopyPrefix=None,
                 hardcopyTerminalOptions=None,
                 customRegexp=None,
                 writeFiles=False,
                 raiseit=False,
                 progress=False,
                 start=None,
                 end=None,
                 singleFile=False,
                 writePickled=True,
                 plottingImplementation=None,
                 gnuplotTerminal=None,
                 adaptFrequency=True):
        """
        TODO: Docu
        """
        StepAnalyzedCommon.__init__(self,
                                    fname,
                                    BoundingLogAnalyzer(doTimelines=True,
                                                        doFiles=writeFiles,
                                                        progress=progress,
                                                        singleFile=singleFile,
                                                        startTime=start,
                                                        endTime=end),
                                    writePickled=writePickled,
                                    smallestFreq=smallestFreq,
                                    adaptFrequency=adaptFrequency)

        self.startTime=start
        self.endTime=end

        self.plots={}
        self.createPlots(persist=persist,
                         raiseit=raiseit,
                         start=start,
                         end=end,
                         writeFiles=writeFiles,
                         splitThres=splitThres,
                         plotLinear=plotLinear,
                         plotCont=plotCont,
                         plotBound=plotBound,
                         plotIterations=plotIterations,
                         plotCourant=plotCourant,
                         plotExecution=plotExecution,
                         plotDeltaT=plotDeltaT,
                         customRegexp=customRegexp,
                         gnuplotTerminal=gnuplotTerminal,
                         plottingImplementation=plottingImplementation)

        self.hardcopy=hardcopy
        self.hardcopyFormat=hardcopyFormat
        self.hardcopyPrefix=hardcopyPrefix
        self.hardcopyTerminalOptions=hardcopyTerminalOptions

    def addPlots(self,plots):
        for k in plots:
            if k not in self.plots:
                self.plots[k]=plots[k]
            else:
                # key already there. Try to build an unique key
                newK=k
                while newK in self.plots:
                    newK+="_"
                self.plots[newK]=plots[k]

    def timeHandle(self):
        StepAnalyzedCommon.timeHandle(self)

        for p in self.plots:
            self.plots[p].redo()

    def stopHandle(self):
        StepAnalyzedCommon.stopHandle(self)
        self.timeHandle()
        if self.hardcopy:
            if self.hardcopyPrefix:
                prefix=self.hardcopyPrefix+"."
            else:
                prefix=""

            for p in self.plots:
                if not self.plots[p].hasData():
                    continue
                self.plots[p].doHardcopy(prefix+p,
                                         self.hardcopyFormat,
                                         self.hardcopyTerminalOptions)

class GnuplotRunner(GnuplotCommon,BasicRunner):
    def __init__(self,
                 argv=None,
                 smallestFreq=0.,
                 persist=None,
                 plotLinear=True,
                 plotCont=True,
                 plotBound=True,
                 plotIterations=False,
                 plotCourant=False,
                 plotExecution=False,
                 plotDeltaT=False,
                 customRegexp=None,
                 hardcopy=False,
                 hardcopyFormat="png",
                 hardcopyPrefix=None,
                 hardcopyTerminalOptions=None,
                 writeFiles=False,
                 server=False,
                 lam=None,
                 raiseit=False,
                 steady=False,
                 progress=False,
                 restart=False,
                 logname=None,
                 compressLog=False,
                 noLog=False,
                 logTail=None,
                 singleFile=False,
                 writePickled=True,
                 plottingImplementation=None,
                 gnuplotTerminal=None,
                 remark=None,
                 parameters=None,
                 jobId=None,
                 echoCommandLine=None):
        """:param smallestFreq: smallest Frequency of output
        :param persist: Gnuplot window persistst after run
        :param steady: Is it a steady run? Then stop it after convergence"""
        BasicRunner.__init__(self,
                             argv=argv,
                             silent=progress,
                             server=server,
                             lam=lam,
                             restart=restart,
                             logname=logname,
                             compressLog=compressLog,
                             noLog=noLog,
                             logTail=logTail,
                             remark=remark,
                             parameters=parameters,
                             echoCommandLine=echoCommandLine,
                             jobId=jobId)
        GnuplotCommon.__init__(self,
                               "Gnuplotting",
                               smallestFreq=smallestFreq,
                               persist=persist,
                               plotLinear=plotLinear,
                               plotCont=plotCont,
                               plotBound=plotBound,
                               plotIterations=plotIterations,
                               plotCourant=plotCourant,
                               plotExecution=plotExecution,
                               plotDeltaT=plotDeltaT,
                               customRegexp=customRegexp,
                               hardcopy=hardcopy,
                               hardcopyFormat=hardcopyFormat,
                               hardcopyPrefix=hardcopyPrefix,
                               hardcopyTerminalOptions=hardcopyTerminalOptions,
                               writeFiles=writeFiles,
                               raiseit=raiseit,
                               progress=progress,
                               singleFile=singleFile,
                               writePickled=writePickled,
                               gnuplotTerminal=gnuplotTerminal,
                               plottingImplementation=plottingImplementation)
        self.steady=steady
        if self.steady:
            self.steadyAnalyzer=SteadyConvergedLineAnalyzer()
            self.addAnalyzer("Convergence",self.steadyAnalyzer)

    def lineHandle(self,line):
        """Not to be called: Stops the solver"""
        GnuplotCommon.lineHandle(self,line)

        if self.steady:
            if not self.steadyAnalyzer.goOn():
                self.stopGracefully()

    def stopHandle(self):
        """Not to be called: Restores controlDict"""
        GnuplotCommon.stopHandle(self)
        BasicRunner.stopHandle(self)

class GnuplotWatcher(GnuplotCommon,BasicWatcher):
    def __init__(self,
                 logfile,
                 smallestFreq=0.,
                 persist=None,
                 silent=False,
                 tailLength=1000,
                 sleep=0.1,
                 replotFrequency=3600,
                 plotLinear=True,
                 plotCont=True,
                 plotBound=True,
                 plotIterations=False,
                 plotCourant=False,
                 plotExecution=False,
                 plotDeltaT=False,
                 customRegexp=None,
                 writeFiles=False,
                 hardcopy=False,
                 hardcopyFormat="png",
                 hardcopyPrefix=None,
                 hardcopyTerminalOptions=None,
                 raiseit=False,
                 progress=False,
                 start=None,
                 end=None,
                 singleFile=False,
                 writePickled=True,
                 gnuplotTerminal=None,
                 plottingImplementation=None,
                 solverNotRunning=False):
        """:param smallestFreq: smallest Frequency of output
        :param persist: Gnuplot window persistst after run"""
        BasicWatcher.__init__(self,
                              logfile,
                              silent=(silent or progress),
                              tailLength=tailLength,
                              sleep=sleep,
                              follow=not solverNotRunning)
        GnuplotCommon.__init__(self,
                               logfile,
                               smallestFreq=smallestFreq,
                               persist=persist,
                               plotLinear=plotLinear,
                               plotCont=plotCont,
                               plotBound=plotBound,
                               plotIterations=plotIterations,
                               plotCourant=plotCourant,
                               plotExecution=plotExecution,
                               plotDeltaT=plotDeltaT,
                               customRegexp=customRegexp,
                               hardcopy=hardcopy,
                               hardcopyFormat=hardcopyFormat,
                               hardcopyPrefix=hardcopyPrefix,
                               hardcopyTerminalOptions=hardcopyTerminalOptions,
                               writeFiles=writeFiles,
                               raiseit=raiseit,
                               progress=progress,
                               start=start,
                               end=end,
                               singleFile=singleFile,
                               writePickled=writePickled,
                               gnuplotTerminal=gnuplotTerminal,
                               plottingImplementation=plottingImplementation,
                               adaptFrequency=False)

        self.hasPlotted=False
        self.replotFrequency=replotFrequency

        if self.analyzer.hasAnalyzer("Time"):
            self.addChangeFileHook(self.analyzer.getAnalyzer("Time").reset)


    def startHandle(self):
        self.bakFreq=self.freq
        if self.endTime!=None:
            self.freq=1
        else:
            self.freq=self.replotFrequency

    def tailingHandle(self):
        self.freq=self.bakFreq
        self.oldtime=0

    def timeHandle(self):
        plotNow=True
        if not self.hasPlotted and self.endTime!=None:
            try:
                if float(self.getTime())>self.endTime:
                    self.hasPlotted=True
            except ValueError:
                pass
        elif self.hasPlotted:
            plotNow=False
        if plotNow:
            for p in self.plots:
                self.plots[p].redo()

# Should work with Python3 and Python2
