#  ICE Revision: $Id$
"""Plots a collection of timelines. General superclass for te other implementations"""

from PyFoam.Basics.CustomPlotInfo import readCustomPlotInfo,CustomPlotInfo

from PyFoam.Error import notImplemented

from PyFoam.ThirdParty.six import iteritems

import re

class PlotLinesRegistry(object):
    """Collects references to GeneralPlotLines objects"""

    nr=1

    def __init__(self):
        self.plots={}

    def clear(self):
        PlotLinesRegistry.nr=1
        self.plots={}

    def add(self,plot):
        nr=PlotLinesRegistry.nr
        PlotLinesRegistry.nr+=1
        self.plots[nr]=plot

        return nr

    def prepareForTransfer(self):
        """Makes sure that the data about the plots is to be transfered via XMLRPC"""
        lst={}
        for i,p in iteritems(self.plots):
            lst[str(i)]={ "nr"   : i,
                     "spec" : p.spec.getDict(),
                     "id"   : p.spec.id,
                     "data" : p.data.lineNr }
        return lst

_allPlots=PlotLinesRegistry()

def allPlots():
    return _allPlots


class GeneralPlotTimelines(object):
    """This class defines the interface for specific implementations of plotting

    This class is moedelled after the Gnuplot-class from the Gnuplot-package"""

    def __init__(self,
                 timelines,
                 custom,
                 showWindow=True,
                 registry=None):
        """:param timelines: The timelines object
        :type timelines: TimeLineCollection
        :param custom: A CustomplotInfo-object. Values in this object usually override the
        other options
        :param showWindow: whether or not to show a window. Doesn't affect all implementations
        """

        self.data=timelines
        self.spec=custom

        self.alternate=getattr(self.spec,"alternateAxis",[])
        self.forbidden=getattr(self.spec,"forbidden",[])

        self.showWindow=showWindow

        if registry==None:
            registry=allPlots()
        self.nr=registry.add(self)

    def testAlternate(self,name):
        if name in self.alternate:
            return True

        if name.find("_slave")>0 and re.compile(r".+_slave[0-9]*").match(name):
            return self.testAlternate(name[:name.find("_slave")])

        for a in self.alternate:
            try:
                try:
                    if re.compile(a).fullmatch(name):
                        return True
                except AttributeError:
                    # python 2 has no fullmatch
                    if re.compile("(?:" + a + r")\Z").match(name):
                        return True

            except re.error:
                pass

        return False

    def getNames(self):
        """Get the names of the data items"""
        names=[]
        tmp=self.data.getValueNames()

        for n in tmp:
            addIt=True
            for f in self.forbidden:
                if n.find(f)>=0:
                    addIt=False
                    break
            if addIt:
                names.append(n)
        return sorted(names)

    def hasTimes(self):
        """Check whether this timeline contains any timesteps"""
        return len(self.data.getTimes())>0

    def hasData(self):
        """Check whether there is any plotable data"""
        return self.hasTimes() and len(self.getNames())>0

    def redo(self):
        """Replot the timelines"""
        if not self.hasData():
            return

        self.preparePlot()

        names=self.getNames()
        for n in names:
            title=n

            if title.find("_slave")>=0:
                title=title[: title.find("_slave")]
                slaveNr=int(n[n.find("_slave")+len("_slave"):])
                lastValid=self.data.slaves[slaveNr].lastValid[title]
            else:
                lastValid=self.data.lastValid[title]
            times=self.data.getTimes(title)
            self.buildData(times,n,title,lastValid)

        if len(names)>0 and len(times)>0:
            self.doReplot()

    def buildData(self,times,name,title,lastValid):
        """Build the implementation specific data
        :param times: The vector of times for which data exists
        :param name: the name under which the data is stored in the timeline
        :param title: the title under which this will be displayed
        :param lastValid: wether the last data entry is valid"""

        notImplemented(self,"buildData")

    def preparePlot(self):
        """Prepare the plotting window"""

        notImplemented(self,"preparePlot")


    def doReplot(self):
        """Replot the whole data"""

        notImplemented(self,"doReplot")

    def actualSetTitle(self,title):
        """Sets the title"""

        notImplemented(self,"actualSetTitle")

    def setTitle(self,title):
        """Sets the title"""
        self.actualSetTitle(title)
        self.spec.theTitle=title

    def setYLabel(self,title):
        """Sets the label on the first Y-Axis"""

        notImplemented(self,"setYLabel")

    def setYLabel2(self,title):
        """Sets the label on the second Y-Axis"""

        notImplemented(self,"setYLabel2")

    def doHardcopy(self,filename,form,termOpts=None):
        """Write the contents of the plot to disk
        :param filename: Name of the file without type extension
        :param form: String describing the format"""

        notImplemented(self,"doHardcopy")

# Should work with Python3 and Python2
