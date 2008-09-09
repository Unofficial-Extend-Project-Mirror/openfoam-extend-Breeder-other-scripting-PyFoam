#  ICE Revision: $Id: FoamServer.py 7964 2007-09-20 08:33:20Z bgschaid $ 
"""A XMLRPC-Server that answeres about the current state of a Foam-Run"""

from ServerBase import ServerBase

from xmlrpclib import ServerProxy

from PyFoam import configuration as config
from PyFoam import versionString
from PyFoam.Basics.RingBuffer import RingBuffer
from PyFoam.Infrastructure.NetworkHelpers import freeServerPort
from PyFoam.Infrastructure.Logging import foamLogger
from PyFoam.FoamInformation import foamMPI
from PyFoam.RunDictionary.ParameterFile import ParameterFile

from Hardcoded import userName

from threading import Lock,Thread,Timer
from time import time
from os import environ,uname,path,getpid
import socket

import sys,string
from traceback import extract_tb

def findFreePort():
    """Finds a free server port on this machine and returns it

    Valid server ports are in the range 18000 upward (the function tries to 
    find the lowest possible port number

    ATTENTION: this part may introduce race conditions"""
    
    return freeServerPort(config().getint("Network","startServerPort"),
                          length=config().getint("Network","nrServerPorts"))

class FoamAnswerer(object):
    """The class that handles the actual requests (only needed to hide the
    Thread-methods from the world
    """
    def __init__(self,run=None,master=None,lines=100):
        """
        @param run: The thread that controls the run
        @param master: The Runner-Object that controls everything
	@param lines: the number of lines the server should remember
        """
        self._run=run
        self._master=master
	self._lines=RingBuffer(nr=lines)
        self._lastTime=time()
	self._linesLock=Lock()
        self._maxOutputTime=config().getfloat("IsAlive","maxTimeStart")
        
    def _insertLine(self,line):
	"""Inserts a new line, not to be called via XMLRPC"""
	self._linesLock.acquire()
	self._lines.insert(line)
        tmp=time()
        if (tmp-self._lastTime)>self._maxOutputTime:
            self._maxOutputTime=tmp-self._lastTime
        self._lastTime=tmp
	self._linesLock.release()

    def isFoamServer(self):
        """This is a Foam-Server (True by default)"""
        return True

    def isLiving(self):
        """The calculation still generates output and therefor seems to be living"""
        return self.elapsedTime()<self._maxOutputTime

    def _kill(self):
        """Interrupts the FOAM-process"""
        if self._run:
            foamLogger().warning("Killed by request")
            self._run.interrupt()
            return True
        else:
            return False

    def stop(self):
        """Stops the run gracefully (after writing the last time-step to disk)"""
        self._master.stopGracefully()
        return True
    
    def write(self):
        """Makes the program write the next time-step to disk and the continue"""
        self._master.writeResults()
        return True
    
    def argv(self):
        """Argument vector with which the runner was called"""
        if self._master:
            return self._master.origArgv
        else:
            return []
        
    def usedArgv(self):
        """Argument vector with which the runner started the run"""
        if self._master:
            return self._master.argv
        else:
            return []
        
    def isParallel(self):
        """Is it a parallel run?"""
        if self._master:
            return self._master.lam!=None
        else:
            return False
        
    def procNr(self):
        """How many processors are used?"""
        if self._master:
            if self._master.lam!=None:
                return self._master.lam.cpuNr()
            else:
                return 1
        else:
            return 0
        
    def nrWarnings(self):
        """Number of warnings the executable emitted"""
        if self._master:
            return self._master.warnings
        else:
            return 0

    def commandLine(self):
        """The command line"""
        if self._master:
            return string.join(self._master.origArgv)
        else:
            return ""

    def actualCommandLine(self):
        """The actual command line used"""
        if self._master:
            return self._master.cmd
        else:
            return ""

    def scriptName(self):
        """Name of the Python-Script that runs the show"""
        return sys.argv[0]
    
    def lastLine(self):
	"""@return: the last line that was output by the running FOAM-process"""
	self._linesLock.acquire()
	result=self._lines.last()
	self._linesLock.release()
        if not result:
            return ""
	return result

    def tail(self):
	"""@return: the current last lines as a string"""
	self._linesLock.acquire()
	tmp=self._lines.dump()
	self._linesLock.release()
        result=""
        for l in tmp:
            result+=l

        return result

    def elapsedTime(self):
        """@return: time in seconds since the last line was output"""
	self._linesLock.acquire()
	result=time()-self._lastTime
	self._linesLock.release()

        return result
    
    def getEnviron(self,name):
        """@param name: name of an environment variable
        @return: value of the variable, empty string if non-existing"""
        result=""
        if environ.has_key(name):
            result=environ[name]
        return result

    def mpi(self):
        """@return: name of the MPI-implementation"""
        return foamMPI()

    def foamVersion(self):
        """Version number of the Foam-Version"""
        return self.getEnviron("WM_PROJECT_VERSION")
    
    def pyFoamVersion(self):
        """@return: Version number of the PyFoam"""
        return versionString()

    def uname(self):
        """@return: the complete uname-information"""
        return uname()

    def ip(self):
        """@return: the ip of this machine"""
        return socket.gethostbyname(socket.gethostname())
    
    def hostname(self):
        """@return: The name of the computer"""
        return uname()[1]

    def configuration(self):
        """@return: all the configured parameters"""
        return config().dump()

    def cwd(self):
        """@return: the current working directory"""
        return path.abspath(path.curdir)

    def pid(self):
        """@return: the PID of the script"""
        return getpid()
    
    def user(self):
        """@return: the user that runs this script"""
        return userName()

    def id(self):
        """@return: an ID for this run: IP and process-id"""
        return "%s:%d" % (self.ip(),self.pid())

    def time(self):
        """@return: the current time in the simulation"""
        if self._master.nowTime:
            return self._master.nowTime
        else:
            return 0
        
    def createTime(self):
        """@return: the time in the simulation for which the mesh was created"""
        if self._master.nowTime:
            return self._master.createTime
        else:
            return 0

    def _readParameter(self,name):
        """Reads a parametr from the controlDict
        @param name: the parameter
        @return: The value"""
        control=ParameterFile(self._master.getSolutionDirectory().controlDict())
        return control.readParameter(name)

    def startTime(self):
        """@return: parameter startTime from the controlDict"""
        return float(self._readParameter("startTime"))
    
    def endTime(self):
        """@return: parameter endTime from the controlDict"""
        return float(self._readParameter("endTime"))
    
    def deltaT(self):
        """@return: parameter startTime from the controlDict"""
        return float(self._readParameter("deltaT"))
    
class FoamServer(Thread):
    """This is the class that serves the requests about the FOAM-Run"""
    def __init__(self,run=None,master=None,lines=100):
	"""
        @param run: The thread that controls the run
        @param master: The Runner-Object that controls everything
	@param lines: the number of lines the server should remember
	"""
        Thread.__init__(self)
        self._port=findFreePort()

        self._running=False

        if self._port<0:
            foamLogger().warning("Could not get a free port. Server not started")
            return
        
        foamLogger().info("Serving on port %d" % self._port)
	self._server=ServerBase(('',self._port),logRequests=False)
        self._server.register_introspection_functions()
        self._answerer=FoamAnswerer(run=run,master=master,lines=lines)
        self._server.register_instance(self._answerer)
        self._server.register_function(self.killServer)
        self._server.register_function(self.kill)
        if run:
            self._server.register_function(run.cpuTime)
            self._server.register_function(run.cpuUserTime)
            self._server.register_function(run.cpuSystemTime)
            self._server.register_function(run.wallTime)
            self._server.register_function(run.usedMemory)

    def run(self):
        if self._port<0:
            return
        # wait befor registering to avoid timeouts
        reg=Timer(5.,self.register)
        reg.start()

        self._running=True

        while self._running:
            self._server.handle_request()
            
        # self._server.serve_forever() # the old way
        self._server.server_close()
        
        foamLogger().info("Stopped serving on port %d" % self._port)

    def info(self):
        """Returns the IP, the PID and the port of the server (as one tuple)"""
        
        return self._answerer.ip(),self._answerer.pid(),self._port
    
    def kill(self):
        """Interrupts the FOAM-process (and kills the server)"""
        self._answerer._kill()
        return self.killServer()
        
    def killServer(self):
        """Kills the server process"""
        tmp=self._running
        self._running=False
        return tmp
    
    def register(self):
        """Tries to register with the Meta-Server"""

        try:
            try:
                meta=ServerProxy("http://%s:%d" % (config().get("Metaserver","ip"),config().getint("Metaserver","port")))
                meta.registerServer(self._answerer.ip(),self._answerer.pid(),self._port)
            except socket.error, reason:
                foamLogger().warning("Can't connect to meta-server - SocketError: "+str(reason))
            except:
                foamLogger().error("Can't connect to meta-server - Unknown Error: "+str(sys.exc_info()[0]))
                foamLogger().error(str(sys.exc_info()[1]))
                foamLogger().error("Traceback: "+str(extract_tb(sys.exc_info()[2])))
        except:
            # print "Error during registering (no socket module?)"
            pass
        
    def deregister(self):
        """Tries to deregister with the Meta-Server"""
        self._server.server_close()

        try:
            meta=ServerProxy("http://%s:%d" % (config().get("Metaserver","ip"),config().getint("Metaserver","port")))
            meta.deregisterServer(self._answerer.ip(),self._answerer.pid(),self._port)
        except socket.error, reason:
            foamLogger().warning("Can't connect to meta-server - SocketError: "+str(reason))
        except:
            foamLogger().error("Can't connect to meta-server - Unknown Error: "+str(sys.exc_info()[0]))
            foamLogger().error(str(sys.exc_info()[1]))
            foamLogger().error("Traceback: "+str(extract_tb(sys.exc_info()[2])))
        
    def _insertLine(self,line):
        """Inserts a new line, not to be called via XMLRPC"""
        self._answerer._insertLine(line)
