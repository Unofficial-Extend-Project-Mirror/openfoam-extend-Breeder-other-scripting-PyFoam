#! /usr/bin/env python
"""Lists the running pyFoam-Processes"""

from PyFoam.Applications.PyFoamApplication import PyFoamApplication
from PyFoam import configuration as config

import xmlrpclib,socket,sys,time

class NetList(PyFoamApplication):
    def __init__(self):
        description="""\
Lists all the processes known to a meta-server
        """
        self.defaultHost=config().get("Metaserver","ip")
        self.defaultPort=config().getint("Metaserver","port")

        PyFoamApplication.__init__(self,description=description,usage="%prog [options]",interspersed=True,nr=0)

    def addOptions(self):
        self.parser.add_option("--server",
                               type="string",
                               dest="server",
                               default=self.defaultHost,
                               help="The server that should be queried (Default: "+self.defaultHost+")")
        self.parser.add_option("--port",
                               type="int",
                               dest="port",
                               default=self.defaultPort,
                               help="The port at which the query takes place (Default: "+str(self.defaultPort)+")")
        self.parser.add_option("--dump",
                               action="store_true",
                               dest="dump",
                               default=False,
                               help="Dump all the statically stored data")
        self.parser.add_option("--process",
                               action="store_true",
                               dest="process",
                               default=False,
                               help="Additional data about the process")
        self.parser.add_option("--time",
                               action="store_true",
                               dest="time",
                               default=False,
                               help="Request timing information")
        self.parser.add_option("--ip",
                               action="store_true",
                               dest="ip",
                               default=False,
                               help="Output the IP-number instead of the machine name")
        self.parser.add_option("--user",
                               action="store",
                               dest="user",
                               default=None,
                               help="Only show runs that belong to a certain username")
        
    def run(self):
        try:
            self.server=xmlrpclib.ServerProxy("http://%s:%d" % (self.parser.options.server,self.parser.options.port))
            data=self.server.list()
        except socket.error,reason:
            print "Socket error while connecting:",reason
            sys.exit(1)
        except xmlrpclib.ProtocolError,reason:
            print "XMLRPC-problem",reason
            sys.exit(1)

        hostString="Hostname"
        maxhost=len(hostString)
        cmdString="Command Line"
        maxcommandline=len(cmdString)

        for name,info in data.iteritems():
            if len(info["commandLine"])>maxcommandline:
                maxcommandline=len(info["commandLine"])
            if self.opts.ip:
                tmpHost=info["ip"]
            else:
                tmpHost=info["hostname"]
                
            if len(tmpHost)>maxhost:
                maxhost=len(tmpHost)

        header=hostString+(" "*(maxhost-len(hostString)))+" | "+" Port  | User       | "+cmdString+"\n"
        line=("-"*(len(header)))
        header+=line

        formatString="%-"+str(maxhost)+"s | %6d | %10s | %s"
        print header
        
        for name,info in data.iteritems():
            if self.opts.user:
                if self.opts.user!=info["user"]:
                    continue
                
            if self.opts.ip:
                tmpHost=info["ip"]
            else:
                tmpHost=info["hostname"]

            print formatString % (tmpHost,info["port"],info["user"],info["commandLine"])
            if self.parser.options.process:
                isParallel=self.forwardCommand(info,"isParallel()")
                if isParallel:
                    pidString="CPUs: %5d" % self.forwardCommand(info,"procNr()")
                else:
                    pidString="PID: %6d" % info["pid"]
                print "  %s   Working dir: %s" % (pidString,info["cwd"])
            if self.parser.options.time:
                startTime=self.forwardCommand(info,"startTime()")
                endTime=self.forwardCommand(info,"endTime()")
                createTime=self.forwardCommand(info,"createTime()")
                nowTime=self.forwardCommand(info,"time()")
                try:
                    progress=(nowTime-createTime)/(endTime-createTime)
                except ZeroDivisionError:
                    progress=0

                try:
                    progress2=(nowTime-startTime)/(endTime-startTime)
                except ZeroDivisionError:
                    progress2=0
                
                print "  Time: %g Timerange: [ %g , %g ]  Mesh created: %g -> Progress: %.2f%% (Total: %.2f%%)" % (nowTime,startTime,endTime,createTime,progress*100,progress2*100)

                wallTime=self.forwardCommand(info,"wallTime()")
                now=time.time()
                start=now-wallTime
                startString=time.strftime("%Y-%b-%d %H:%M",time.localtime(start))
                try:
                    estimate=start+wallTime/progress
                    estimateString=time.strftime("%Y-%b-%d %H:%M",time.localtime(estimate))
                except ZeroDivisionError:
                    estimate=start
                    estimateString=" - NaN - "
                    
                print "  Started: %s   Walltime: %8gs  Estimated End: %s" % (startString,wallTime,estimateString)
                
            if self.parser.options.process or self.parser.options.time:
                print line
            if self.parser.options.dump:
                print info
                print line
                
    def forwardCommand(self,info,cmd):
        """Forwards a command
        :param info: dictionary with the information
        :param cmd: the command that will be forwarded
        """
        result=0

        try:
            result=float(self.server.forwardCommand(info["ip"],info["port"],cmd))
        except:
            pass
        
        return result
    
NetList()

