#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/BasicRunner.py 7361 2011-03-17T09:41:49.879693Z bgschaid  $ 
"""Run a OpenFOAM command"""

import sys
import string
import gzip
from os import path
from threading import Timer
from time import time,asctime

from PyFoam.FoamInformation import oldAppConvention as oldApp

if not 'curdir' in dir(path) or not 'sep' in dir(path):
    print "Warning: Inserting symbols into os.path (Python-Version<2.3)"
    path.curdir='.'
    path.sep   ='/'
    
from FoamThread import FoamThread
from PyFoam.Infrastructure.FoamServer import FoamServer
from PyFoam.Infrastructure.Logging import foamLogger
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParameterFile import ParameterFile
from PyFoam.Error import warning,error,debug
from PyFoam import configuration as config

def restoreControlDict(ctrl,runner):
    """Timed function to avoid time-stamp-problems"""
    warning("Restoring the controlDict")
    ctrl.restore()
    runner.controlDict=None
    
class BasicRunner(object):
    """Base class for the running of commands

    When the command is run the output is copied to a LogFile and
    (optionally) standard-out

    The argument list assumes for the first three elements the
    OpenFOAM-convention:

    <cmd> <dir> <case>

    The directory name for outputs is therefor created from <dir> and
    <case>
    
    Provides some handle-methods that are to be overloaded for
    additional functionality"""
    
    def __init__(self,
                 argv=None,
                 silent=False,
                 logname=None,
                 compressLog=False,
                 lam=None,
                 server=False,
                 restart=False,
                 noLog=False,
                 remark=None,
                 jobId=None,
                 writeState=True):
        """@param argv: list with the tokens that are the command line
        if not set the standard command line is used
        @param silent: if True no output is sent to stdout
        @param logname: name of the logfile
        @param compressLog: Compress the logfile into a gzip
        @param lam: Information about a parallel run
        @param server: Whether or not to start the network-server
        @type lam: PyFoam.Execution.ParallelExecution.LAMMachine
        @param noLog: Don't output a log file
        @param remark: User defined remark about the job
        @param jobId: Job ID of the controlling system (Queueing system)
        @param writeState: Write the state to some files in the case"""

        if sys.version_info < (2,3):
            # Python 2.2 does not have the capabilities for the Server-Thread
            if server:
                warning("Can not start server-process because Python-Version is too old")
            server=False

        if argv==None:
            self.argv=sys.argv[1:]
        else:
            self.argv=argv

        if oldApp():
            self.dir=path.join(self.argv[1],self.argv[2])
            if self.argv[2][-1]==path.sep:
                self.argv[2]=self.argv[2][:-1]
        else:
            self.dir=path.curdir
            if "-case" in self.argv:
                self.dir=self.argv[self.argv.index("-case")+1]
                
        if logname==None:
            logname="PyFoam."+path.basename(argv[0])
            
        try:
            sol=self.getSolutionDirectory()
        except OSError,e:
            error("Solution directory",self.dir,"does not exist. No use running. Problem:",e)
            
        self.silent=silent
        self.lam=lam
        self.origArgv=self.argv
        self.writeState=writeState
        self.__lastLastSeenWrite=0
        self.__lastNowTimeWrite=0
        
        if self.lam!=None:
            self.argv=lam.buildMPIrun(self.argv)
            if config().getdebug("ParallelExecution"):
                debug("Command line:",string.join(self.argv))
        self.cmd=string.join(self.argv," ")
        foamLogger().info("Starting: "+self.cmd+" in "+path.abspath(path.curdir))
        self.logFile=path.join(self.dir,logname+".logfile")
        self.noLog=noLog
        self.compressLog=compressLog
        if self.compressLog:
            self.logFile+=".gz"
            
        self.fatalError=False
        self.fatalFPE=False
        self.fatalStackdump=False
        
        self.warnings=0
        self.started=False

        self.isRestarted=False
        if restart:
            self.controlDict=ParameterFile(path.join(self.dir,"system","controlDict"),backup=True)
            self.controlDict.replaceParameter("startFrom","latestTime")
            self.isRestarted=True
        else:
            self.controlDict=None
            
        self.run=FoamThread(self.cmd,self)

        self.server=None
        if server:
            self.server=FoamServer(run=self.run,master=self)
            self.server.setDaemon(True)
            self.server.start()
            try:
                IP,PID,Port=self.server.info()
                f=open(path.join(self.dir,"PyFoamServer.info"),"w")
                print >>f,IP,PID,Port
                f.close()
            except AttributeError:
                warning("There seems to be a problem with starting the server:",self.server,"with attributes",dir(self.server))
                self.server=None
                
        self.createTime=None
        self.nowTime=None
        self.startTimestamp=time()

        self.stopMe=False
        self.writeRequested=False

        self.endTriggers=[]

        self.lastLogLineSeen=None
        self.lastTimeStepSeen=None

        self.remark=remark
        self.jobId=jobId
        
    def start(self):
        """starts the command and stays with it till the end"""
        
        self.started=True
        if not self.noLog:
            if self.compressLog:
                fh=gzip.open(self.logFile,"w")
            else:
                fh=open(self.logFile,"w")

        self.startHandle()

        self.writeStartTime()
        self.writeTheState("Running")
        
        check=BasicRunnerCheck()
        
        self.run.start()
        interrupted=False
        
        while self.run.check():
            try:
                self.run.read()
                if not self.run.check():
                    break

                line=self.run.getLine()
                self.lastLogLineSeen=time()
                self.writeLastSeen()

                tmp=check.getTime(line)
                if check.controlDictRead(line):
                    if self.writeRequested:
                        warning("Preparing to reset controlDict to old glory")
                        Timer(config().getfloat("Execution","controlDictRestoreWait",default=30.),
                              restoreControlDict,
                              args=[self.controlDict,self]).start()
                        self.writeRequested=False
                        
                if tmp!=None:
                    self.nowTime=tmp
                    self.writeTheState("Running",always=False)
                    self.writeNowTime()
                    self.lastTimeStepSeen=time()
                    if self.createTime==None:
                        # necessary because interFoam reports no creation time
                        self.createTime=tmp
                        
                tmp=check.getCreateTime(line)
                if tmp!=None:
                    self.createTime=tmp
                    
                if not self.silent:
                    try:
                        print line
                    except IOError,e:
                        if e.errno!=32:
                            raise e
                        else:
                            # Pipe was broken
                            self.run.interrupt()
                            
                if line.find("FOAM FATAL ERROR")>=0 or line.find("FOAM FATAL IO ERROR")>=0:
                    self.fatalError=True
                if line.find("Foam::sigFpe::sigFpeHandler")>=0:
                    self.fatalFPE=True
                if line.find("Foam::error::printStack")>=0:
                    self.fatalStackdump=True
                    
                if self.fatalError and line!="":
                    foamLogger().error(line)

                if line.find("FOAM Warning")>=0:
                    self.warnings+=1

                if self.server!=None:
                    self.server._insertLine(line)
                
                self.lineHandle(line)

                if not self.noLog:
                    fh.write(line+"\n")
                    fh.flush()
                    
            except KeyboardInterrupt,e:
                foamLogger().warning("Keyboard Interrupt")
                self.run.interrupt()
                self.writeTheState("Interrupted")
                interrupted=True
                
        self.writeNowTime(force=True)
       
        self.stopHandle()

        if not interrupted:
            self.writeTheState("Finished")
            
        for t in self.endTriggers:
            t()

        if not self.noLog:        
            fh.close()
        
        if self.server!=None:
            self.server.deregister()
            self.server.kill()
            
        foamLogger().info("Finished")

    def writeToStateFile(self,fName,message):
        """Write a message to a state file"""
        if self.writeState:
            open(path.join(self.dir,"PyFoamState."+fName),"w").write(message+"\n")
        
    def writeStartTime(self):
        """Write the real time the run was started at"""
        self.writeToStateFile("StartedAt",asctime())

    def writeTheState(self,state,always=True):
        """Write the current state the run is in"""
        if always or (time()-self.__lastLastSeenWrite)>9:
            self.writeToStateFile("TheState",state)
        
    def writeLastSeen(self):
        if (time()-self.__lastLastSeenWrite)>10:
            self.writeToStateFile("LastOutputSeen",asctime())
            self.__lastLastSeenWrite=time()

    def writeNowTime(self,force=False):
        if (time()-self.__lastNowTimeWrite)>10 or force:
            self.writeToStateFile("CurrentTime",str(self.nowTime))
            self.__lastNowTimeWrite=time()
    
    def runOK(self):
        """checks whether the run was successful"""
        if self.started:
            return not self.fatalError and not self.fatalFPE and not self.fatalStackdump # and self.run.getReturnCode()==0
        else:
            return False
        
    def startHandle(self):
        """to be called before the program is started"""
        pass

    def stopGracefully(self):
        """Tells the runner to stop at the next convenient time"""
        if not self.stopMe:
            self.stopMe=True
            if not self.isRestarted:
                if self.controlDict:
                    warning("The controlDict has already been modified. Restoring will be problementic")
                self.controlDict=ParameterFile(path.join(self.dir,"system","controlDict"),backup=True)
            self.controlDict.replaceParameter("stopAt","writeNow")
            warning("Stopping run at next write")

    def writeResults(self):
        """Writes the next possible time-step"""
        #        warning("writeResult is not yet implemented")
        if not self.writeRequested:
            if not self.isRestarted:
                if self.controlDict:
                    warning("The controlDict has already been modified. Restoring will be problementic")
                self.controlDict=ParameterFile(path.join(self.dir,"system","controlDict"),backup=True)
            self.controlDict.replaceParameter("writeControl","timeStep")
            self.controlDict.replaceParameter("writeInterval","1")
            self.writeRequested=True
            
    def stopHandle(self):
        """called after the program has stopped"""
        if self.stopMe or self.isRestarted:
            self.controlDict.restore()
    
    def lineHandle(self,line):
        """called every time a new line is read"""
        pass
    
    def logName(self):
        """Get the name of the logfiles"""
        return self.logFile

    def getSolutionDirectory(self,archive=None):
        """@return: The directory of the case
        @rtype: PyFoam.RunDictionary.SolutionDirectory
        @param archive: Name of the directory for archiving results"""

        return SolutionDirectory(self.dir,archive=archive,parallel=True)

    def addEndTrigger(self,f):
        """@param f: A function that is to be executed at the end of the simulation"""
        self.endTriggers.append(f)
        
import re

class BasicRunnerCheck(object):
    """A small class that does primitve checking for BasicRunner
    Duplicates other efforts, but ...."""

    floatRegExp="[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"

    def __init__(self):
        self.timeExpr=re.compile("^Time = (%f%)$".replace("%f%",self.floatRegExp))
        self.createExpr=re.compile("^Create mesh for time = (%f%)$".replace("%f%",self.floatRegExp))
        
    def getTime(self,line):
        """Does this line contain time information?"""
        m=self.timeExpr.match(line)
        if m:
            return float(m.group(1))
        else:
            return None
        
    def getCreateTime(self,line):
        """Does this line contain mesh time information?"""
        m=self.createExpr.match(line)
        if m:
            return float(m.group(1))
        else:
            return None
        
    def controlDictRead(self,line):
        """Was the controlDict reread?"""
        if line.find("Reading object controlDict from file")>=0:
            return True
        else:
            return False
        
