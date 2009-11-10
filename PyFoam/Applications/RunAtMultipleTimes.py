#  ICE Revision: $Id: RunAtMultipleTimes.py 10516 2009-06-29 09:19:38Z bgschaid $ 
"""
Application class that implements pyFoamRunAtMultipleTimes
"""

from PyFoamApplication import PyFoamApplication
from CommonSelectTimesteps import CommonSelectTimesteps
from CommonReportUsage import CommonReportUsage
from CommonStandardOutput import CommonStandardOutput
from CommonServer import CommonServer

from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

import sys
from os import path

class RunAtMultipleTimes(PyFoamApplication,
                         CommonReportUsage,
                         CommonSelectTimesteps,
                         CommonServer,
                         CommonStandardOutput):
    def __init__(self,args=None):
        description="""
        Runs a OpenFoam Utility that only supports being run for one or all times
        to be run at multiple selected times
        """
        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description)

    def addOptions(self):
        CommonStandardOutput.addOptions(self,logname="RunAtMultipleTimes")
        CommonServer.addOptions(self)
        CommonSelectTimesteps.addOptions(self,defaultUnique=True)
        CommonReportUsage.addOptions(self)
        
    def run(self):
        cName=self.parser.casePath()

        times=self.processTimestepOptions(SolutionDirectory(cName))
        if len(times)<1:
            self.warning("Can't continue without time-steps")
            return

        for i,t in enumerate(times):
            print " Running for t=",t
            run=UtilityRunner(argv=self.parser.getArgs()+["-time",t],
                              silent=self.opts.progress,
                              server=self.opts.server,
                              logname="%s.%s.t=%s" % (self.opts.logname,self.parser.getApplication(),t),
                              compressLog=self.opts.compress,
                              noLog=self.opts.noLog)

            self.addToCaseLog(cName,"Starting for t=%s",t)
            
            run.start()
            
            self.addToCaseLog(cName,"Ending")

            self.reportUsage(run)
            
