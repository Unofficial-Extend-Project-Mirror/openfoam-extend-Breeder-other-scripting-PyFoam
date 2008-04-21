#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/GnuplotRunner.py 2835 2008-02-29T12:45:45.007361Z bgschaid  $ 
"""Runner that outputs the residuals of the linear solver with Gnuplot"""

from StepAnalyzedCommon import StepAnalyzedCommon
from BasicRunner import BasicRunner
from BasicWatcher import BasicWatcher

from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.LogAnalysis.RegExpLineAnalyzer import RegExpLineAnalyzer
from PyFoam.LogAnalysis.SteadyConvergedLineAnalyzer import SteadyConvergedLineAnalyzer
from PyFoam.Basics.GnuplotTimelines import GnuplotTimelines
from PyFoam.Basics.TimeLineCollection import signedMax

from os import path

class GnuplotCommon(StepAnalyzedCommon):
    """Class that collects the Gnuplotting-Stuff for two other classes"""
    def __init__(self,fname,smallestFreq=0.,persist=None,splitThres=2048,plotLinear=True,plotCont=True,plotBound=True,plotIterations=False,plotCourant=False,plotExecution=False,plotDeltaT=False,customRegexp=None,writeFiles=False,raiseit=False,progress=False,start=None,end=None):
        """
        TODO: Docu
        """
        StepAnalyzedCommon.__init__(self,fname,BoundingLogAnalyzer(doTimelines=True,doFiles=writeFiles,progress=progress),smallestFreq=smallestFreq)

        self.plot=None
        self.plotCont=None
        self.plotBound=None
        self.plotIter=None
        self.plotCourant=None
        self.plotExecution=None
        self.plotCustom=None
        self.plotDeltaT=None
        
        if plotLinear:
            self.plot=GnuplotTimelines(self.getAnalyzer("Linear").lines,persist=persist,raiseit=raiseit,forbidden=["final","iterations"],start=start,end=end,logscale=True)
            self.getAnalyzer("Linear").lines.setSplitting(splitThres=splitThres,splitFun=max)
        
            self.plot.title("Residuals")

        if plotCont:
            self.plotCont=GnuplotTimelines(self.getAnalyzer("Continuity").lines,persist=persist,alternateAxis=["Global"],raiseit=raiseit,start=start,end=end)
            self.plotCont.set_string("ylabel \"Cumulative\"")
            self.plotCont.set_string("y2label \"Global\"")
            self.getAnalyzer("Continuity").lines.setSplitting(splitThres=splitThres)

            self.plotCont.title("Continuity")
 
        if plotBound:
            self.plotBound=GnuplotTimelines(self.getAnalyzer("Bounding").lines,persist=persist,raiseit=raiseit,start=start,end=end)
            self.getAnalyzer("Bounding").lines.setSplitting(splitThres=splitThres,splitFun=signedMax)
            self.plotBound.title("Bounded variables")

        if plotIterations:
            self.plotIter=GnuplotTimelines(self.getAnalyzer("Iterations").lines,persist=persist,with="steps",raiseit=raiseit,start=start,end=end)
            self.getAnalyzer("Iterations").lines.setSplitting(splitThres=splitThres)

            self.plotIter.title("Iterations")

        if plotCourant:
            self.plotCourant=GnuplotTimelines(self.getAnalyzer("Courant").lines,persist=persist,raiseit=raiseit,start=start,end=end)
            self.getAnalyzer("Courant").lines.setSplitting(splitThres=splitThres)

            self.plotCourant.title("Courant")
 
        if plotDeltaT:
            self.plotDeltaT=GnuplotTimelines(self.getAnalyzer("DeltaT").lines,persist=persist,raiseit=raiseit,start=start,end=end,logscale=True)
            self.getAnalyzer("DeltaT").lines.setSplitting(splitThres=splitThres)

            self.plotDeltaT.title("DeltaT")
 
        if plotExecution:
            self.plotExecution=GnuplotTimelines(self.getAnalyzer("Execution").lines,persist=persist,with="steps",raiseit=raiseit,start=start,end=end)
            self.getAnalyzer("Execution").lines.setSplitting(splitThres=splitThres)

            self.plotExecution.title("Execution Time")

        if customRegexp:
            self.plotCustom=[]
            for i in range(len(customRegexp)):
                name="Custom%02d" % i
                expr=customRegexp[i]
                titles=[]
                theTitle="Custom %d" % i
                if expr[0]=="{":
                    data=eval(expr)
                    expr=data["expr"]
                    if "name" in data:
                        name+="_"+data["name"]
                        name=name.replace(" ","_").replace(path.sep,"Slash")
                        theTitle+=" - "+data["name"]
                    if "titles" in data:
                        titles=data["titles"]
                self.addAnalyzer(name,RegExpLineAnalyzer(name.lower(),expr,titles=titles,doTimelines=True,doFiles=writeFiles))
                plotCustom=GnuplotTimelines(self.getAnalyzer(name).lines,persist=persist,with="lines",raiseit=raiseit,start=start,end=end)
                plotCustom.title(theTitle)
                self.plotCustom.append(plotCustom)
                
            self.reset()
           
    def timeHandle(self):
        if self.plot:
            self.plot.redo()
        if self.plotCont:
            self.plotCont.redo()
        if self.plotBound:
            self.plotBound.redo()
        if self.plotIter:
            self.plotIter.redo()
        if self.plotCourant:
            self.plotCourant.redo()
        if self.plotExecution:
            self.plotExecution.redo()
        if self.plotDeltaT:
            self.plotDeltaT.redo()
        if self.plotCustom:
            for r in self.plotCustom:
                r.redo()

    def stopHandle(self):
        self.timeHandle()
        
        
class GnuplotRunner(GnuplotCommon,BasicRunner):
    def __init__(self,argv=None,smallestFreq=0.,persist=None,plotLinear=True,plotCont=True,plotBound=True,plotIterations=False,plotCourant=False,plotExecution=False,plotDeltaT=False,customRegexp=None,writeFiles=False,server=False,lam=None,raiseit=False,steady=False,progress=False,restart=False):
        """@param smallestFreq: smallest Frequency of output
        @param persist: Gnuplot window persistst after run
        @param steady: Is it a steady run? Then stop it after convergence"""
        BasicRunner.__init__(self,argv=argv,silent=progress,server=server,lam=lam,restart=restart)
        GnuplotCommon.__init__(self,"Gnuplotting",smallestFreq=smallestFreq,persist=persist,plotLinear=plotLinear,plotCont=plotCont,plotBound=plotBound,plotIterations=plotIterations,plotCourant=plotCourant,plotExecution=plotExecution,plotDeltaT=plotDeltaT,customRegexp=customRegexp,writeFiles=writeFiles,raiseit=raiseit,progress=progress)
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
    def __init__(self,logfile,smallestFreq=0.,persist=None,silent=False,tailLength=1000,sleep=0.1,plotLinear=True,plotCont=True,plotBound=True,plotIterations=False,plotCourant=False,plotExecution=False,plotDeltaT=False,customRegexp=None,writeFiles=False,raiseit=False,progress=False,start=None,end=None):
        """@param smallestFreq: smallest Frequency of output
        @param persist: Gnuplot window persistst after run"""
        BasicWatcher.__init__(self,logfile,silent=(silent or progress),tailLength=tailLength,sleep=sleep)
        GnuplotCommon.__init__(self,logfile,smallestFreq=smallestFreq,persist=persist,plotLinear=plotLinear,plotCont=plotCont,plotBound=plotBound,plotIterations=plotIterations,plotCourant=plotCourant,plotExecution=plotExecution,plotDeltaT=plotDeltaT,customRegexp=customRegexp,writeFiles=writeFiles,raiseit=raiseit,progress=progress,start=start,end=end)

    def startHandle(self):
        self.bakFreq=self.freq
        self.freq=3600
        
    def tailingHandle(self):
        self.freq=self.bakFreq
        self.oldtime=0
        
        
