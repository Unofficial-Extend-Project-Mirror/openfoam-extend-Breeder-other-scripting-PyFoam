#  ICE Revision: $Id: SamplePlot.py 11121 2009-12-21 17:05:33Z bgschaid $ 
"""
Application class that implements pyFoamSamplePlot.py
"""

import sys,string
from os import path
from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication
from PyFoam.RunDictionary.SampleDirectory import SampleDirectory

from PyFoam.Error import error,warning

from PlotHelpers import cleanFilename

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
                                   changeVersion=False,
                                   interspersed=True)
        
    modeChoices=["separate","timesInOne","fieldsInOne","complete"]    

    def addOptions(self):
        data=OptionGroup(self.parser,
                          "Data",
                          "Select the data to plot")
        self.parser.add_option_group(data)
        
        data.add_option("--line",
                        action="append",
                        default=None,
                        dest="line",
                        help="Thesample line from which data is plotted (can be used more than once)")
        data.add_option("--field",
                        action="append",
                        default=None,
                        dest="field",
                        help="The fields that are plotted (can be used more than once). If none are specified all found fields are used")
        data.add_option("--directory-name",
                        action="store",
                        default="samples",
                        dest="dirName",
                        help="Alternate name for the directory with the samples (Default: %default)")
        data.add_option("--preferred-component",
                        action="store",
                        type="int",
                        default=None,
                        dest="component",
                        help="The component that should be used for vectors. Otherwise the absolute value is used")
        
        time=OptionGroup(self.parser,
                         "Time",
                         "Select the times to plot")
        self.parser.add_option_group(time)
        
        time.add_option("--time",
                        action="append",
                        default=None,
                        dest="time",
                        help="The times that are plotted (can be used more than once). If none are specified all found times are used")
        time.add_option("--min-time",
                        action="store",
                        type="float",
                        default=None,
                        dest="minTime",
                        help="The smallest time that should be used")
        time.add_option("--max-time",
                        action="store",
                        type="float",
                        default=None,
                        dest="maxTime",
                        help="The biggest time that should be used")
        time.add_option("--fuzzy-time",
                        action="store_true",
                        default=False,
                        dest="fuzzyTime",
                        help="Try to find the next timestep if the time doesn't match exactly")

        output=OptionGroup(self.parser,
                           "Appearance",
                           "How it should be plotted")
        self.parser.add_option_group(output)
        
        output.add_option("--mode",
                          type="choice",
                          default="separate",
                          dest="mode",
                          action="store",
                          choices=self.modeChoices,
                          help="What kind of plots are generated: a) separate for every time and field b) all times of a field in one plot c) all fields of a time in one plot d) all lines in one plot. (Names: "+string.join(self.modeChoices,", ")+") Default: %default")
        output.add_option("--unscaled",
                          action="store_false",
                          dest="scaled",
                          default=True,
                          help="Don't scale a value to the same range for all plots")
        output.add_option("--scale-all",
                          action="store_true",
                          dest="scaleAll",
                          default=False,
                          help="Use the same scale for all fields (else use one scale for each field)")
        output.add_option("--gnuplot-file",
                          action="store",
                          dest="gnuplotFile",
                          default=None,
                          help="Write the necessary gnuplot commands to this file. Else they are written to the standard output")
        output.add_option("--picture-destination",
                          action="store",
                          dest="pictureDest",
                          default=None,
                          help="Directory the pictures should be stored to")
        output.add_option("--name-prefix",
                          action="store",
                          dest="namePrefix",
                          default=None,
                          help="Prefix to the picture-name")
        
        data.add_option("--info",
                        action="store_true",
                        dest="info",
                        default=False,
                        help="Print info about the sampled data and exit")
        output.add_option("--style",
                          action="store",
                          default="lines",
                          dest="style",
                          help="Gnuplot-style for the data (Default: %default)")
        output.add_option("--clean-filename",
                          action="store_true",
                          dest="cleanFilename",
                          default=False,
                          help="Clean filenames so that they can be used in HTML or Latex-documents")
        
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
            #            error("At least one line has to be specified. Found were",samples.lines())
            self.opts.line=lines
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
        elif self.opts.time:
            iTimes=self.opts.time
            self.opts.time=[]
            for t in iTimes:
                if t in samples.times:
                    self.opts.time.append(t)
                elif self.opts.fuzzyTime:
                    tf=float(t)
                    use=None
                    dist=1e20
                    for ts in samples.times:
                        if abs(tf-float(ts))<dist:
                            use=ts
                            dist=abs(tf-float(ts))
                    if use and use not in self.opts.time:
                        self.opts.time.append(use)
                else:
                    pass
                #                    self.warning("Time",t,"not found in the sample-times. Use option --fuzzy")
                
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
            if self.opts.scaled and not self.opts.scaleAll:
                warning("In mode '",self.opts.mode,"' all fields are scaled to the same value")
                self.opts.scaleAll=True
                
            if self.opts.time==None:
                self.opts.time=samples.times
            for t in self.opts.time:
                plots.append(samples.getData(line=self.opts.line,
                                             value=self.opts.field,
                                             time=[t]))
        elif self.opts.mode=="complete":
            if self.opts.scaled and not self.opts.scaleAll:
                warning("In mode '",self.opts.mode,"' all fields are scaled to the same value")
                self.opts.scaleAll=True

            plots.append(samples.getData(line=self.opts.line,
                                         value=self.opts.field,
                                         time=self.opts.time))

        if self.opts.scaled:
            if self.opts.scaleAll:
                vRange=None
            else:
                vRanges={}
                
            for p in plots:
                for d in p:
                    mi,ma=d.range(component=self.opts.component)
                    nm=d.name
                    if not self.opts.scaleAll:
                        if nm in vRanges:
                            vRange=vRanges[nm]
                        else:
                            vRange=None
                            
                    if vRange==None:
                        vRange=mi,ma
                    else:
                        vRange=min(vRange[0],mi),max(vRange[1],ma)
                    if not self.opts.scaleAll:
                        vRanges[nm]=vRange
            
        result="set term png\n"

        for p in plots:
            if len(p)<1:
                continue

            name=""
            if self.opts.namePrefix:
                name+=self.opts.namePrefix+"_"
            name+=self.opts.dirName
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
            if self.opts.pictureDest:
                name=path.join(self.opts.pictureDest,name)

            if self.opts.cleanFilename:
                name=cleanFilename(name)
                
            result+='set output "%s"\n' % name
            if title!=None:
                result+='set title "%s"\n' % title
                
            result+="plot "
            if self.opts.scaled:
                if not self.opts.scaleAll:
                    vRange=vRanges[p[0].name]

                # only scale if extremas are sufficiently different
                if abs(vRange[0]-vRange[1])>1e-5*max(abs(vRange[0]),abs(vRange[1])) and max(abs(vRange[0]),abs(vRange[1]))>1e-10:
                    result+="[][%g:%g] " % vRange

            first=True

            for d in p:
                if first:
                    first=False
                else:
                    result+=", "

                colSpec="%s" % (d.index+1)
                if d.isVector():
                    if self.opts.component:
                        colSpec="%d" % (d.index+1+self.opts.component)
                    else:
                        colSpec="(sqrt($%d**2+$%d**2+$%d**2))" % (d.index+1,d.index+2,d.index+3)
                    
                result+='"%s" using 1:%s ' % (d.file,colSpec)
                
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

        dest=sys.stdout
        if self.opts.gnuplotFile:
            dest=open(self.opts.gnuplotFile,"w")
            
        dest.write(result)
        
