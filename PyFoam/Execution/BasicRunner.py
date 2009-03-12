#  ICE Revision: $Id: BasicRunner.py 9667 2008-11-12 18:20:16Z bgschaid $ 
"""Run a OpenFOAM command"""

import sys
import string
from os import path
from threading import Timer

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
from PyFoam.Error import warning,error
from PyFoam import configuration as config

def restoreControlDict(ctrl):
    """Timed function to avoid time-stamp-problems"""
    warning("Restoring the controlDict")
    ctrl.restore()
    
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
                 lam=None,
                 server=False,
                 restart=False,
                 noLog=False):
        """@param argv: list with the tokens that are the command line
        if not set the standard command line is used
        @param silent: if True no output is sent to stdout
        @param logname: name of the logfile
        @param lam: Information about a parallel run
        @param server: Whether or not to start the network-server
        @type lam: PyFoam.Execution.ParallelExecution.LAMMachine
        @param noLog: Don't output a log file"""

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
        
        if self.lam!=None:
            self.argv=lam.buildMPIrun(self.argv)
        self.cmd=string.join(self.argv," ")
        foamLogger().info("Starting: "+self.cmd+" in "+path.abspath(path.curdir))
        self.logFile=path.join(self.dir,logname+".logfile")
        self.noLog=noLog
        
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

        self.stopMe=False
        self.writeRequested=False

        self.endTriggers=[]
        
    def start(self):
        """starts the command and stays with it till the end"""
        
        self.started=True
        if not self.noLog:
            fh=open(self.logFile,"w")

        self.startHandle()

        check=BasicRunnerCheck()
        
        self.run.start()

        while self.run.check():
            try:
                self.run.read()
                if not self.run.check():
                    break

                line=self.run.getLine()

                tmp=check.getTime(line)
                if check.controlDictRead(line):
                    if self.writeRequested:
                        warning("Preparing to reset controlDict to old glory")
                        Timer(config().getfloat("Execution","controlDictRestoreWait",default=30.),
                              restoreControlDict,
                              args=[self.controlDict]).start()
                        self.writeRequested=False
                        
                if tmp!=None:
                    self.nowTime=tmp
                    if self.createTime==None:
                        # necessary because interFoam reports no creation time
                        self.createTime=tmp
                        
                tmp=check.getCreateTime(line)
                if tmp!=None:
                    self.createTime=tmp
                    
                if not self.silent:
                    print line
                    
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

        self.stopHandle()

        for t in self.endTriggers:
            t()

        if not self.noLog:        
            fh.close()
        
        if self.server!=None:
            self.server.deregister()
            self.server.kill()
            
        foamLogger().info("Finished")

    def runOK(self):
        """checks whether the run was successful"""
        if self.started:
            return not self.fatalError and not self.fatalFPE and not self.fatalStackdump
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
                self.controlDict=ParameterFile(path.join(self.dir,"system","controlDict"),backup=True)
            self.controlDict.replaceParameter("stopAt","writeNow")
            warning("Stopping run at next write")

    def writeResults(self):
        """Writes the next possible time-step"""
        #        warning("writeResult is not yet implemented")
        if not self.writeRequested:
            if not self.isRestarted:
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

        return SolutionDirectory(self.dir,archive=archive)

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
        if line.find("Reading object controlDict from file"):
            return True
        else:
            return False
        
