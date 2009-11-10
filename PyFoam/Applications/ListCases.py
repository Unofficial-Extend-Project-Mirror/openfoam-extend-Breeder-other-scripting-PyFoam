"""
Application-class that implements pyFoamListCases.py
"""
from optparse import OptionGroup
from os import path,listdir,stat
import time
from stat import ST_MTIME
import string
import subprocess
import re

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam import configuration

class ListCases(PyFoamApplication):
    def __init__(self,args=None):
        description="""
List the valid OpenFOAM-cases in a number of directories along with some
basic information (number of timesteps, last timestep, etc). Currently
doesn't honor the parallel data
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [<directories>]",
                                   interspersed=True,
                                   changeVersion=False,
                                   nr=0,
                                   exactNr=False)

    sortChoices=["name","first","last","mtime","nrSteps","procs","diskusage","pFirst","pLast","nrParallel"]
    
    def addOptions(self):
        what=OptionGroup(self.parser,
                         "What",
                         "Define what should be shown")
        self.parser.add_option_group(what)
        
        what.add_option("--dump",
                        action="store_true",
                        dest="dump",
                        default=False,
                        help="Dump the information as Python-dictionaries")

        what.add_option("--disk-usage",
                        action="store_true",
                        dest="diskusage",
                        default=False,
                        help="Show the disk-usage of the case (in MB) - may take a long time")

        what.add_option("--parallel-info",
                        action="store_true",
                        dest="parallel",
                        default=False,
                        help="Print information about parallel runs (if present): number of processors and processor first and last time. The mtime will be that of the processor-directories")

        how=OptionGroup(self.parser,
                         "How",
                         "How the things should be shown")
        self.parser.add_option_group(how)

        how.add_option("--sort-by",
                        type="choice",
                        action="store",
                        dest="sort",
                        default=configuration().get("CommandOptionDefaults","sortListCases",default="name"),
                        choices=self.sortChoices,
                        help="Sort the cases by a specific key (Keys: "+string.join(self.sortChoices,", ")+") Default: %default")
        how.add_option("--reverse-sort",
                       action="store_true",
                       dest="reverse",
                       default=False,
                       help="Sort in reverse order")

        behave=OptionGroup(self.parser,
                         "Behaviour",
                         "Additional output etc")
        self.parser.add_option_group(behave)
        
        behave.add_option("--progress",
                          action="store_true",
                          dest="progress",
                          default=False,
                          help="Print the directories while they are being processed")

    def run(self):
        dirs=self.parser.getArgs()
        
        if len(dirs)==0:
            dirs=[path.curdir]

        cData=[]
        totalDiskusage=0
        
        for d in dirs:
            for n in listdir(d):
                cName=path.join(d,n)
                if path.isdir(cName):
                    try:
                        sol=SolutionDirectory(cName,archive=None,paraviewLink=False)
                        if sol.isValid():
                            if self.opts.progress:
                                print "Processing",cName

                            data={}

                            data["mtime"]=stat(cName)[ST_MTIME]
                            times=sol.getTimes()
                            try:
                                data["first"]=times[0]
                            except IndexError:
                                data["first"]="None"                            
                            try:
                                data["last"]=times[-1]
                            except IndexError:
                                data["last"]="None"                            
                            data["nrSteps"]=len(times)
                            data["procs"]=sol.nrProcs()
                            data["pFirst"]=-1
                            data["pLast"]=-1
                            data["nrParallel"]=-1
                            if self.opts.parallel:
                                pTimes=sol.getParallelTimes()
                                data["nrParallel"]=len(pTimes)
                                if len(pTimes)>0:
                                    data["pFirst"]=pTimes[0]
                                    data["pLast"]=pTimes[-1]                                
                            data["name"]=cName
                            data["diskusage"]=-1
                            if self.opts.diskusage:
                                data["diskusage"]=int(subprocess.Popen(["du","-sm",cName], stdout=subprocess.PIPE).communicate()[0].split()[0])
                                totalDiskusage+=data["diskusage"]
                            if self.opts.parallel:
                                for f in listdir(cName):
                                    if re.compile("processor[0-9]+").match(f):
                                        data["mtime"]=max(stat(path.join(cName,f))[ST_MTIME],data["mtime"])

                            cData.append(data)
                    except OSError:
                        print cName,"is unreadable"
                        
        if self.opts.progress:
            print "Sorting data"
            
        if self.opts.reverse:
            cData.sort(lambda x,y:cmp(y[self.opts.sort],x[self.opts.sort]))
        else:
            cData.sort(lambda x,y:cmp(x[self.opts.sort],y[self.opts.sort]))

        if len(cData)==0:
            print "No cases found"
            return

        if self.opts.dump:
            print cData
            return
        
        lens={}
        for k in cData[0].keys():
            lens[k]=len(k)
        for c in cData:
            c["mtime"]=time.asctime(time.localtime(c["mtime"]))
            for k,v in c.iteritems():
                lens[k]=max(lens[k],len(str(v)))

        format=""
        spec=["mtime"," | ","first"," - ","last"," (","nrSteps",") "]
        if self.opts.parallel:
            spec+=["| ","procs"," : ","pFirst"," - ","pLast"," (","nrParallel",") | "]
        if self.opts.diskusage:
            spec+=["diskusage"," MB "]
        spec+=["name"]
        
        for i,l in enumerate(spec):
            if  not l in cData[0].keys():
                format+=l
            else:
                if i<len(spec)-1:
                    format+="%%(%s)%ds" % (l,lens[l])
                else:
                    format+="%%(%s)s" % (l)

        if self.opts.progress:
            print "Printing\n\n"
            
        header=format % dict(zip(cData[0].keys(),cData[0].keys()))
        print header
        print "-"*len(header)
        
        for d in cData:
            for k in d.keys():
                d[k]=str(d[k])
            print format % d

        if self.opts.diskusage:
            print "Total disk-usage:",totalDiskusage,"MB"
            
