#! /usr/bin/env python
"""A test utility that ghets all the information necessary for plotting from a remote machine and writes some plots<<"""

import sys

from PyFoam.Applications.PyFoamApplication import PyFoamApplication

from PyFoam.ThirdParty.six import PY3
if PY3:
    from xmlrpc.client import ServerProxy,Fault,ProtocolError
else:
    from xmlrpclib import ServerProxy,Fault,ProtocolError

import socket

from optparse import OptionGroup
from PyFoam.ThirdParty.six.moves import cPickle as pickle
from time import sleep

from PyFoam.Basics.TimeLineCollection import TimeLineCollection,TimeLinesRegistry
from PyFoam.Basics.PlotTimelinesFactory import createPlotTimelines
from PyFoam.Basics.GeneralPlotTimelines import PlotLinesRegistry
from PyFoam.Basics.CustomPlotInfo import CustomPlotInfo
from PyFoam.Error import error,warning

from PyFoam.ThirdParty.six import print_,iteritems

class RedoPlot(PyFoamApplication):
    def __init__(self):
        description="""\
Either connects to a running pyFoam-Server and gets all the
information for plotting or reads the relevant data from a pickle file
and either displays the plot or writes the plots to file
        """
        PyFoamApplication.__init__(self,
                                   description=description,
                                   usage="%prog [options] (<host> <port>|<pickleFile>)",
                                   interspersed=True,
                                   nr=1,
                                   exactNr=False)
    def addOptions(self):
        mode=OptionGroup(self.parser,
                         "Input mode",
                         "How we get the data")
        mode.add_option("--server",
                        dest="server",
                        action="store_true",
                        default=False,
                        help="Get the data from a FoamServer")
        mode.add_option("--pickle-file",
                        dest="pickle",
                        action="store_true",
                        default=False,
                        help="Get the data from a pickle-file")

        self.parser.add_option_group(mode)

        output=OptionGroup(self.parser,
                           "Output",
                           "Output of the data")
        output.add_option("--csv-files",
                          dest="csvFiles",
                          action="store_true",
                          default=False,
                          help="Write CSV-files instead of plotting")
        output.add_option("--file-prefix",
                          dest="filePrefix",
                          default="",
                          help="Prefix to add to the names of the data files")
        output.add_option("--raw-lines",
                          dest="rawLines",
                          action="store_true",
                          default=False,
                          help="Write the raw line data (not the way it is plotted)")
        self.parser.add_option_group(output)

        plot=OptionGroup(self.parser,
                         "Plot mode",
                         "How the data should be plotted")

        plot.add_option("--implementation",
                        default="matplotlib",
                        dest="implementation",
                        help="The implementation that should be used for plotting")
        plot.add_option("--show-window",
                        dest="showWindow",
                        action="store_true",
                        default=False,
                        help="Show the window with the plot")
        plot.add_option("--no-write-pictures",
                        dest="writePictures",
                        action="store_false",
                        default=True,
                        help="Do not write picture files")
        plot.add_option("--picture-prefix",
                        dest="prefix",
                        default="",
                        help="Prefix to add to the names of the picture files")
        plot.add_option("--sleep-time",
                        dest="sleepTime",
                        action="store",
                        default=0.1,
                        type="float",
                        help="How long to wait to allow gnuplot to finish. Default: %default")
        plot.add_option("--insert-titles",
                        dest="insertTitles",
                        action="store_true",
                        default=False,
                        help="Add the title to the plots")
        plot.add_option("--start",
                        dest="start",
                        action="store",
                        default=None,
                        type="float",
                        help="Start the plot at this time. If undefined starts at the beginning of the data")
        plot.add_option("--end",
                        dest="end",
                        action="store",
                        default=None,
                        type="float",
                        help="End the plot at this time. If undefined ends at the end of the data")

        self.parser.add_option_group(plot)

    def run(self):
        if not self.opts.server and not self.opts.pickle:
            error("No mode selected")
        if self.opts.server and self.opts.pickle:
            error("Both modes selected")

        if self.opts.server:
            if len(self.parser.getArgs())!=2:
                error("Need a server and a port to be specified")

            host=self.parser.getArgs()[0]
            port=int(self.parser.getArgs()[1])

            try:
                self.server=ServerProxy("http://%s:%d" % (host,port))
                methods=self.server.system.listMethods()
            except socket.error:
                reason = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                self.error("Socket error while connecting:",reason)
            except ProtocolError:
                reason = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                self.error("XMLRPC-problem",reason)

            plotInfo=self.executeCommand("getPlots()")
            lineInfo=self.executeCommand("getPlotData()")
        else:
            if len(self.parser.getArgs()[0])!=1:
                warning("Only the first parameter is used")

            fName=self.parser.getArgs()[0]
            unpick=pickle.Unpickler(open(fName))

            lineInfo=unpick.load()
            plotInfo=unpick.load()

        print_("Found",len(plotInfo),"plots and",len(lineInfo),"data sets")

        registry=TimeLinesRegistry()
        for nr,line in iteritems(lineInfo):
            print_("Adding line",nr)
            TimeLineCollection(preloadData=line,registry=registry)

        registry.resolveSlaves()

        if self.opts.csvFiles and self.opts.rawLines:
            for k,l in iteritems(registry.lines):
                name=str(k)
                if type(k)==int:
                    name="Line%d" % k
                name=self.opts.filePrefix+name+".csv"
                print_("Writing",k,"to",name)
                l.getData().writeCSV(name)
            return

        pRegistry=PlotLinesRegistry()

        for i,p in iteritems(plotInfo):
            theId=p["id"]
            print_("Plotting",i,":",theId,end=" ")
            spec=CustomPlotInfo(raw=p["spec"])
            if len(registry.get(p["data"]).getTimes())>0 and registry.get(p["data"]).getValueNames()>0:
                if self.opts.csvFiles:
                    registry.get(p["data"]).getData().writeCSV(self.opts.filePrefix+theId+".csv")
                else:
                    if self.opts.start or self.opts.end:
                        # rewrite CustomPlotInfo one of these days
                        if "start" in spec.getDict():
                            self.warning("Overriding plot start",spec["start"],
                                         "with",self.opts.start)
                        spec.set("start",self.opts.start)
                        if "end" in spec.getDict():
                            self.warning("Overriding plot end",spec["end"],
                                         "with",self.opts.end)
                        spec.set("end",self.opts.end)

                    mp=createPlotTimelines(registry.get(p["data"]),
                                           spec,
                                           implementation=self.opts.implementation,
                                           showWindow=self.opts.showWindow,
                                           registry=pRegistry)
                    if self.opts.insertTitles:
                        mp.actualSetTitle(p["spec"]["theTitle"])
                    if self.opts.writePictures:
                        if mp.hasData():
                            mp.doHardcopy(self.opts.prefix+theId,"png")
                        else:
                            print_("has no data",end=" ")
                print_()
            else:
                print_("No data - skipping")

            sleep(self.opts.sleepTime) # there seems to be a timing issue with Gnuplot


    def executeCommand(self,cmd):
        result=None
        try:
            result=eval("self.server."+cmd)
            if result==None: # this needed to catch the unmarschalled-None-exception
                return None
        except Fault:
            reason = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
            print_("XMLRPC-problem:",reason.faultString)
        except socket.error:
            reason = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
            print_("Problem with socket (server propably dead):",reason)
        except TypeError:
            reason = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
            print_("Type error: ",reason)
            result=None
        except SyntaxError:
            reason = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
            print_("Syntax Error in:",cmd)

        return result

# Should work with Python3 and Python2
