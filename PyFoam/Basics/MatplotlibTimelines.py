#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/MatplotlibTimelines.py 5768 2009-10-31T12:43:14.986952Z bgschaid  $ 
"""Plots a collection of timelines"""

from PyFoam.Error import warning,error

from PyFoam.Basics.CustomPlotInfo import readCustomPlotInfo,CustomPlotInfo

from GeneralPlotTimelines import GeneralPlotTimelines

from os import uname

firstTimeImport=True

class MatplotlibTimelines(GeneralPlotTimelines):
    """This class opens a matplotlib window and plots a timelines-collection in it"""
    
    figureNr=1
    
    def __init__(self,
                 timelines,
                 custom,
                 showWindow=True,
                 registry=None):
        """@param timelines: The timelines object
        @type timelines: TimeLineCollection
        @param custom: A CustomplotInfo-object. Values in this object usually override the
        other options
        """

        self.hasSubplotHost=True
        try:
            global plt,matplotlib,firstTimeImport,SubplotHost
            import matplotlib
            if not showWindow and firstTimeImport:
                matplotlib.use("agg")
                firstTimeImport=False
            import matplotlib.pyplot as plt
            try:
                from mpl_toolkits.axes_grid.parasite_axes import SubplotHost
            except ImportError:
                self.hasSubplotHost=False
                warning("Matplotlib-Version does not support SubplotHost")
        except ImportError:
            error("Matplotlib not installed.")
    
        GeneralPlotTimelines.__init__(self,timelines,custom,showWindow=showWindow,registry=registry)

        self.figNr=MatplotlibTimelines.figureNr
        MatplotlibTimelines.figureNr+=1

        self.figure=None
        self.title=""
        
        self.ylabel=""
        self.ylabel2=""
        try:
            if self.spec.ylabel:
                self.setYLabel(self.spec.ylabel)
        except AttributeError:
            pass
        try:
            if self.spec.y2label:
                self.setYLabel2(self.spec.y2label)
        except AttributeError:
            pass
        
        self.axis1=None
        self.axis2=None

        self.setTitle(self.spec.theTitle)

        self.with_=self.spec.with_
        if not self.with_ in ['lines','points','dots','steps','linespoints']:
            warning("'with'-style",self.with_,"not implemented, using 'lines'")
            self.with_='lines'
        self.redo()

    def buildData(self,times,name,title,lastValid):
        """Build the implementation specific data
        @param times: The vector of times for which data exists
        @param name: the name under which the data is stored in the timeline
        @param title: the title under which this will be displayed"""

        a=self.axis1
        if name in self.alternate:
            a=self.axis2
        data=self.data.getValues(name)
        tm=times
        if len(tm)>0 and not lastValid:
            tm=tm[:-1]
            data=data[:-1]
        plotIt=True
        try:
            if self.spec.logscale and min(data)<=0:
                plotIt=False
        except AttributeError:
            pass

        drawstyle='default'
        marker=''
        linestyle='-'

        if self.with_=='lines':
            pass
        elif self.with_=='steps':
            drawstyle='steps'
        elif self.with_=='points':
            linestyle=''
            marker='*'
        elif self.with_=='dots':
            linestyle=''
            marker='.'
        elif self.with_=='linespoints':
            marker='*'
        else:
            warning("'with'-style",self.with_,"not implemented, using 'lines'")
        
        if plotIt:
            a.plot(tm,
                   data,
                   label=title,
                   drawstyle=drawstyle,
                   marker=marker,
                   linestyle=linestyle)
        
    def preparePlot(self):
        """Prepare the plotting window"""
        plt.hot()
        self.figure=plt.figure(self.figNr)
        self.figure.clear()
        # this is black magic that makes the legend work with two axes
        if self.hasSubplotHost:
            self.axis1=SubplotHost(self.figure,111)
            self.figure.add_subplot(self.axis1)
        else:
            self.axis1=self.figure.add_subplot(111)
        self.axis1.set_xlabel("Time")
        self.axis1.set_ylabel(self.ylabel)
        if self.spec.start or self.spec.end:
            self.axis1.set_xbound(lower=self.spec.start,upper=self.spec.end)
            
        if len(self.alternate)>0:
            self.axis2=self.axis1.twinx()
            self.axis2.set_ylabel(self.ylabel2)
        
        try:
            if self.spec.logscale:
                self.axis1.set_yscale("log")
                if self.axis2:
                    self.axis2.set_yscale("log")                    
        except AttributeError:
            pass

    def doReplot(self):
        """Replot the whole data"""

        if self.hasSubplotHost:
            l=self.axis1.legend(fancybox=True)
        else:
            l=plt.legend(fancybox=True)
        #         l.get_frame().set_fill(False)
        if l:
            l.get_frame().set_alpha(0.7)
            l.get_texts()[0].set_size(10)
        plt.suptitle(self.title)
        plt.draw()

    def actualSetTitle(self,title):
        """Sets the title"""

        self.title=title

    def setYLabel(self,title):
        """Sets the label on the first Y-Axis"""

        self.ylabel=title

    def setYLabel2(self,title):
        """Sets the label on the second Y-Axis"""

        self.ylabel2=title

    def doHardcopy(self,filename,form):
        """Write the contents of the plot to disk
        @param filename: Name of the file without type extension
        @param form: String describing the format"""

        self.figure.savefig(filename+"."+form,format=form)
        
