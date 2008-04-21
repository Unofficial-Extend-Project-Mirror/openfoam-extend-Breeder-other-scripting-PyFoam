#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/SamplePlot.py 2683 2008-01-18T15:00:48.175145Z bgschaid  $ 
"""
Application class that implements pyFoamSamplePlot.py
"""

import sys,string

from PyFoamApplication import PyFoamApplication
from PyFoam.RunDictionary.SampleDirectory import SampleDirectory

from PyFoam.Error import error

class SamplePlot(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Reads data from the sample-dictionary and generates appropriate
gnuplot-commands
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <casedir>",
                                   nr=1,
                                   interspersed=True)
        
    modeChoices=["separate","timesInOne","fieldsInOne","complete"]    

    def addOptions(self):
        self.parser.add_option("--line",
                               action="append",
                               default=None,
                               dest="line",
                               help="Thesample line from which data is plotted (can be used more than once)")
        self.parser.add_option("--field",
                               action="append",
                               default=None,
                               dest="field",
                               help="The fields that are plotted (can be used more than once). If none are specified all found fields are used")
        self.parser.add_option("--time",
                               action="append",
                               default=None,
                               dest="time",
                               help="The times that are plotted (can be used more than once). If none are specified all found times are used")
        self.parser.add_option("--min-time",
                               action="store",
                               type="float",
                               default=None,
                               dest="minTime",
                               help="The smallest time that should be used")
        self.parser.add_option("--max-time",
                               action="store",
                               type="float",
                               default=None,
                               dest="maxTime",
                               help="The biggest time that should be used")
        self.parser.add_option("--mode",
                               type="choice",
                               default="separate",
                               dest="mode",
                               action="store",
                               choices=self.modeChoices,
                               help="What kind of plots are generated: a) separate for every time and field b) all times of a field in one plot c) all fields of a time in one plot d) all lines in one plot. (Names: "+string.join(self.modeChoices,", ")+") Default: %default")
        self.parser.add_option("--directory-name",
                               action="store",
                               default="samples",
                               dest="dirName",
                               help="Alternate name for the directory with the samples (Default: %default)")
        self.parser.add_option("--unscaled",
                               action="store_false",
                               dest="scaled",
                               default=True,
                               help="Don't scale a value to the same range for all plots")
        self.parser.add_option("--info",
                               action="store_true",
                               dest="info",
                               default=False,
                               help="Print info about the sampled data and exit")
        self.parser.add_option("--style",
                               action="store",
                               default="lines",
                               dest="style",
                               help="Gnuplot-style for the data (Default: %default)")
        
    def run(self):
        samples=SampleDirectory(self.parser.getArgs()[0],dirName=self.opts.dirName)

        lines=samples.lines()
        times=samples.times
        values=samples.values()
        
        if self.opts.info:
            print "Times : ",samples.times
            print "Lines : ",samples.lines()
            print "Values: ",samples.values()
            sys.exit(0)
            
        if self.opts.line==None:
            error("At least one line has to be specified. Found were",samples.lines())
        else:
            
            for l in self.opts.line:
                if l not in lines:
                    error("The line",l,"does not exist in",lines)

        if self.opts.maxTime or self.opts.minTime:
            if self.opts.time:
                error("Times",self.opts.time,"and range [",self.opts.minTime,",",self.opts.maxTime,"] set: contradiction")
            self.opts.time=[]
            if self.opts.maxTime==None:
                self.opts.maxTime= 1e20
            if self.opts.minTime==None:
                self.opts.minTime=-1e20

            for t in times:
                if float(t)<=self.opts.maxTime and float(t)>=self.opts.minTime:
                    self.opts.time.append(t)

            if len(self.opts.time)==0:
                error("No times in range [",self.opts.minTime,",",self.opts.maxTime,"] found: ",times)
                
        plots=[]

        if self.opts.mode=="separate":
            if self.opts.time==None:
                self.opts.time=samples.times
            if self.opts.field==None:
                self.opts.field=samples.values()
            for t in self.opts.time:
                for f in self.opts.field:
                    plots.append(samples.getData(line=self.opts.line,
                                                 value=[f],
                                                 time=[t]))
        elif self.opts.mode=="timesInOne":
            if self.opts.field==None:
                self.opts.field=samples.values() 
            for f in self.opts.field:
                plots.append(samples.getData(line=self.opts.line,
                                             value=[f],
                                             time=self.opts.time))
        elif self.opts.mode=="fieldsInOne":
            if self.opts.time==None:
                self.opts.time=samples.times
            for t in self.opts.time:
                plots.append(samples.getData(line=self.opts.line,
                                             value=self.opts.field,
                                             time=[t]))
        elif self.opts.mode=="complete":
            plots.append(samples.getData(line=self.opts.line,
                                         value=self.opts.field,
                                         time=self.opts.time))

        if self.opts.scaled:
            vRange=None
            for p in plots:
                for d in p:
                    mi,ma=d.range()
                    if vRange==None:
                        vRange=mi,ma
                    else:
                        vRange=min(vRange[0],mi),max(vRange[1],ma)
                        
        result="set term png\n"

        for p in plots:
            if len(p)<1:
                continue

            name=self.opts.dirName
            title=None
            tIndex=times.index(p[0].time())
            
            name+="_"+string.join(self.opts.line,"_")

            if self.opts.mode=="separate":
                name+="_%s_%04d"   % (p[0].name,tIndex)
                title="%s at t=%f" % (p[0].name,float(p[0].time()))
            elif self.opts.mode=="timesInOne":
                if self.opts.time!=None:
                    name+="_"+string.join(self.opts.time,"_")
                name+="_%s" % p[0].name
                title="%s"  % p[0].name
            elif self.opts.mode=="fieldsInOne":
                if self.opts.field!=None:
                    name+="_"+string.join(self.opts.field,"_")
                name+="_%04d" % tIndex
                title="t=%f"  % float(p[0].time())
            elif self.opts.mode=="complete":
                pass
            
            name+=".png"
            result+='set output "%s"\n' % name
            if title!=None:
                result+='set title "%s"\n' % title
                
            result+="plot "
            if self.opts.scaled:
                result+="[][%f:%f] " % vRange

            first=True

            for d in p:
                if first:
                    first=False
                else:
                    result+=", "

                result+='"%s" using 1:%d ' % (d.file,d.index+1)
                
                title=None
                if self.opts.mode=="separate":
                    title=""
                elif self.opts.mode=="timesInOne":
                    title="t=%f" % float(d.time())
                elif self.opts.mode=="fieldsInOne":
                    title="%s"   % d.name
                elif self.opts.mode=="complete":
                    title="%s at t=%f" % (d.name,float(d.time()))

                if len(self.opts.line)>1:
                    title+=" on %s" % d.line()

                if title=="":
                    result+="notitle "
                else:
                    result+='title "%s" ' % title

                result+="with %s " % self.opts.style

            result+="\n"

        print result
        
