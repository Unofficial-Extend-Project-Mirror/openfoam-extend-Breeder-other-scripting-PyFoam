#  ICE Revision: $Id$
"""Plots a collection of timelines"""

from PyFoam.ThirdParty.Gnuplot import Gnuplot,Data,gp

from PyFoam.Error import warning

from .GeneralPlotTimelines import GeneralPlotTimelines

from platform import uname

from PyFoam import configuration as config

def validTerminals():
    """Returns a list with the valid Gnuplot terminals"""
    terms=["x11","wxt","caca","dumb"]
    if uname()[0]=="Darwin":
        terms.append("aqua")
    return terms

class GnuplotTimelines(GeneralPlotTimelines,Gnuplot):
    """This class opens a gnuplot window and plots a timelines-collection in it"""

    terminalNr=1

    def __init__(self,
                 timelines,
                 custom,
                 terminal="x11",
                 showWindow=True,
                 registry=None):
        """:param timelines: The timelines object
        :type timelines: TimeLineCollection
        :param custom: A CustomplotInfo-object. Values in this object usually override the
        other options. If the object has an attribute named gnuplotCommands
        (which is assumed to be a string list) then these strings are executed during
        initialization of the plot (the purpose of this is to set non-standard stuff)
        :param terminal: terminal implementation to use
        """

        GeneralPlotTimelines.__init__(self,timelines,custom,showWindow=showWindow,registry=registry)
        Gnuplot.__init__(self,persist=self.spec.persist)

        self.itemlist=[]

        if self.spec.start or self.spec.end:
            rng="["
            if self.spec.start:
                rng+=str(self.spec.start)
            rng+=":"
            if self.spec.end:
                rng+=str(self.spec.end)
            rng+="]"
            self.set_string("xrange "+rng)

        if len(self.alternate)>0:
            self.set_string("y2tics")

        try:
            if self.spec.logscale:
                self.set_string("logscale y")
        except AttributeError:
            pass

        try:
            if self.spec.ylabel:
                self.set_string('ylabel "'+self.spec.ylabel+'"')
        except AttributeError:
            pass

        try:
            if self.spec.xlabel:
                self.set_string('xlabel "'+self.spec.xlabel+'"')
        except AttributeError:
            pass

        try:
            if self.spec.y2label:
                self.set_string('y2label  "'+self.spec.y2label+'"')
        except AttributeError:
            pass

        raiseit=False
        enhanced=False
        x11addition=[]

        if "raiseit" in dir(self.spec):
            raiseit=self.spec.raiseit
        if raiseit:
            x11addition.append("raise")
        else:
            x11addition.append("noraise")
        if "enhanced" in dir(self.spec):
            enhanced=self.spec.enhanced
        if enhanced:
            x11addition.append("enhanced")
        else:
            x11addition.append("noenhanced")

        if showWindow:
            self.set_string("terminal "+terminal+" "+" ".join(x11addition))
            if uname()[0]=="Darwin":
                GnuplotTimelines.terminalNr+=1
        else:
            self.set_string("terminal dumb")

        self.with_=self.spec.with_

        self(config().get("Plotting","gnuplotCommands"))

        try:
            for l in custom.gnuplotCommands:
                self(l)
        except AttributeError:
            pass

        self.redo()

    def buildData(self,times,name,title,lastValid):
        """Build the implementation specific data
        :param times: The vector of times for which data exists
        :param name: the name under which the data is stored in the timeline
        :param title: the title under which this will be displayed"""

        tm=times
        dt=self.data.getValues(name)
        if len(tm)>0 and not lastValid:
            tm=tm[:-1]
            dt=dt[:-1]

        if len(dt)>0:
            it=Data(tm,dt,title=title,with_=self.with_)

            if self.testAlternate(name):
                it.set_option(axes="x1y2")

            self.itemlist.append(it)

    def preparePlot(self):
        """Prepare the plotting window"""
        self.itemlist=[]

    def doReplot(self):
        """Replot the whole data"""

        self.replot()

    def actualSetTitle(self,title):
        """Sets the title"""

        self.title(title)

    def setYLabel(self,title):
        """Sets the label on the first Y-Axis"""

        self.set_string('ylabel "%s"' % title)

    def setYLabel2(self,title):
        """Sets the label on the second Y-Axis"""

        self.set_string('y2label "%s"' % title)

    def internalHardcopy(self,terminal,filename):
        """Emulate the regular hardcopy command"""
        self.set_string("output",filename)
        self("set terminal "+terminal)
        self.refresh()
        # reset the terminal to its `default' setting:
        self('set terminal %s' % gp.GnuplotOpts.default_term)
        self.set_string('output')

    def doHardcopy(self,filename,form,termOpts=""):
        """Write the contents of the plot to disk
        :param filename: Name of the file without type extension
        :param form: String describing the format"""

        # print "Hardcopy",filename,form,termOpts

        if termOpts!="":
            termOpts=" "+termOpts

        if form=="png":
            self.internalHardcopy(terminal="png"+termOpts,filename=filename+".png")
        elif form=="pdf":
            self.internalHardcopy(terminal="pdf"+termOpts,filename=filename+".pdf")
        elif form=="svg":
            self.internalHardcopy(terminal="svg"+termOpts,filename=filename+".svg")
        elif form=="postscript":
            self.internalHardcopy(terminal="postscript"+termOpts,filename=filename+".ps")
        elif form=="eps":
            self.internalHardcopy(terminal="postscript eps"+termOpts,filename=filename+".eps")
        else:
            warning("Hardcopy format",form,"unknown. Falling back to postscript")
            self.hardcopy(filename=filename+".ps",color=True)

# Should work with Python3 and Python2
