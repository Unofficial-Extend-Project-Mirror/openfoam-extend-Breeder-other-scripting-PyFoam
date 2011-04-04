#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/SamplePlot.py 7393 2011-03-29T14:55:03.425417Z bgschaid  $ 
"""
Application class that implements pyFoamSamplePlot.py
"""

import sys,string
from os import path
from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication
from PyFoam.RunDictionary.SampleDirectory import SampleDirectory
from PyFoam.Basics.SpreadsheetData import WrongDataSize

from PyFoam.Error import error,warning

from PlotHelpers import cleanFilename

class SamplePlot(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Reads data from the sample-dictionary and generates appropriate
gnuplot-commands. As an option the data can be written to a
CSV-file.
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <casedir>",
                                   nr=1,
                                   changeVersion=False,
                                   interspersed=True)
        
    modeChoices=["separate","timesInOne","fieldsInOne","linesInOne","complete"]    

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
        data.add_option("--reference-directory",
                        action="store",
                        default=None,
                        dest="reference",
                        help="A reference directory. If fitting sample data is found there it is plotted alongside the regular data")
        data.add_option("--reference-case",
                        action="store",
                        default=None,
                        dest="referenceCase",
                        help="A reference case where a directory with the same name is looked for. Mutual exclusive with --reference-directory")
        
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
                          help="What kind of plots are generated: a) separate for every time, line and field b) all times of a field in one plot c) all fields of a time in one plot d) all lines in one plot e) everything in one plot (Names: "+string.join(self.modeChoices,", ")+") Default: %default")
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
        output.add_option("--csv-file",
                          action="store",
                          dest="csvFile",
                          default=None,
                          help="Write the data to a CSV-file instead of the gnuplot-commands")
        
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
        output.add_option("--reference-prefix",
                          action="store",
                          dest="refprefix",
                          default="Reference",
                          help="Prefix that gets added to the reference lines. Default: %default")
        output.add_option("--resample-reference",
                          action="store_true",
                          dest="resampleReference",
                          default=False,
                          help="Resample the reference value to the current x-axis (for CSV-output)")
        output.add_option("--extend-data",
                          action="store_true",
                          dest="extendData",
                          default=False,
                          help="Extend the data range if it differs (for CSV-files)")
        output.add_option("--compare",
                          action="store_true",
                          dest="compare",
                          default=None,
                          help="Compare all data sets that are also in the reference data")
        output.add_option("--metrics",
                          action="store_true",
                          dest="metrics",
                          default=None,
                          help="Print the metrics of the data sets")
        
    def run(self):
        samples=SampleDirectory(self.parser.getArgs()[0],
                                dirName=self.opts.dirName)
        reference=None
        if self.opts.reference and self.opts.referenceCase:
            self.error("Options --reference-directory and --reference-case are mutual exclusive")
        if self.opts.csvFile and (self.opts.compare or self.opts.metrics):
            self.error("Options --csv-file and --compare/--metrics are mutual exclusive")
            
        if self.opts.reference:
            reference=SampleDirectory(self.parser.getArgs()[0],
                                      dirName=self.opts.reference)
        elif self.opts.referenceCase:
            reference=SampleDirectory(self.opts.referenceCase,
                                      dirName=self.opts.dirName)

        lines=samples.lines()
        times=samples.times
        values=samples.values()
        
        if self.opts.info:
            print "Times : ",samples.times
            print "Lines : ",samples.lines()
            print "Fields: ",samples.values()

            if reference:
                print "\nReference Data:"
                print "Times : ",reference.times
                print "Lines : ",reference.lines()
                print "Fields: ",reference.values()
                
            return 0
            
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
        oPlots=[]
        rPlots=[]
        
        if self.opts.mode=="separate":
            if self.opts.time==None:
                self.opts.time=samples.times
            if self.opts.field==None:
                self.opts.field=samples.values()
            if self.opts.line==None:
                self.opts.line=samples.lines()
            for t in self.opts.time:
                for f in self.opts.field:
                    for l in self.opts.line:
                        plot=samples.getData(line=[l],
                                             value=[f],
                                             time=[t])
                        oPlots.append(plot[:])
                        if reference:
                            p=reference.getData(line=[l],
                                                value=[f],
                                                time=[t],
                                                note=self.opts.refprefix+" ")
                            rPlots.append(p)
                            plot+=p
                        plots.append(plot)
                    
        elif self.opts.mode=="timesInOne":
            if self.opts.field==None:
                self.opts.field=samples.values() 
            if self.opts.line==None:
                self.opts.line=samples.lines()
            for f in self.opts.field:
                for l in self.opts.line:
                    plot=samples.getData(line=[l],
                                         value=[f],
                                         time=self.opts.time)
                    oPlots.append(plot[:])

                    if reference:
                        p=reference.getData(line=[l],
                                            value=[f],
                                            time=self.opts.time,
                                            note=self.opts.refprefix+" ")
                        rPlots.append(p)
                        plot+=p

                    plots.append(plot)
                
        elif self.opts.mode=="fieldsInOne":
            if self.opts.scaled and not self.opts.scaleAll:
                warning("In mode '",self.opts.mode,"' all fields are scaled to the same value")
                self.opts.scaleAll=True
                
            if self.opts.time==None:
                self.opts.time=samples.times
            if self.opts.line==None:
                self.opts.line=samples.lines()
            for t in self.opts.time:
                for l in self.opts.line:
                    plot=samples.getData(line=[l],
                                         value=self.opts.field,
                                         time=[t])
                    oPlots.append(plot[:])
                    if reference:
                        p=reference.getData(line=[l],
                                            value=self.opts.field,
                                            time=[t],
                                            note=self.opts.refprefix+" ")
                        rPlots.append(p)
                        plot+=p

                    plots.append(plot)
                
        elif self.opts.mode=="linesInOne":
            if self.opts.field==None:
                self.opts.field=samples.values() 
            if self.opts.time==None:
                self.opts.time=samples.times()
            for f in self.opts.field:
                for t in self.opts.time:
                    plot=samples.getData(line=self.opts.line,
                                         value=[f],
                                         time=[t])
                    oPlots.append(plot[:])

                    if reference:
                        p=reference.getData(line=self.opts.line,
                                            value=[f],
                                            time=[t],
                                            note=self.opts.refprefix+" ")
                        rPlots.append(p)
                        plot+=p

                    plots.append(plot)
                
        elif self.opts.mode=="complete":
            if self.opts.scaled and not self.opts.scaleAll:
                warning("In mode '",self.opts.mode,"' all fields are scaled to the same value")
                self.opts.scaleAll=True

            plot=samples.getData(line=self.opts.line,
                                 value=self.opts.field,
                                 time=self.opts.time)
            oPlots.append(plot[:])
            if reference:
                p=reference.getData(line=self.opts.line,
                                    value=self.opts.field,
                                    time=self.opts.time,
                                    note=self.opts.refprefix+" ")
                plot+=p
                rPlots.append(p)
                
            plots.append(plot)
            
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
            
            #            name+="_"+string.join(self.opts.line,"_")

            if self.opts.mode=="separate":
                name+="_%s"        % (p[0].line())
                name+="_%s_%04d"   % (p[0].name,tIndex)
                title="%s at t=%f on %s" % (p[0].name,float(p[0].time()),p[0].line())
            elif self.opts.mode=="timesInOne":
                name+="_%s"        % (p[0].line())
                if self.opts.time!=None:
                    name+="_"+"_".join(["t="+t for t in self.opts.time])
                name+="_%s" % p[0].name
                title="%s on %s"  % (p[0].name,p[0].line())
            elif self.opts.mode=="fieldsInOne":
                name+="_%s"        % (p[0].line())
                if self.opts.field!=None:
                    name+="_"+string.join(self.opts.field,"_")
                if self.opts.time!=None:
                    name+="_"+"_".join(["t="+t for t in self.opts.time])
                name+="_%04d" % tIndex
                title="t=%f on %s" % (float(p[0].time()),p[0].line())
            elif self.opts.mode=="linesInOne":
                name+="_%s"        % (p[0].name)
                if self.opts.line!=None:
                    name+="_"+string.join(self.opts.line,"_")
                name+="_t=%f" % float(p[0].time())
                title="%s at t=%f" % (p[0].name,float(p[0].time()))
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
                
                title=d.note
                if self.opts.mode=="separate":
                    title+=""
                elif self.opts.mode=="timesInOne":
                    title+="t=%f" % float(d.time())
                elif self.opts.mode=="fieldsInOne":
                    title+="%s"   % d.name
                elif self.opts.mode=="linesInOne":
                    title+="t=%f"   % float(d.time())
                elif self.opts.mode=="complete":
                    title+="%s at t=%f" % (d.name,float(d.time()))

                if len(self.opts.line)>1:
                    title+=" on %s" % d.line()

                if title=="":
                    result+="notitle "
                else:
                    result+='title "%s" ' % title

                result+="with %s " % self.opts.style

            result+="\n"

        if self.opts.csvFile:
            tmp=sum(plots,[])
            c=tmp[0]()
            for p in tmp[1:]:
                try:
                    c+=p()
                except WrongDataSize,e:
                    if self.opts.resampleReference:
                        sp=p()
                        for n in sp.names()[1:]:
                            data=c.resample(sp,
                                            n,
                                            extendData=self.opts.extendData)
                            try:
                                c.append(n,data)
                            except ValueError:
                                c.append(self.opts.refprefix+" "+n,data)
                    else:
                        self.warning("Try the --resample-option")
                        raise
                    
            c.writeCSV(self.opts.csvFile)
        elif self.opts.compare or self.opts.metrics:
            oPlots=[item for sublist in oPlots for item in sublist]
            rPlots=[item for sublist in rPlots for item in sublist]
            if len(rPlots)!=len(oPlots) and self.opts.compare:
                self.error("Number of original data sets",len(oPlots),
                           "is not equal to the reference data sets",
                           len(rPlots))
            if len(rPlots)==0 and self.opts.metrics:
                rPlots=[None]*len(oPlots)
                
            for o,r in zip(oPlots,rPlots):                    
                data=o()                
                if self.opts.compare:
                    if o.name!=r.name or o.index!=r.index:
                        self.error("Data from original",o.name,o.index,
                                   "and reference",r.name,r.index,
                                   "do not match")
                    ref=r()
                else:
                    ref=None
                for i,n in enumerate(data.names()):
                    if i==0:
                        continue
                    if self.opts.metrics:
                        print "Metrics for",o.name,"(Path:",o.file,")"
                        result=data.metrics(data.names()[i])
                        print "  Min                :",result["min"]
                        print "  Max                :",result["max"]
                        print "  Average            :",result["average"]
                        print "  Weighted average   :",result["wAverage"]
                        if not self.opts.compare:
                            print "Data size:",data.size()
                        print "  Time Range         :",result["tMin"],result["tMax"]
                    if self.opts.compare:
                        print "Comparing",o.name,"with name",n,"(Path:",o.file,")"
                        result=data.compare(ref,data.names()[i])
                        print "  Max difference     :",result["max"]
                        print "  Average difference :",result["average"]
                        print "  Weighted average   :",result["wAverage"]
                        print "Data size:",data.size(),"Reference:",ref.size()
                        if not self.opts.metrics:
                            print "  Time Range         :",result["tMin"],result["tMax"]
                        
                    print
        else:
            dest=sys.stdout
            if self.opts.gnuplotFile:
                dest=open(self.opts.gnuplotFile,"w")

            dest.write(result)
        
