#! /usr/bin/env python
"""A test utility that ghets all the information necessary for plotting from a remote machine and writes some plots<<"""

from PyFoam.Applications.PyFoamApplication import PyFoamApplication

import xmlrpclib,socket
import sys

from PyFoam.Basics.TimeLineCollection import TimeLineCollection,TimeLinesRegistry
from PyFoam.Basics.MatplotlibTimelines import MatplotlibTimelines
from PyFoam.Basics.GeneralPlotTimelines import PlotLinesRegistry
from PyFoam.Basics.CustomPlotInfo import CustomPlotInfo

class PlotRemote(PyFoamApplication):
    prompt="PFNET> "

    def __init__(self):
        description="""
        Connects to a running pyFoam-Server and gets all the information for plotting
        """
        PyFoamApplication.__init__(self,description=description,usage="%prog <host> <port>",interspersed=True,nr=2)
    def addOptions(self):
        pass
    
    def run(self):
        host=self.parser.getArgs()[0]
        port=int(self.parser.getArgs()[1])

        try:
            self.server=xmlrpclib.ServerProxy("http://%s:%d" % (host,port))
            methods=self.server.system.listMethods()
        except socket.error,reason:
            print "Socket error while connecting:",reason
            sys.exit(1)
        except xmlrpclib.ProtocolError,reason:
            print "XMLRPC-problem",reason
            sys.exit(1)

        plotInfo=self.executeCommand("getPlots()")
        lineInfo=self.executeCommand("getPlotData()")
        print "Found",len(plotInfo),"plots and",len(lineInfo),"data sets"
        
        registry=TimeLinesRegistry()
        for nr,line in lineInfo.iteritems():
            print "Adding line",nr
            TimeLineCollection(preloadData=line,registry=registry)
            
        registry.resolveSlaves()

        pRegistry=PlotLinesRegistry()
        
        for i,p in plotInfo.iteritems():
            theId=p["id"]
            print "Plotting",i,":",theId,
            spec=CustomPlotInfo(raw=p["spec"])
            mp=MatplotlibTimelines(registry.get(p["data"]),
                                   spec,
                                   showWindow=False,
                                   registry=pRegistry)
            if mp.hasData():
                mp.doHardcopy(theId,"png")
            else:
                print "has no data",
            print
            
    def executeCommand(self,cmd):
        result=None
        try:
            result=eval("self.server."+cmd)
            if result==None: # this needed to catch the unmarschalled-None-exception
                return None
        except xmlrpclib.Fault,reason:
            print "XMLRPC-problem:",reason.faultString
        except socket.error,reason:
            print "Problem with socket (server propably dead):",reason
        except TypeError,reason:
            print "Type error: ",reason
            result=None
        except SyntaxError,reason:
            print "Syntax Error in:",cmd
            
        return result

PlotRemote()
